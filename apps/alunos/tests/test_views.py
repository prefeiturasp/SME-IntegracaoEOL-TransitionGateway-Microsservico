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


def _aluno_ue_payload(codigo_aluno: int = 123456) -> dict:
    return {
        "codigo_aluno": codigo_aluno,
        "tipo_turno": 2,
        "ano_letivo": 2026,
        "nome_aluno": "Fulano de Tal",
        "nome_social_aluno": None,
        "codigo_situacao_matricula": 1,
        "situacao_matricula": "Ativo",
        "data_situacao": "2026-02-01",
        "data_nascimento": "2010-01-01",
        "numero_aluno_chamada": "15",
        "codigo_turma": 9001,
        "nome_responsavel": None,
        "tipo_responsavel": None,
        "ddd_celular": None,
        "numero_celular": None,
        "data_atualizacao_contato": "2026-02-02T13:20:30+00:00",
        "codigo_tipo_turma": 1,
        "turma_nome": "5A",
        "etapa_ensino": 5,
        "ciclo_ensino": 2,
        "desc_etapa_ensino": "Ensino Fundamental",
        "desc_ciclo_ensino": "Ciclo Interdisciplinar",
        "data_atualizacao_tabela": "2026-02-01T13:00:00+00:00",
    }


def _filiacao_payload() -> dict:
    return {
        "nome_responsavel": "Maria da Silva",
        "cpf": "12345678901",
        "email": "maria@example.com",
        "ddd_celular": "11",
        "numero_celular": "999998888",
        "ddd_residencial": "11",
        "numero_residencial": "33334444",
        "ddd_comercial": "11",
        "numero_comercial": "55556666",
        "tipo_responsavel": 1,
        "endereco": {
            "id": 123,
            "nro": "100",
            "complemento": "AP 1",
            "bairro": "Centro",
            "cep": "01310200",
            "nome_municipio": "SAO PAULO",
            "sigla_uf": "SP",
            "tipo_logradouro": "Rua",
            "logradouro": "das Flores",
        },
    }


def _alunos_ativos_turma_payload() -> dict:
    return {
        "codigo_aluno": 123456,
        "nome_aluno": "Fulano de Tal",
        "nome_social_aluno": None,
        "data_nascimento": "2015-04-27",
        "codigo_situacao_matricula": 1,
        "situacao_matricula": "Ativo",
        "data_situacao": "2025-11-04",
        "numero_aluno_chamada": "006",
        "possui_deficiencia": True,
        "codigo_matricula": 999,
        "codigo_turma": 9001,
        "codigo_escola": "100001",
        "ano_letivo": 2026,
    }


def _http_status_error(
    status_code: int, body: dict | list | str
) -> httpx.HTTPStatusError:
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


