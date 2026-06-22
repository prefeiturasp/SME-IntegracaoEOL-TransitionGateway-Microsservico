"""Valida as views do domínio de alunos."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


def _turma_payload(codigo_aluno: int = 123456) -> dict:
    return {
        "codigo_aluno": codigo_aluno,
        "ano_letivo": 2026,
        "nome_aluno": "Fulano de Tal",
        "nome_social_aluno": None,
        "codigo_situacao_matricula": 1,
        "situacao_matricula": "Ativo",
        "data_situacao": "2024-02-01 13:00:00.020000+00:00",
        "data_nascimento": "2010-01-01",
        "documento_cpf": "12345678901",
        "data_matricula": "2024-01-31 10:20:30.120000",
        "numero_aluno_chamada": "15",
        "codigo_turma": 9001,
        "data_atualizacao_contato": "2024-02-02 13:20:30.120000+00:00",
        "tipo_responsavel": 1,
        "codigo_escola": "100001",
        "codigo_tipo_turma": 1,
        "data_atualizacao_tabela": "2024-02-01 13:00:00.020000+00:00",
    }


def _http_status_error(status_code: int, body: dict) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://sidecar.local/test")
    response = httpx.Response(status_code, json=body, request=request)
    return httpx.HTTPStatusError(
        "Erro no sidecar",
        request=request,
        response=response,
    )


def _request_error() -> httpx.RequestError:
    request = httpx.Request("GET", "https://sidecar.local/test")
    return httpx.ConnectError("Sidecar indisponivel", request=request)


class AlunosUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_preserva_codigo_aluno_informacoes(self) -> None:
        match = resolve("/api/v1/alunos/123456/informacoes")

        self.assertEqual(match.kwargs, {"codigo_aluno": "123456"})

    def test_preserva_codigo_aluno_necessidades_especiais(self) -> None:
        match = resolve("/api/v1/alunos/123456/necessidades-especiais")

        self.assertEqual(match.kwargs, {"codigo_aluno": "123456"})

    def test_preserva_codigo_aluno_turmas(self) -> None:
        match = resolve("/api/v1/alunos/123456/turmas")

        self.assertEqual(match.kwargs, {"codigo_aluno": "123456"})

    def test_preserva_codigo_aluno_turmas_com_barra(self) -> None:
        match = resolve("/api/v1/alunos/123456/turmas/")

        self.assertEqual(match.kwargs, {"codigo_aluno": "123456"})

    def test_rota_listagem_alunos(self) -> None:
        match = resolve("/api/v1/alunos/alunos")

        self.assertEqual(match.kwargs, {})

    def test_preserva_ue_codigo_autocomplete_ativos(self) -> None:
        match = resolve("/api/v1/alunos/ues/100001/autocomplete/ativos")

        self.assertEqual(match.kwargs, {"ue_codigo": "100001"})

    def test_preserva_cpf_responsavel_resumido(self) -> None:
        match = resolve("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(match.kwargs, {"cpf_responsavel": "12345678900"})

    def test_preserva_codigo_turma_informacoes_alunos_turma(self) -> None:
        match = resolve("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(match.kwargs, {"codigo_turma": "9001"})

    def test_preserva_parametros_alunos_ativos_data_aula(self) -> None:
        match = resolve(
            "/api/turmas/3012185/alunos-ativos/"
            "data-aula-ticks/639031104000000000/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "codigo_turma": "3012185",
                "data_ticks": "639031104000000000",
            },
        )

    def test_alunos_ativos_data_aula(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        path = (
            "/api/turmas/{codigo_turma}/alunos-ativos/"
            "data-aula-ticks/{data_ticks}/"
        )
        operation = resp.data["paths"][path]["get"]
        self.assertEqual(operation["tags"], ["Turma"])
        self.assertEqual(
            {item["name"] for item in operation["parameters"]},
            {"codigo_turma", "data_ticks"},
        )


class AlunoAutocompleteAtivosViewTest(SimpleTestCase):
    """Valida a view de autocomplete de alunos ativos."""

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_200_retorna_lista_alunos(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 123456,
                "nome_aluno": "Fulano de Tal",
                "nome_social_aluno": None,
                "codigo_turma": 9001,
                "numero_aluno_chamada": "15",
                "turma": "7A",
                "modalidade": "EI",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos"
            "?aluno_nome=Fulano&data_referencia=2026-02-03T10:00:00"
            "&aluno_codigo=0&limite=5"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data[0]["codigoAluno"], 123456)
        self.assertEqual(data[0]["nomeAluno"], "Aluno Teste")
        self.assertIsNone(data[0]["nomeSocialAluno"])
        self.assertEqual(data[0]["codigoTurma"], 9001)
        self.assertEqual(data[0]["numeroAlunoChamada"], "15")
        self.assertEqual(data[0]["turma"], "7A")
        self.assertEqual(data[0]["modalidade"], "EI")
        mock_service.assert_called_once_with(
            ue_codigo="100001",
            aluno_nome="Fulano",
            data_referencia=datetime(2026, 2, 3, 10, 0, 0),
            aluno_codigo=0,
            limite=5,
        )

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_400_quando_query_params_camelcase(
        self, mock_service: MagicMock
    ) -> None:
        """Verifica que aliases camelCase não são aceitos na entrada."""
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos"
            "?alunoNome=Fulano&dataReferencia=2026-02-03T10:00:00"
            "&alunoCodigo=0&limite=5"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_400_quando_ue_codigo_vazio(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/%20/autocomplete/ativos"
            "?aluno_nome=Fulano&data_referencia=2026-02-03T10:00:00"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo da UE."},
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_400_legado_quando_data_referencia_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos?aluno_nome=Fulano"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME.",
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_400_quando_nome_menor_que_tres_sem_codigo(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos"
            "?aluno_nome=ab&data_referencia=2026-02-03T10:00:00"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "O Nome deve conter no mínimo 3 caracteres."},
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.buscar_alunos_ativos_autocomplete")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos"
            "?aluno_nome=Fulano&data_referencia=2026-02-03T10:00:00"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(
            "/api/v1/alunos/ues/100001/autocomplete/ativos"
            "?aluno_nome=Fulano"
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoInformacoesViewTest(SimpleTestCase):
    """Valida a view de informações do aluno."""

    @patch("apps.alunos.views.services.get_informacoes_aluno")
    def test_200_retorna_dados_aluno(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {
            "codigo_aluno": 123456,
            "nome_aluno": "Fulano de Tal",
            "nome_social_aluno": None,
            "data_nascimento": "2010-01-01",
            "sexo": "M",
            "cpf": None,
            "nome_mae": "Maria",
            "nacionalidade": "Brasileiro",
            "nis": None,
            "raca_cor": None,
            "possui_deficiencia": False,
            "endereco": {
                "id": 1,
                "nro": "100",
                "complemento": None,
                "bairro": "Centro",
                "cep": 12345678,
                "nome_municipio": "SAO PAULO",
                "sigla_uf": "SP",
                "tipo_logradouro": "Rua",
                "logradouro": "Teste",
            },
        }
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["codigoAluno"], 123456)
        self.assertEqual(data["nomeAluno"], "Fulano de Tal")
        self.assertEqual(data["grupoEtnico"], None)
        self.assertEqual(data["endereco"]["nomeMunicipio"], "SAO PAULO")
        self.assertFalse(data["ehImigrante"])
        self.assertEqual(
            set(data),
            {
                "codigoAluno",
                "nomeAluno",
                "nomeMae",
                "sexo",
                "grupoEtnico",
                "nacionalidade",
                "endereco",
                "ehImigrante",
                "nis",
                "cns",
            },
        )
        mock_service.assert_called_once_with("123456")

    @patch("apps.alunos.views.services.get_informacoes_aluno")
    def test_204_quando_sidecar_retorna_404(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Aluno não encontrado."},
        )
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.alunos.views.services.get_informacoes_aluno")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    @patch("apps.alunos.views.services.get_informacoes_aluno")
    def test_204_quando_aluno_ausente(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_aluno_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/%20/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo do aluno."},
        )

    def test_601_quando_codigo_aluno_e_zero(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/0/informacoes")

        self.assertEqual(resp.status_code, 601)
        self.assertEqual(
            resp.json(),
            "É necessário informar o codigo do aluno.",
        )

    def test_400_quando_codigo_aluno_nao_e_inteiro(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/abc/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo do aluno."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/alunos/123456/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ResponsavelResumidoViewTest(SimpleTestCase):
    """Valida a view de dados resumidos do responsável."""

    @patch("apps.alunos.views.services.get_responsavel_resumido")
    def test_200_retorna_responsavel_resumido(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {
            "id": 9999,
            "cpf": "12345678900",
            "email": "responsavel@email.com",
            "nome": "Maria da Silva",
            "tipo_responsavel": 1,
            "data_nascimento": "2001-08-30",
            "data_atualizacao": "2021-10-01T10:09:53.003",
            "nome_mae": "Josefa",
            "ddd_celular": "11",
            "numero_celular": "999999999",
            "codigo_aluno": None,
        }
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {
                "id": 9999,
                "cpf": "12345678900",
                "email": "responsavel@email.com",
                "nome": "Maria da Silva",
                "tipoResponsavel": 1,
                "dataNascimento": "2001-08-30T00:00:00",
                "dataAtualizacao": "2021-10-01T10:09:53.003",
                "nomeMae": "Josefa",
                "dddCelular": "11",
                "numeroCelular": "999999999",
                "codigoAluno": None,
            },
        )
        mock_service.assert_called_once_with("12345678900")

    @patch("apps.alunos.views.services.get_responsavel_resumido")
    def test_204_quando_sidecar_nao_encontra(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Responsável não encontrado."},
        )
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.alunos.views.services.get_responsavel_resumido")
    def test_204_quando_responsavel_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.alunos.views.services.get_responsavel_resumido")
    def test_400_quando_cpf_nao_numerico(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis/abc/resumido")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "CPF do responsável inválido."},
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_responsavel_resumido")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class InformacoesAlunosTurmaViewTest(SimpleTestCase):
    """Valida a view de informações dos alunos de uma turma."""

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_200_retorna_alunos_da_turma(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "numero_chamada": 3,
                "codigo_aluno": 123456,
                "nome_aluno": "Fulano da Silva",
                "nome_social_aluno": None,
                "sexo": "M",
                "raca": "Parda",
                "codigo_raca": 3,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "numeroChamada": 3,
                    "codigoAluno": 123456,
                    "nomeAluno": "Fulano da Silva",
                    "nomeSocialAluno": None,
                    "sexo": "M",
                    "raca": "Parda",
                    "codigoRaca": 3,
                }
            ],
        )
        mock_service.assert_called_once_with("9001")

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_200_retorna_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with("9001")

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_400_quando_codigo_turma_nao_e_inteiro(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/abc/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo da turma."},
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_601_quando_codigo_turma_e_zero(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/0/turma/informacoes")

        self.assertEqual(resp.status_code, 601)
        self.assertEqual(resp.json(), "O código da turma é obrigatório.")
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_200_vazio_quando_codigo_turma_negativo(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/-1/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_informacoes_alunos_turma")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunosAtivosDataAulaTicksViewTest(SimpleTestCase):
    """Valida a resposta de alunos ativos na data da aula."""

    _PATH = (
        "/api/turmas/3012185/alunos-ativos/"
        "data-aula-ticks/639031104000000000/"
    )

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 7730117,
                "nome_aluno": "Aluno Teste",
                "nome_social_aluno": None,
                "data_nascimento": "2020-07-10",
                "codigo_situacao_matricula": 1,
                "situacao_matricula": "Ativo",
                "data_situacao": "2025-12-08T11:42:14.66-03:00",
                "numero_aluno_chamada": None,
                "possui_deficiencia": False,
                "codigo_matricula": 43790514,
                "codigo_turma": 3012185,
                "codigo_escola": "097144",
                "ano_letivo": 2026,
                "data_matricula": "2025-11-04T08:16:14.26-03:00",
                "nome_responsavel": "Responsável",
                "tipo_responsavel": 1,
                "celular_responsavel": None,
                "data_atualizacao_contato": None,
                "sequencia": 1,
                "codigo_dre": "108100",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoAluno"], 7730117)
        self.assertEqual(resp.json()[0]["codigoComponenteCurricular"], 0)
        self.assertEqual(resp.json()[0]["transferencia_Interna"], False)
        self.assertEqual(resp.json()[0]["numeroAlunoChamada"], "000")
        mock_service.assert_called_once_with(
            codigo_turma="3012185",
            data_ticks="639031104000000000",
        )

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_400_quando_codigo_turma_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/abc/alunos-ativos/"
            "data-aula-ticks/639031104000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_400_quando_data_ticks_invalida(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/3012185/alunos-ativos/data-aula-ticks/abc/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Turma não encontrada."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), {"detail": "Turma não encontrada."})

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoNecessidadesEspeciaisViewTest(SimpleTestCase):
    """Valida a view de necessidades especiais do aluno."""

    @patch("apps.alunos.views.services.get_necessidades_especiais_aluno")
    def test_200_retorna_lista_necessidades(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 123456,
                "tipo_necessidade_especial": 10,
                "descricao_necessidade_especial": "Deficiencia Visual",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/necessidades-especiais")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["codigoAluno"], 123456)
        self.assertEqual(data["tipoNecessidadeEspecial"], 10)
        self.assertEqual(
            data["descricaoNecessidadeEspecial"],
            "Deficiencia Visual",
        )
        self.assertIsNone(data["tipoRecurso"])
        self.assertIsNone(data["descricaoRecurso"])
        mock_service.assert_called_once_with("123456")

    @patch("apps.alunos.views.services.get_necessidades_especiais_aluno")
    def test_204_quando_lista_necessidades_vazia(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/necessidades-especiais")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_aluno_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/%20/necessidades-especiais")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo do aluno."},
        )


class AlunoTurmasViewTest(SimpleTestCase):
    """Valida a view de turmas do aluno."""

    @patch("apps.alunos.views.services.get_turmas_aluno")
    def test_200_retorna_lista_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_payload()]
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/turmas")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["codigoAluno"], 123456)
        self.assertEqual(data[0]["codigoTurma"], 9001)
        self.assertEqual(data[0]["numeroAlunoChamada"], "15")
        self.assertEqual(data[0]["dataSituacao"], "2024-02-01T10:00:00.02")
        self.assertEqual(data[0]["dataNascimento"], "2010-01-01T00:00:00")
        self.assertEqual(data[0]["dataMatricula"], "2024-01-31T10:20:30.12")
        self.assertEqual(data[0]["celularResponsavel"], "")
        self.assertEqual(
            data[0]["dataAtualizacaoContato"],
            "2024-02-02T10:20:30.12",
        )
        self.assertEqual(data[0]["tipoResponsavel"], "1")
        self.assertIn("idade", data[0])
        self.assertIn("documentoCpf", data[0])
        self.assertIn("nomeResponsavel", data[0])
        self.assertIn("codigoEscola", data[0])
        self.assertEqual(
            data[0]["dataAtualizacaoTabela"],
            "2024-02-01T10:00:00.02",
        )
        mock_service.assert_called_once_with("123456")

    @patch("apps.alunos.views.services.get_turmas_aluno")
    def test_503_quando_sidecar_indisponivel_turmas(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/123456/turmas")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    def test_400_quando_codigo_aluno_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/%20/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo do aluno."},
        )


class AlunosListViewTest(SimpleTestCase):
    """Valida a view de listagem de alunos."""

    @patch("apps.alunos.views.services.listar_alunos")
    def test_200_retorna_lista_alunos(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_payload(1), _turma_payload(2)]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/alunos?codigos_aluno=1&codigos_aluno=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["codigoAluno"], 1)
        self.assertEqual(data[1]["codigoAluno"], 2)
        self.assertEqual(data[0]["tipoTurno"], 0)
        self.assertIn("turmaNome", data[0])
        mock_service.assert_called_once_with(["1", "2"])

    @patch("apps.alunos.views.services.listar_alunos")
    def test_601_quando_codigos_aluno_ausentes(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/alunos")

        self.assertEqual(resp.status_code, 601)
        self.assertEqual(
            resp.json(),
            "Os códigos dos Alunos são obrigatórios.",
        )
        mock_service.assert_not_called()
