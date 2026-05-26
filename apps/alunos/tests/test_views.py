"""Valida as views do domínio de alunos."""

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
    request = httpx.Request("GET", "http://sidecar.local/test")
    response = httpx.Response(status_code, json=body, request=request)
    return httpx.HTTPStatusError(
        "Erro no sidecar",
        request=request,
        response=response,
    )


def _request_error() -> httpx.RequestError:
    request = httpx.Request("GET", "http://sidecar.local/test")
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

    def test_preserva_parametros_legados_turmas(self) -> None:
        match = resolve(
            "/api/v1/alunos/123456/turmas/anosLetivos/2026/"
            "historico/false/filtrar-situacao/true/tipo-turma/false"
        )

        self.assertEqual(
            match.kwargs,
            {
                "codigoAluno": "123456",
                "anoLetivo": "2026",
                "historico": "false",
                "filtrarSituacao": "true",
                "tipoTurma": "false",
            },
        )

    def test_rota_listagem_alunos(self) -> None:
        match = resolve("/api/v1/alunos/alunos")

        self.assertEqual(match.kwargs, {})


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
            {"detail": "E necessario informar o codigo do aluno."},
        )


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
            {"detail": "E necessario informar o codigo do aluno."},
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
    def test_200_repassa_parametros_legados(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = [_turma_payload()]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/123456/turmas/anosLetivos/2026/"
            "historico/false/filtrar-situacao/true/tipo-turma/false"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            "123456",
            ano_letivo="2026",
            historico="false",
            filtrar_situacao="true",
            tipo_turma="false",
        )

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
            {"detail": "E necessario informar o codigo do aluno."},
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