def _http_status_error_texto(
    status_code: int, texto: str
) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://sidecar.local/test")
    response = httpx.Response(status_code, text=texto, request=request)
    return httpx.HTTPStatusError(
        "Erro no sidecar",
        request=request,
        response=response,
    )


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

    def test_preserva_parametros_da_rota_alunos_da_ue(self) -> None:
        match = resolve("/api/v1/alunos/ues/019362/anosLetivos/2026")

        self.assertEqual(
            match.kwargs,
            {"codigo_ue": "019362", "ano_letivo": "2026"},
        )

    def test_preserva_cpf_responsavel_resumido(self) -> None:
        match = resolve("/api/v1/alunos/responsaveis/12345678900/resumido")

        self.assertEqual(match.kwargs, {"cpf_responsavel": "12345678900"})

    def test_preserva_codigo_turma_informacoes_alunos_turma(self) -> None:
        match = resolve("/api/v1/alunos/9001/turma/informacoes")

        self.assertEqual(match.kwargs, {"codigo_turma": "9001"})

    def test_preserva_codigo_aluno_filiacao(self) -> None:
        match = resolve("/api/v1/alunos/123456/responsaveis/filiacao")

        self.assertEqual(match.kwargs, {"codigo_aluno": "123456"})

    def test_preserva_parametros_ativos_por_periodo(self) -> None:
        match = resolve("/api/v1/alunos/turmas/9001/ativos/2026-12-31")

        self.assertEqual(
            match.kwargs,
            {
                "codigo_turma": "9001",
                "data_referencia_fim": "2026-12-31",
            },
        )

    def test_preserva_parametros_total_ativos_por_periodo(self) -> None:
        match = resolve(
            "/api/v1/alunos/ativos/anos/5/anos-letivos/2026/"
            "inicio/2026-01-01/fim/2026-12-31"
        )

        self.assertEqual(
            match.kwargs,
            {
                "ano_turma": "5",
                "ano_letivo": "2026",
                "data_inicio": "2026-01-01",
                "data_fim": "2026-12-31",
            },
        )

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

    def test_preserva_parametros_data_matricula_ticks(self) -> None:
        match = resolve(
            "/api/turmas/3015603/data-matricula-ticks/639059616000000000/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "codigo_turma": "3015603",
                "data_matricula_ticks": "639059616000000000",
            },
        )

    def test_preserva_parametros_aluno_considera_inativos(self) -> None:
        match = resolve(
            "/api/turmas/3123349/aluno/7345634/considera-inativos/true/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "codigo_turma": "3123349",
                "codigo_aluno": "7345634",
                "considera_inativos": "true",
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

    def test_data_matricula_ticks_schema(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        path = (
            "/api/turmas/{codigo_turma}/"
            "data-matricula-ticks/{data_matricula_ticks}/"
        )
        operation = resp.data["paths"][path]["get"]
        self.assertEqual(operation["tags"], ["Turma"])
        self.assertEqual(
            {item["name"] for item in operation["parameters"]},
            {"codigo_turma", "data_matricula_ticks"},
        )

    def test_aluno_considera_inativos_schema(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        path = (
            "/api/turmas/{codigo_turma}/aluno/{codigo_aluno}/"
            "considera-inativos/{considera_inativos}/"
        )
        operation = resp.data["paths"][path]["get"]
        self.assertEqual(operation["tags"], ["Turma"])
        self.assertEqual(
            {item["name"] for item in operation["parameters"]},
            {"codigo_turma", "codigo_aluno", "considera_inativos"},
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
        self.assertEqual(data[0]["nomeAluno"], "Fulano de Tal")
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


class AlunoAutocompleteUeViewTest(SimpleTestCase):
    """Valida a view de autocomplete de alunos da UE por ano letivo."""

    @patch("apps.alunos.views.services.get_alunos_autocomplete_ue")
    def test_200_retorna_lista_alunos(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 123456,
                "nome_aluno": "Fulano de Tal",
                "nome_social_aluno": None,
                "codigo_turma": 9001,
                "numero_aluno_chamada": "15",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
            "?nome_aluno=Fulano&codigo_eol=123456&limite=5"
            "&codigos_turmas=9001&eh_historico=false"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data[0]["codigoAluno"], 123456)
        self.assertEqual(data[0]["nomeAluno"], "Fulano de Tal")
        self.assertEqual(data[0]["codigoTurma"], 9001)
        self.assertEqual(data[0]["numeroAlunoChamada"], "15")
        mock_service.assert_called_once_with(
            codigo_ue="100001",
            ano_letivo="2026",
            codigo_turmas=["9001"],
            nome_aluno="Fulano",
            codigo_eol="123456",
            somente_ativos=None,
            eh_historico="false",
            limite=5,
        )

    @patch("apps.alunos.views.services.get_alunos_autocomplete_ue")
    def test_contrato_tem_apenas_5_campos(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 123456,
                "nome_aluno": "Fulano de Tal",
                "nome_social_aluno": None,
                "codigo_turma": 9001,
                "numero_aluno_chamada": "15",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(resp.json()[0]),
            [
                "codigoAluno",
                "nomeAluno",
                "nomeSocialAluno",
                "codigoTurma",
                "numeroAlunoChamada",
            ],
        )

    @patch("apps.alunos.views.services.get_alunos_autocomplete_ue")
    def test_repassa_erro_do_sidecar(self, mock_service: MagicMock) -> None:
        mock_service.side_effect = _http_status_error(
            404, {"detail": "Não foram encontradas turmas para o aluno."}
        )
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.alunos.views.services.get_alunos_autocomplete_ue")
    def test_400_quando_limite_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
            "?limite=abc"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.alunos.views.services.get_alunos_autocomplete_ue")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ues/100001/anosLetivos/2026/autocomplete"
        )

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )


class DadosAcompanhamentoEscolarViewTest(SimpleTestCase):
    """Valida a view de dados de acompanhamento escolar."""

    @patch("apps.alunos.views.services.get_dados_acompanhamento_escolar")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_eol": 7074492,
                "nome_responsavel": "MARIA DA SILVA",
                "cpf_responsavel": "12345678901",
                "nome": "JOAO DA SILVA",
                "nome_social": None,
                "codigo_escola": "019267",
                "codigo_dre": "108200",
                "escola": "EMEF TESTE",
                "tipo_responsavel": 1,
                "codigo_tipo_escola": 1,
                "descricao_tipo_escola": "EMEF",
                "sigla_dre": "DRE - CL",
                "codigo_turma": 3038818,
                "turma": "5A",
                "situacao_matricula": "Ativo",
                "data_nascimento": "2015-04-21",
                "data_situacao_matricula": "2026-01-22T11:59:03.323000",
                "codigo_ciclo_ensino": 24,
                "codigo_etapa_ensino": 5,
                "serie_resumida": "5",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/dados-acompanhamento-escolar"
            "?codigo_aluno=7074492"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        corpo = resp.json()[0]
        self.assertEqual(corpo["codigoEol"], 7074492)
        self.assertEqual(corpo["codigoEscola"], "019267")
        self.assertEqual(corpo["escola"], "EMEF TESTE")
        self.assertEqual(corpo["siglaDre"], "DRE - CL")
        self.assertEqual(corpo["dataNascimento"], "2015-04-21T00:00:00")
        self.assertEqual(
            corpo["dataSituacaoMatricula"], "2026-01-22T11:59:03.323"
        )
        self.assertEqual(corpo["modalidadeCodigo"], 0)
        self.assertIsNone(corpo["modalidadeDescricao"])
        self.assertEqual(
            list(corpo)[-2:], ["modalidadeCodigo", "modalidadeDescricao"]
        )

    @patch("apps.alunos.views.services.get_dados_acompanhamento_escolar")
    def test_repassa_status_601_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            601, "Nenhum filtro foi especificado"
        )
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/dados-acompanhamento-escolar")

        self.assertEqual(resp.status_code, 601)

    @patch("apps.alunos.views.services.get_dados_acompanhamento_escolar")
    def test_repassa_corpo_texto_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error_texto(
            601, "erro de negocio em texto puro"
        )
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/dados-acompanhamento-escolar")

        self.assertEqual(resp.status_code, 601)
        self.assertEqual(
            resp.json(), {"detail": "erro de negocio em texto puro"}
        )

    @patch("apps.alunos.views.services.get_dados_acompanhamento_escolar")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/dados-acompanhamento-escolar")

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )


class QuantidadeMatriculadosViewTest(SimpleTestCase):
    """Valida a view de quantidade de matriculados."""

    @patch("apps.alunos.views.services.get_quantidade_matriculados")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "quantidade": 28,
                "ordem": 2,
                "modalidade": "EF",
                "ano": "3",
                "turma": "3B",
                "dre_codigo": "108200",
                "ue_codigo": "019267",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ano-letivo/2026/matriculados/quantidade"
            "?ue_codigo=019267&modalidade=5&ano=3&turma=3038818"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        corpo = resp.json()[0]
        self.assertEqual(
            list(corpo),
            [
                "quantidade",
                "ordem",
                "modalidade",
                "ano",
                "turma",
                "dreCodigo",
                "ueCodigo",
            ],
        )
        self.assertEqual(corpo["quantidade"], 28)
        self.assertEqual(corpo["dreCodigo"], "108200")
        self.assertEqual(corpo["ueCodigo"], "019267")
        mock_service.assert_called_once_with(
            ano_letivo="2026",
            dre_codigo=None,
            ue_codigo="019267",
            modalidade=["5"],
            ano=["3"],
            turma=["3038818"],
        )

    @patch("apps.alunos.views.services.get_quantidade_matriculados")
    def test_repassa_status_601_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            601, "Ano Letivo deve ser informado"
        )
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ano-letivo/0/matriculados/quantidade"
        )

        self.assertEqual(resp.status_code, 601)

    @patch("apps.alunos.views.services.get_quantidade_matriculados")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/ano-letivo/2026/matriculados/quantidade"
        )

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )


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


class ResponsaveisViewTest(SimpleTestCase):
    """Valida a listagem de responsáveis no contrato legado."""

    @patch("apps.alunos.views.services.get_responsaveis")
    def test_200_retorna_contrato_completo(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_dre": "108",
                "dre": "DRE TESTE",
                "codigo_ue": "100001",
                "ue": "UE TESTE",
                "codigo_turma": 12345,
                "turma": "5A",
                "cpf_responsavel": 1234567890,
                "codigo_aluno": 1234567,
                "codigo_tipo_escola": 1,
                "codigo_etapa_ensino": 5,
                "codigo_ciclo_ensino": 2,
                "serie_resumida": "5",
                "codigo_modalidade_turma": 5,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/responsaveis"
            "?codigo_dre=108&codigo_ue=100001&ano_letivo=2026"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigoDre": "108",
                    "dre": "DRE TESTE",
                    "codigoUe": "100001",
                    "ue": "UE TESTE",
                    "codigoTurma": 12345,
                    "turma": "5A",
                    "cpfResponsavel": 1234567890,
                    "codigoAluno": 1234567,
                    "codigoTipoEscola": 1,
                    "codigoEtapaEnsino": 5,
                    "codigoCicloEnsino": 2,
                    "serieResumida": "5",
                    "codigoModalidadeTurma": 5,
                    "temAppInstalado": False,
                }
            ],
        )
        mock_service.assert_called_once_with(
            codigo_dre="108",
            codigo_ue="100001",
            ano_letivo=2026,
        )

    @patch("apps.alunos.views.services.get_responsaveis")
    def test_400_quando_ano_invalido(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/responsaveis?ano_letivo=abc")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()


class FiliacaoAlunoViewTest(SimpleTestCase):
    """Valida a view de dados de filiação do aluno."""

    _URL = "/api/v1/alunos/123456/responsaveis/filiacao"

    @patch("apps.alunos.views.services.get_filiacao_aluno")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [_filiacao_payload()]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(item["nomeResponsavel"], "Maria da Silva")
        self.assertEqual(item["dddResidencial"], "11")
        self.assertEqual(item["numeroComercial"], "55556666")
        self.assertEqual(item["tipoResponsavel"], 1)
        self.assertEqual(item["endereco"]["nomeMunicipio"], "SAO PAULO")
        self.assertEqual(item["endereco"]["tipologradouro"], "Rua")
        mock_service.assert_called_once_with("123456")

    @patch("apps.alunos.views.services.get_filiacao_aluno")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.alunos.views.services.get_filiacao_aluno")
    def test_400_quando_codigo_nao_e_inteiro(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/alunos/abc/responsaveis/filiacao")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    def test_403_sem_autenticacao(self) -> None:
        resp = APIClient().get(self._URL)

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
                "numero_aluno_chamada": "015",
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
    def test_200_retorna_numero_chamada_000_quando_vazio(
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
                "numero_aluno_chamada": "",
                "possui_deficiencia": False,
                "codigo_matricula": 43790514,
                "codigo_turma": 3012185,
                "codigo_escola": "097144",
                "ano_letivo": 2026,
                "data_matricula": "2025-11-04T08:16:14.26-03:00",
                "nome_responsavel": "Responsavel",
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
        self.assertEqual(resp.json()[0]["numeroAlunoChamada"], "000")

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_200_vazio_quando_codigo_turma_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/abc/alunos-ativos/"
            "data-aula-ticks/639031104000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_ativos_data_aula_ticks")
    def test_200_vazio_quando_codigo_turma_zero(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/0/alunos-ativos/"
            "data-aula-ticks/639031104000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
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
    def test_200_vazio_quando_sem_resultados(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            codigo_turma="3012185",
            data_ticks="639031104000000000",
        )

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


class AlunosDataMatriculaTicksViewTest(SimpleTestCase):
    """Valida a resposta de alunos por data de matricula."""

    _PATH = "/api/turmas/3015603/data-matricula-ticks/639059616000000000/"

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 7614272,
                "nome_aluno": "ALICIA GABRIELLI FERREIRA SILVA",
                "nome_social_aluno": None,
                "data_nascimento": "2020-03-19",
                "codigo_situacao_matricula": 1,
                "situacao_matricula": "Ativo",
                "data_situacao": "2025-12-18T11:34:28.050000-03:00",
                "numero_aluno_chamada": "001",
                "possui_deficiencia": False,
                "codigo_matricula": 44295982,
                "codigo_turma": 3015603,
                "codigo_escola": "099791",
                "ano_letivo": 2026,
                "data_matricula": "2025-12-18T11:34:28.050000-03:00",
                "nome_responsavel": "KATIA CRISTINA DA SILVA",
                "tipo_responsavel": 1,
                "celular_responsavel": None,
                "data_atualizacao_contato": (
                    "2024-02-05T20:16:39.513000-03:00"
                ),
                "sequencia": 1,
                "codigo_dre": "108300",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()[0]
        self.assertEqual(data["codigoAluno"], 7614272)
        self.assertEqual(data["numeroAlunoChamada"], "001")
        self.assertEqual(data["celularResponsavel"], "")
        self.assertEqual(data["codigoTurma"], 0)
        self.assertIsNone(data["codigoEscola"])
        self.assertEqual(data["ano"], 0)
        self.assertIsNone(data["codigoDre"])
        self.assertFalse(data["dataMatricula"].endswith("Z"))
        mock_service.assert_called_once_with(
            codigo_turma="3015603",
            data_matricula_ticks="639059616000000000",
        )

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_200_vazio_quando_codigo_turma_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/abc/data-matricula-ticks/639059616000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_200_vazio_quando_codigo_turma_zero(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/0/data-matricula-ticks/639059616000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_400_quando_data_matricula_ticks_invalida(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/turmas/3015603/data-matricula-ticks/0/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_200_vazio_quando_sem_resultados(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            codigo_turma="3015603",
            data_matricula_ticks="639059616000000000",
        )

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
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

    @patch("apps.alunos.views.services.get_alunos_data_matricula_ticks")
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Turma nao encontrada."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), {"detail": "Turma nao encontrada."})

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoTurmaConsideraInativosViewTest(SimpleTestCase):
    """Valida a consulta de aluno da turma considerando inativos."""

    _PATH = "/api/turmas/3123349/aluno/7345634/considera-inativos/true/"

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_retorna_objeto_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 7345634,
                "nome_aluno": "HELENA SILVA DOS SANTOS",
                "nome_social_aluno": None,
                "data_nascimento": "2018-06-21",
                "codigo_situacao_matricula": 12,
                "situacao_matricula": "Cessado",
                "data_situacao": "2025-12-16T12:32:50.857000-03:00",
                "numero_aluno_chamada": None,
                "possui_deficiencia": True,
                "codigo_matricula": 44267709,
                "codigo_turma": 3123349,
                "codigo_escola": "019370",
                "ano_letivo": 2025,
                "data_matricula": "2025-12-16T12:10:53.233000-03:00",
                "nome_responsavel": "LEIDY SILVA DOS SANTOS",
                "tipo_responsavel": 1,
                "celular_responsavel": None,
                "data_atualizacao_contato": (
                    "2025-02-10T17:40:53.043000-03:00"
                ),
                "sequencia": 1,
                "codigo_dre": "108200",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["codigoAluno"], 7345634)
        self.assertEqual(data["codigoTurma"], 3123349)
        self.assertEqual(data["numeroAlunoChamada"], "000")
        self.assertEqual(data["celularResponsavel"], "")
        self.assertEqual(data["possuiDeficiencia"], 1)
        mock_service.assert_called_once_with(
            "3123349",
            considerar_inativos=True,
            codigo_aluno="7345634",
        )

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_204_quando_turma_zero(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/0/aluno/7345634/considera-inativos/true/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_204_quando_turma_negativa(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/-1/aluno/7345634/considera-inativos/true/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_400_quando_turma_nao_numerica(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/abc/aluno/7345634/considera-inativos/true/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME.",
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_400_quando_aluno_nao_numerico(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/3123349/aluno/abc/considera-inativos/true/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            "Houve um comportamento inesperado do sistema. "
            "Por favor, contate a SME.",
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_400_quando_flag_invalida(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/turmas/3123349/aluno/7345634/considera-inativos/talvez/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_204_quando_sem_resultado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Servico de alunos indisponivel."}
        )

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Aluno nÃ£o encontrado."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), {"detail": "Aluno nÃ£o encontrado."})

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoMatriculasTurmaViewTest(SimpleTestCase):
    """Valida a listagem de matrículas de um aluno em uma turma."""

    _PATH = "/api/turmas/3123349/aluno/7345634/matriculas/"

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_retorna_lista_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 7345634,
                "nome_aluno": "HELENA SILVA DOS SANTOS",
                "nome_social_aluno": None,
                "data_nascimento": "2018-06-21",
                "codigo_situacao_matricula": 1,
                "situacao_matricula": "Ativo",
                "data_situacao": "2025-12-16T12:32:50.857000-03:00",
                "numero_aluno_chamada": "15",
                "possui_deficiencia": True,
                "codigo_matricula": 44267709,
                "codigo_turma": 3123349,
                "codigo_escola": "019370",
                "ano_letivo": 2025,
                "data_matricula": "2025-12-16T12:10:53.233000-03:00",
                "nome_responsavel": "LEIDY SILVA DOS SANTOS",
                "tipo_responsavel": 1,
                "celular_responsavel": None,
                "data_atualizacao_contato": (
                    "2025-02-10T17:40:53.043000-03:00"
                ),
                "sequencia": 1,
                "codigo_dre": "108200",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["codigoAluno"], 7345634)
        self.assertEqual(data[0]["codigoTurma"], 3123349)
        mock_service.assert_called_once_with(
            "3123349",
            considerar_inativos=True,
            codigo_aluno="7345634",
        )

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_lista_vazia_quando_sem_resultado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_400_quando_turma_nao_numerica(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/turmas/abc/aluno/7345634/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_400_quando_aluno_nao_numerico(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/turmas/3123349/aluno/abc/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Aluno nÃ£o encontrado."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunosCalculoFrequenciaTurmaViewTest(SimpleTestCase):
    """Valida a listagem de códigos de aluno para cálculo de frequência."""

    _PATH = "/api/turmas/3123349/calculo-frequencia/"

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_retorna_codigos_de_aluno(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {"codigo_aluno": 7345634},
            {"codigo_aluno": 7345635},
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), ["7345634", "7345635"])
        mock_service.assert_called_once_with(
            "3123349", considerar_inativos=True
        )

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_dedup_e_ordena_ascendente(
        self, mock_service: MagicMock
    ) -> None:
        # Entrada fora de ordem e com aluno repetido (vigente+histórico):
        # o UNION (distinct) devolve o resultado ascendente.
        mock_service.return_value = [
            {"codigo_aluno": 6205175},
            {"codigo_aluno": 4896701},
            {"codigo_aluno": 5883703},
            {"codigo_aluno": 4896701},
        ]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), ["4896701", "5883703", "6205175"])

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_200_lista_vazia_quando_sem_resultado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.alunos.views.services.get_alunos_por_turma")
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Turma nÃ£o encontrada."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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


class AlunosDaUeViewTest(SimpleTestCase):
    """Valida a view de alunos matriculados em uma UE."""

    _URL = "/api/v1/alunos/ues/019362/anosLetivos/2026"

    @patch("apps.alunos.views.services.get_alunos_da_ue")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [_aluno_ue_payload()]
        client = _cliente_autenticado()

        resp = client.get(f"{self._URL}?nome_aluno=Fulano&codigo_eol=123456")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        aluno = resp.json()[0]
        self.assertEqual(len(aluno), 22)
        self.assertEqual(aluno["codigoAluno"], 123456)
        self.assertEqual(aluno["tipoTurno"], 2)
        self.assertEqual(aluno["turmaNome"], "5A")
        self.assertEqual(aluno["etapaEnsino"], 5)
        self.assertEqual(aluno["cicloEnsino"], 2)
        self.assertEqual(aluno["descEtapaEnsino"], "Ensino Fundamental")
        self.assertEqual(aluno["descCicloEnsino"], "Ciclo Interdisciplinar")
        mock_service.assert_called_once_with(
            "019362", "2026", "Fulano", "123456"
        )

    @patch("apps.alunos.views.services.get_alunos_da_ue")
    def test_404_do_sidecar_e_repassado(self, mock_service: MagicMock) -> None:
        body = {"detail": "Não foram encontradas turmas para o aluno."}
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            body,
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), body)

    @patch("apps.alunos.views.services.get_alunos_da_ue")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoTurmasPorSituacaoViewTest(SimpleTestCase):
    """Valida a view de turmas do aluno por situação/tipo."""

    _URL = (
        "/api/v1/alunos/123456/turmas/anosLetivos/2026"
        "/matriculaTurma/true/tipoTurma/false"
    )

    @patch("apps.alunos.views.services.get_turmas_aluno_por_situacao")
    def test_200_retorna_lista_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_payload()]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["codigoAluno"], 123456)
        self.assertEqual(data[0]["codigoTurma"], 9001)
        self.assertIn("idade", data[0])
        self.assertIn("dataMatricula", data[0])
        mock_service.assert_called_once_with("123456", "2026", "true", "false")

    @patch("apps.alunos.views.services.get_turmas_aluno_por_situacao")
    def test_404_repassa_quando_sem_turma(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND,
            {"detail": "Não foram encontradas turmas para o aluno."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            resp.json(),
            {"detail": "Não foram encontradas turmas para o aluno."},
        )

    @patch("apps.alunos.views.services.get_turmas_aluno_por_situacao")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de alunos indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunosAtivosTurmaViewTest(SimpleTestCase):
    """Valida a view de alunos ativos da turma (contrato legado)."""

    _URL = "/api/v1/alunos/turmas/9001/ativos"

    def _payload(self) -> dict:
        return _alunos_ativos_turma_payload()

    @patch("apps.alunos.views.services.get_alunos_ativos_turma")
    def test_200_replica_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [self._payload()]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        # 29 campos do contrato legado
        self.assertEqual(len(item), 29)
        # campos com dado real
        self.assertEqual(item["codigoAluno"], 123456)
        self.assertEqual(item["situacaoMatricula"], "Ativo")
        self.assertEqual(item["numeroAlunoChamada"], "006")
        self.assertEqual(item["dataNascimento"], "2015-04-27T00:00:00")
        # campos default fixos do legado (ignoram o dado do MS)
        self.assertEqual(item["codigoComponenteCurricular"], 0)
        self.assertEqual(item["dataMatricula"], "0001-01-01T00:00:00")
        self.assertEqual(item["possuiDeficiencia"], 0)
        self.assertFalse(item["transferencia_Interna"])
        self.assertEqual(item["codigoTurma"], 0)
        self.assertEqual(item["codigoMatricula"], 0)
        self.assertIsNone(item["codigoEscola"])
        self.assertEqual(item["ano"], 0)
        self.assertIsNone(item["id"])
        self.assertIsNone(item["nomeResponsavel"])
        mock_service.assert_called_once_with("9001")

    @patch("apps.alunos.views.services.get_alunos_ativos_turma")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunosAtivosPeriodoTurmaViewTest(SimpleTestCase):
    """Valida a view de alunos ativos por período da turma."""

    _URL = "/api/v1/alunos/turmas/9001/ativos/2026-12-31"

    @patch("apps.alunos.views.services.get_alunos_ativos_turma_periodo")
    def test_200_replica_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [_alunos_ativos_turma_payload()]
        client = _cliente_autenticado()

        resp = client.get(self._URL + "?data_referencia_inicio=2026-01-01")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(len(item), 29)
        self.assertEqual(item["codigoAluno"], 123456)
        self.assertEqual(item["dataMatricula"], "0001-01-01T00:00:00")
        mock_service.assert_called_once_with(
            "9001", "2026-12-31", "2026-01-01"
        )

    @patch("apps.alunos.views.services.get_alunos_ativos_turma_periodo")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_403_sem_autenticacao(self) -> None:
        resp = APIClient().get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class TotalAlunosAtivosPeriodoViewTest(SimpleTestCase):
    """Valida a view do total de alunos ativos por período."""

    _URL = (
        "/api/v1/alunos/ativos/anos/5/anos-letivos/2026/"
        "inicio/2026-01-01/fim/2026-12-31"
    )

    @patch("apps.alunos.views.services.get_total_alunos_ativos_periodo")
    def test_200_retorna_numero_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {"quantidade": 42}
        client = _cliente_autenticado()

        resp = client.get(
            self._URL
            + "?ue_id=100001&dre_id=108800&modalidades=5&modalidades=6"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), 42)
        mock_service.assert_called_once_with(
            ano_turma="5",
            ano_letivo="2026",
            data_inicio="2026-01-01",
            data_fim="2026-12-31",
            ue_id="100001",
            dre_id="108800",
            modalidades=["5", "6"],
        )

    @patch("apps.alunos.views.services.get_total_alunos_ativos_periodo")
    def test_repassa_400_do_sidecar(self, mock_service: MagicMock) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_400_BAD_REQUEST,
            {"detail": "Parâmetro inválido."},
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), {"detail": "Parâmetro inválido."})

    @patch("apps.alunos.views.services.get_total_alunos_ativos_periodo")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_403_sem_autenticacao(self) -> None:
        resp = APIClient().get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


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


class CodigosTurmasRegularesAlunoViewTest(SimpleTestCase):
    """Valida o endpoint .../regulares (endpoint 3)."""

    _PATH = "/api/turmas/anos-letivos/2026/alunos/7345634/regulares/"
    _SVC = "apps.alunos.views.services.montar_codigos_turmas_regulares_aluno"

    @patch(_SVC)
    def test_200_retorna_codigos(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [23456, 12345]
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), ["23456", "12345"])
        mock_service.assert_called_once_with(
            ano_letivo="2026",
            codigo_aluno="7345634",
            tipos_turma=[],
            ue_codigo=None,
            data_referencia=None,
            semestre=None,
        )

    @patch(_SVC)
    def test_200_repassa_filtros_da_query(
        self, mock_service: MagicMock
    ) -> None:
        """Testa que os filtros da query string são repassados para o serviço."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            self._PATH + "?tipos_turma=1&tipos_turma=5&ue_codigo=019370"
            "&data_referencia=2026-06-01&semestre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            ano_letivo="2026",
            codigo_aluno="7345634",
            tipos_turma=[1, 5],
            ue_codigo="019370",
            data_referencia="2026-06-01",
            semestre=1,
        )

    @patch(_SVC)
    def test_200_lista_vazia_quando_sem_resultado(
        self, mock_service: MagicMock
    ) -> None:
        """Testa que o endpoint retorna 200 e lista vazia quando o serviço"""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch(_SVC)
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        """Testa que o endpoint retorna 503 quando o serviço de alunos está"""
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch(_SVC)
    def test_preserva_erro_http_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            status.HTTP_404_NOT_FOUND, {"detail": "nao encontrado"}
        )
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_403_sem_autenticacao(self) -> None:
        """Testa que o endpoint retorna 403 quando não há autenticação."""
        resp = APIClient().get(self._PATH)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class CodigoTurmaAlunoComponenteCurricularViewTest(SimpleTestCase):
    """Valida o endpoint componentes-curriculares (endpoint 4)."""

    _PATH = (
        "/api/turmas/anos-letivos/2026/alunos/7345634/"
        "componentes-curriculares/512/"
    )
    _SVC = "apps.alunos.views.services.montar_codigos_turmas_regulares_aluno"

    @patch(_SVC)
    def test_200_ignora_componente_e_so_passa_tipos_turma(
        self, mock_service: MagicMock
    ) -> None:
        """Testa que o endpoint retorna 200 e lista de códigos de turma, ignorando"""
        mock_service.return_value = [12345]
        client = _cliente_autenticado()

        resp = client.get(self._PATH + "?tipos_turma=1&ue_codigo=019370")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), ["12345"])
        # Alias do endpoint 3: só tipos_turma é considerado; ue_codigo é
        # ignorado (conforme a assinatura deste endpoint).
        mock_service.assert_called_once_with(
            ano_letivo="2026",
            codigo_aluno="7345634",
            tipos_turma=[1],
        )

    @patch(_SVC)
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        """Testa que o endpoint retorna 503 quando o serviço de alunos está"""
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._PATH)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_403_sem_autenticacao(self) -> None:
        """Testa que o endpoint retorna 403 quando não há autenticação."""
        resp = APIClient().get(self._PATH)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AlunoTurmasComHistoricoViewTest(SimpleTestCase):
    """Valida a view de turmas do aluno com histórico explícito."""

    _URL = (
        "/api/v1/alunos/7074492/turmas/anosLetivos/2026/historico/false"
        "/filtrar-situacao/true/tipo-turma/true"
    )

    @patch("apps.alunos.views.services.get_turmas_aluno_com_historico")
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_payload()]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data[0]["codigoAluno"], 123456)
        self.assertEqual(data[0]["codigoTurma"], 9001)
        mock_service.assert_called_once_with(
            "7074492", "2026", "false", "true", "true"
        )

    @patch("apps.alunos.views.services.get_turmas_aluno_com_historico")
    def test_400_quando_codigo_aluno_em_branco(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/alunos/%20/turmas/anosLetivos/2026/historico/false"
            "/filtrar-situacao/true/tipo-turma/true"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.get_turmas_aluno_com_historico")
    def test_repassa_404_do_sidecar(self, mock_service: MagicMock) -> None:
        mock_service.side_effect = _http_status_error(
            404, {"detail": "Não foram encontradas turmas para o aluno."}
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.alunos.views.services.get_turmas_aluno_com_historico")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )


class AlunosPorAnoViewTest(SimpleTestCase):
    """Valida a view de alunos por códigos e ano letivo."""

    _URL = "/api/v1/alunos/anoLetivo/2026/alunos"

    @patch("apps.alunos.views.services.listar_alunos_por_ano")
    def test_200_retorna_alunos(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_payload(1), _turma_payload(2)]
        client = _cliente_autenticado()

        resp = client.get(
            self._URL + "?codigos_aluno=1&codigos_aluno=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["codigoAluno"], 1)
        mock_service.assert_called_once_with("2026", ["1", "2"])

    @patch("apps.alunos.views.services.listar_alunos_por_ano")
    def test_200_aceita_alias_camelcase(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [_turma_payload(1)]
        client = _cliente_autenticado()

        resp = client.get(self._URL + "?codigosAluno=1")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with("2026", ["1"])

    @patch("apps.alunos.views.services.listar_alunos_por_ano")
    def test_601_quando_codigos_ausentes(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, 601)
        self.assertEqual(
            resp.json(), "Os códigos dos Alunos são obrigatórios."
        )
        mock_service.assert_not_called()

    @patch("apps.alunos.views.services.listar_alunos_por_ano")
    def test_repassa_status_601_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            601, "Os códigos dos Alunos são obrigatórios."
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL + "?codigos_aluno=1")

        self.assertEqual(resp.status_code, 601)

    @patch("apps.alunos.views.services.listar_alunos_por_ano")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL + "?codigos_aluno=1")

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )


class QuantidadeMatriculadosCCViewTest(SimpleTestCase):
    """Valida a view de matriculados por componente curricular."""

    _URL = "/api/v1/alunos/ano-letivo/2026/matriculados"

    @patch("apps.alunos.views.services.get_quantidade_matriculados_cc")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "componente_curricular_id": 1310,
                "quantidade": 7,
                "ordem": 0,
                "modalidade": None,
                "ano": "1",
                "turma": "1A",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            self._URL + "?componentes_curriculares=1310&ue_id=093181"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        corpo = resp.json()[0]
        self.assertEqual(
            list(corpo),
            [
                "componenteCurricularId",
                "quantidade",
                "ordem",
                "modalidade",
                "ano",
                "turma",
            ],
        )
        self.assertEqual(corpo["componenteCurricularId"], 1310)
        self.assertEqual(corpo["quantidade"], 7)
        mock_service.assert_called_once_with(
            ano_letivo="2026",
            componentes_curriculares=["1310"],
            dre_id=None,
            ue_id="093181",
        )

    @patch("apps.alunos.views.services.get_quantidade_matriculados_cc")
    def test_repassa_status_601_do_sidecar(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _http_status_error(
            601,
            "Os códigos dos componentes curriculares são obrigatórios.",
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, 601)

    @patch("apps.alunos.views.services.get_quantidade_matriculados_cc")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            self._URL + "?componentes_curriculares=1310"
        )

        self.assertEqual(
            resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )
