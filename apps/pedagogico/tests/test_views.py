"""Valida as views do domínio pedagógico."""

from typing import Any
from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/v1/componentes-curriculares"
_PREFIX_TURMAS = "/api/turmas"
_PREFIX_UES = "/api/ues"


# Componente curricular completo retornado pelo sidecar.
_CC: dict[str, Any] = {
    "codigo": 1,
    "codigo_componente_territorio_saber": None,
    "codigo_componente_curricular_pai": None,
    "descricao": "Matematica",
    "regencia": False,
    "planejamento_regencia": False,
    "territorio_saber": False,
    "turma_codigo": None,
    "exibir_componente_eol": True,
    "professor": None,
    "codigos_territorios_agrupamento": [],
}

# Resumo de componente (apenas código e descrição).
_BASE_CC = {"codigo": 1, "descricao": "Matematica"}

# Item de grade curricular retornado pelo sidecar.
_GRADE = {
    "codigo_componente_curricular": 1,
    "descricao_componente_curricular": "Matematica",
    "codigo_ano_turma": "1",
    "descricao_serie_ensino": "1o Ano",
    "codigo_serie_ensino": 1,
    "modalidade": 5,
}

_REGENCIA = {
    "ano_turma": "1",
    "ano_letivo": 2024,
    "codigo": 1,
    "codigo_componente_territorio_saber": 0,
    "descricao": "Regencia",
    "territorio_saber": False,
    "tipo_escola": None,
    "turno_turma": 0,
    "componente_planejamento_regencia": False,
    "turma_codigo": None,
    "professor": None,
    "inicio_atribuicao": None,
    "fim_atribuicao": None,
}

_TURMA = {
    "ano": "1",
    "anoLetivo": 2026,
    "codigo": 3034092,
    "tipoTurma": 1,
    "modalidade": "Fundamental",
    "codigoModalidade": 5,
    "nomeTurma": "1A",
    "semestre": 0,
    "duracaoTurno": 55,
    "tipoTurno": 6,
    "dataFim": None,
    "ehistorico": False,
    "ensinoEspecial": False,
    "etapaEJA": 0,
    "serieEnsino": "1o Ano",
    "dataInicioTurma": "2026-02-04T00:00:00",
    "extinta": False,
    "situacao": "O",
    "ueCodigo": "092622",
}

_TURMA_HISTORICA_MS = {
    "ano": "7",
    "ano_letivo": 2025,
    "codigo": 2825477,
    "modalidade": "Infantil",
    "codigo_modalidade": 1,
    "nome_turma": "7A",
    "semestre": 0,
}

_SINCRONIZACAO_INSTITUCIONAL = {
    "ano": "7",
    "ano_letivo": 2026,
    "codigo": 3010807,
    "tipo_turma": 1,
    "modalidade": "Infantil",
    "codigo_modalidade": 1,
    "nome_turma": "7A",
    "semestre": 0,
    "duracao_turno": 6,
    "tipo_turno": 1,
    "data_fim_turma": None,
    "ensino_especial": False,
    "etapa_eja": 0,
    "serie_ensino": "INFANTIL UNIFICADO",
    "data_inicio_turma": "2026-02-04T03:00:00Z",
    "extinta": False,
    "situacao": "O",
    "ue_codigo": "091120",
    "data_atualizacao": "2026-06-17T08:11:45.807000Z",
    "data_status_turma_escola": "2026-06-03T18:46:18.833000Z",
    "etapa_ensino": 1,
    "ciclo_ensino": 2,
    "tipo_escola": 2,
    "descricao_grade_programa": "INFANTIL UNIFICADO",
    "tipo_grade_programa": 1,
    "codigo_grade_programa": 4239,
    "nome_filtro": "7A - INFANTIL UNIFICADO",
    "componentes": [
        {
            "nome_componente_curricular": "ED.INF. EMEI 4 HS",
            "componente_curricular_codigo": 512,
            "registro_funcional": "7393423",
            "data_disponibizacao": None,
        }
    ],
}

_ITINERARIOS_ENSINO_MEDIO = [
    {
        "id": 9,
        "nome": "Investigação cientifica",
        "serie": "2",
    },
    {
        "id": 9,
        "nome": "Investigação cientifica",
        "serie": "2",
    },
]


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()

    user = User(username="teste")
    client.force_authenticate(user=user)

    return client


class ComponentesTurmaViewSetTest(SimpleTestCase):
    """Valida a view de componentes por turmas de uma UE."""

    @patch("apps.pedagogico.views.services.get_componentes_por_turmas_ue")
    def test_200_repassa_turmas(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/turmas/?turmas=T001&turmas=T002"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_id="UE001", turmas=["T001", "T002"]
        )


class TurmasRegularesViewSetTest(SimpleTestCase):
    """Valida a view de turmas regulares."""

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_200_retorna_lista_de_codigos(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = ["3014194", "3024590"]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            ["3024590", "3014194"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, ["3014194", "3024590"])
        mock_svc.assert_called_once_with(["3024590", "3014194"])

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_400_quando_payload_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            ["3024590", "ABC"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class TurmasProgramaViewSetTest(SimpleTestCase):
    """Valida a view de turmas programa."""

    @patch("apps.pedagogico.views.services.post_turmas_programa")
    def test_200_retorna_lista_de_codigos(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = ["3133093", "3133096"]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-programa/",
            ["3133093", "3133096"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, ["3133093", "3133096"])
        mock_svc.assert_called_once_with(["3133093", "3133096"])

    @patch("apps.pedagogico.views.services.post_turmas_programa")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-programa/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class ListarTurmasViewSetTest(SimpleTestCase):
    """Valida a view de listagem de turmas."""

    @patch("apps.pedagogico.views.services.post_listar_turmas")
    def test_200_retorna_dados_de_turmas(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = [_TURMA]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/listar-turmas/",
            ["3034092"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["codigo"], 3034092)
        self.assertEqual(resp.data[0]["nomeTurma"], "1A")
        mock_svc.assert_called_once_with(["3034092"])

    @patch("apps.pedagogico.views.services.post_listar_turmas")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/listar-turmas/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class DadosTurmaViewSetTest(SimpleTestCase):
    """Valida a view de dados da turma."""

    @patch("apps.pedagogico.views.services.get_dados_turma")
    def test_200_retorna_dados_da_turma(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = _TURMA
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/3034092/dados/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["codigo"], 3034092)
        self.assertEqual(resp.data["ueCodigo"], "092622")
        mock_svc.assert_called_once_with("3034092")


class TurmasHistoricasGeraisProfessorViewSetTest(SimpleTestCase):
    """Valida a consulta de turmas históricas gerais do professor."""

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_200_retorna_contrato_legado(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = [_TURMA_HISTORICA_MS]
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/08381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["anoLetivo"], 2025)
        self.assertEqual(response.data[0]["tipoTurma"], 0)
        self.assertEqual(response.data[0]["duracaoTurno"], 0)
        self.assertIsNone(response.data[0]["ueCodigo"])
        mock_service.assert_called_once_with(
            ano_letivo=2025,
            professor_rf="08381399",
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_200_retorna_lista_vazia(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_preserva_erro_http_do_sidecar(
        self,
        mock_service: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        sidecar_response = httpx.Response(
            404,
            request=request,
            json={"detail": "Professor não encontrado."},
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=sidecar_response,
        )
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data,
            {"detail": "Professor não encontrado."},
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_preserva_erro_http_sem_json(
        self,
        mock_service: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        sidecar_response = httpx.Response(
            500,
            request=request,
            text="Falha interna",
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=sidecar_response,
        )
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(response.data, {"detail": "Falha interna"})

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_503_quando_sidecar_indisponivel(
        self,
        mock_service: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        mock_service.side_effect = httpx.ConnectError(
            "Sidecar indisponível",
            request=request,
        )
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data,
            {"detail": "Servico pedagogico indisponivel."},
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_502_quando_service_rejeita_estrutura(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.side_effect = ValueError(
            "Resposta de turmas históricas deve ser uma lista de objetos."
        )
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.data,
            {"detail": "Resposta do servico pedagogico invalida."},
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_turmas_historicas_gerais_professor"
    )
    def test_502_quando_item_for_invalido(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = [{"ano": "7"}]
        client = _cliente_autenticado()

        response = client.get(
            f"{_PREFIX_TURMAS}/anos-letivos/2025/professor/8381399/"
            "turmas-historicas-geral/"
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)


class SincronizacaoInstitucionalTurmaViewSetTest(SimpleTestCase):
    """Valida a view de sincronização institucional da turma."""

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_200_retorna_contrato_legado(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = _SINCRONIZACAO_INSTITUCIONAL
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["modalidade"], "1")
        self.assertEqual(resp.data["tipoGradePrograma"], 1)
        self.assertEqual(resp.data["ueCodigo"], "091120")
        self.assertEqual(
            resp.data["componentes"][0]["registroFuncional"],
            "7393423",
        )
        mock_svc.assert_called_once_with(
            codigo_ue="091120",
            codigo_turma="3010807",
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_400_quando_codigo_turma_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/abc/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {"detail": "O código da turma e Ue são obrigatórios"},
        )
        mock_svc.assert_not_called()

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_400_quando_codigo_turma_zero(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/0/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data,
            {"detail": "O código da turma e Ue são obrigatórios"},
        )
        mock_svc.assert_not_called()

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_preserva_erro_http_do_sidecar(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            404,
            request=request,
            json={"detail": "Turma não encontrada."},
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data, {"detail": "Turma não encontrada."})

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_preserva_erro_http_sem_json(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            500,
            request=request,
            text="Falha institucional",
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(
            resp.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(resp.data, {"detail": "Falha institucional"})

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacao_institucional_turma"
    )
    def test_503_quando_sidecar_indisponivel(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        mock_svc.side_effect = httpx.ConnectError(
            "Sidecar indisponível",
            request=request,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_UES}/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.data,
            {"detail": "Servico pedagogico indisponivel."},
        )


class SincronizacoesInstitucionaisAnosLetivosViewSetTest(SimpleTestCase):
    """Valida a consulta institucional de turmas por anos letivos."""

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_200_retorna_codigos_com_anos_repetidos(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = [3036295, 3082921, 3036225]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=2025&anos_letivos_vigente=2026"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [3036295, 3082921, 3036225])
        mock_svc.assert_called_once_with(
            codigo_ue="019437",
            anos_letivos_vigente=[2025, 2026],
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_200_aceita_array_textual_do_swagger(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/",
            {"anos_letivos_vigente": "[2025, 2026]"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_ue="019437",
            anos_letivos_vigente=[2025, 2026],
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_200_sem_filtro(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_ue="019437",
            anos_letivos_vigente=None,
        )

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_400_quando_ano_for_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
            "?anos_letivos_vigente=invalido"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_preserva_erro_http_do_sidecar(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            404,
            request=request,
            json={"detail": "UE não encontrada."},
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data, {"detail": "UE não encontrada."})

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_preserva_erro_http_sem_json(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            500,
            request=request,
            text="Falha na consulta",
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
        )

        self.assertEqual(
            resp.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(resp.data, {"detail": "Falha na consulta"})

    @patch(
        "apps.pedagogico.views.services."
        "get_sincronizacoes_institucionais_anos_letivos"
    )
    def test_503_quando_sidecar_indisponivel(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        mock_svc.side_effect = httpx.ConnectError(
            "Sidecar indisponível",
            request=request,
        )
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.data,
            {"detail": "Servico pedagogico indisponivel."},
        )


class ItinerariosEnsinoMedioViewSetTest(SimpleTestCase):
    """Valida a listagem de itinerários do ensino médio."""

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_200_converte_serie_e_preserva_ordem_e_duplicidades(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = _ITINERARIOS_ENSINO_MEDIO
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data,
            [
                {
                    "id": 9,
                    "nome": "Investigação cientifica",
                    "serie": 2,
                },
                {
                    "id": 9,
                    "nome": "Investigação cientifica",
                    "serie": 2,
                },
            ],
        )
        mock_svc.assert_called_once_with()

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_200_retorna_lista_vazia(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_preserva_erro_http_do_sidecar(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            404,
            request=request,
            json={"detail": "Itinerários não encontrados."},
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            resp.data,
            {"detail": "Itinerários não encontrados."},
        )

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_preserva_erro_http_sem_json(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        response = httpx.Response(
            500,
            request=request,
            text="Falha nos itinerários",
        )
        mock_svc.side_effect = httpx.HTTPStatusError(
            "Erro no sidecar",
            request=request,
            response=response,
        )
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(
            resp.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(resp.data, {"detail": "Falha nos itinerários"})

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_503_quando_sidecar_indisponivel(
        self,
        mock_svc: MagicMock,
    ) -> None:
        request = httpx.Request("GET", "https://sidecar.local/test")
        mock_svc.side_effect = httpx.ConnectError(
            "Sidecar indisponível",
            request=request,
        )
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.data,
            {"detail": "Servico pedagogico indisponivel."},
        )

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_502_quando_contrato_canonico_for_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = [
            {"id": 9, "nome": "Itinerário", "serie": "inválida"}
        ]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.data,
            {"detail": "Resposta do servico pedagogico invalida."},
        )

    @patch("apps.pedagogico.views.services.get_itinerarios_ensino_medio")
    def test_502_quando_service_rejeita_estrutura(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.side_effect = ValueError(
            "Resposta de itinerários deve ser uma lista de objetos."
        )
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/itinerario/ensino-medio/")

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)


class TurmasSchemaTest(SimpleTestCase):
    """Valida a documentacao de turmas no schema OpenAPI."""

    def test_endpoints_usam_tag_turma(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        schema = resp.data
        self.assertEqual(
            schema["paths"]["/api/turmas/turmas-regulares/"]["post"]["tags"],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/turmas-programa/"]["post"]["tags"],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/listar-turmas/"]["post"]["tags"],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/{codigo_turma}/dados/"]["get"][
                "tags"
            ],
            ["Turma"],
        )
        path = (
            "/api/ues/{codigo_ue}/turmas/{codigo_turma}/"
            "sincronizacoes-institucionais/"
        )
        self.assertEqual(schema["paths"][path]["get"]["tags"], ["Turma"])
        self.assertNotIn(
            "/api/turmas/ues/{codigo_ue}/turmas/{codigo_turma}/"
            "sincronizacoes-institucionais/",
            schema["paths"],
        )
        anos_path = (
            "/api/turmas/ue/{codigo_ue}/"
            "sincronizacoes-institucionais/anos-letivos/"
        )
        operation = schema["paths"][anos_path]["get"]
        self.assertEqual(operation["tags"], ["Turma"])
        query = next(
            item
            for item in operation["parameters"]
            if item["name"] == "anos_letivos_vigente"
        )
        self.assertFalse(query.get("required", False))
        self.assertEqual(query["schema"]["type"], "array")
        self.assertEqual(query["schema"]["items"]["type"], "integer")
        itinerarios_path = "/api/turmas/itinerario/ensino-medio/"
        itinerarios = schema["paths"][itinerarios_path]["get"]
        self.assertEqual(itinerarios["tags"], ["Turma"])
        response_schema = itinerarios["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        self.assertEqual(response_schema["type"], "array")
        turmas_historicas_path = (
            "/api/turmas/anos-letivos/{ano_letivo}/professor/"
            "{professor_rf}/turmas-historicas-geral/"
        )
        turmas_historicas = schema["paths"][turmas_historicas_path]["get"]
        self.assertEqual(turmas_historicas["tags"], ["Turma"])
        self.assertEqual(
            turmas_historicas["responses"]["200"]["content"][
                "application/json"
            ]["schema"]["type"],
            "array",
        )

    def test_body_nao_obrigatorio_e_descreve_codigos_turmas(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        schema = resp.data
        paths = (
            "/api/turmas/turmas-regulares/",
            "/api/turmas/turmas-programa/",
        )
        for path in paths:
            with self.subTest(path=path):
                operation = schema["paths"][path]["post"]
                self.assertFalse(
                    operation["requestBody"].get("required", False)
                )
                self.assertIn(
                    "RequestBody: `codigos_turmas`",
                    operation["description"],
                )


class ComponentesNovosSchemaTest(SimpleTestCase):
    """Valida a documentação dos novos endpoints no OpenAPI."""

    def test_endpoints_possuem_resumo_e_descricao(self) -> None:
        """Garante que todas as operações tenham documentação textual."""
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        schema = resp.data
        operacoes = (
            (
                "/api/v1/componentes-curriculares/turmas/"
                "{codigo_turma}/funcionarios/{login}/perfis/{id_perfil}/"
                "agrupaComponenteCurricular/"
                "{agrupa_componente_curricular}/",
                "get",
            ),
            (
                "/api/v1/componentes-curriculares/turmas/"
                "{codigo_turma}/funcionarios/{login}/perfis/{id_perfil}/"
                "planejamento/",
                "get",
            ),
            ("/api/v1/componentes-curriculares/turmas/", "get"),
            ("/api/v1/componentes-curriculares/turmas/regulares/", "get"),
            ("/api/v1/componentes-curriculares/dados-aula-turma/", "get"),
            (
                "/api/v1/componentes-curriculares/turmas/"
                "{codigo_turma}/sem-atribuicao/{data_base_tick}/",
                "get",
            ),
        )

        for path, metodo in operacoes:
            with self.subTest(path=path, metodo=metodo):
                operation = schema["paths"][path][metodo]
                self.assertTrue(operation["summary"])
                self.assertTrue(operation["description"])

    def test_endpoint_agrupamento_nao_expoe_post(self) -> None:
        """Garante que o contrato de agrupamento permaneça somente GET."""
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        path = (
            "/api/v1/componentes-curriculares/turmas/"
            "{codigo_turma}/funcionarios/{login}/perfis/{id_perfil}/"
            "agrupaComponenteCurricular/"
            "{agrupa_componente_curricular}/"
        )
        self.assertNotIn("post", resp.data["paths"][path])

    def test_agrupamento_documentado_como_booleano(self) -> None:
        """Expõe o agrupamento como seletor booleano no Swagger."""
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        path = (
            "/api/v1/componentes-curriculares/turmas/"
            "{codigo_turma}/funcionarios/{login}/perfis/{id_perfil}/"
            "agrupaComponenteCurricular/"
            "{agrupa_componente_curricular}/"
        )
        parametros = resp.data["paths"][path]["get"]["parameters"]
        agrupamento = next(
            item
            for item in parametros
            if item["name"] == "agrupa_componente_curricular"
        )
        self.assertEqual(agrupamento["schema"]["type"], "boolean")
        self.assertEqual(
            set(agrupamento["schema"]["enum"]),
            {True, False},
        )

    def test_dados_aula_serializa_componentes_como_query_repetida(
        self,
    ) -> None:
        """Documenta a lista conforme o formato aceito pelo legado."""
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        path = "/api/v1/componentes-curriculares/dados-aula-turma/"
        parametros = resp.data["paths"][path]["get"]["parameters"]
        componentes = next(
            item
            for item in parametros
            if item["name"] == "componentesCurriculares"
        )
        self.assertEqual(componentes["schema"]["type"], "array")
        self.assertEqual(componentes["style"], "form")
        self.assertTrue(componentes["explode"])


class ComponentesCurricularesViewSetTest(SimpleTestCase):
    """Valida a view de catálogo de componentes curriculares."""

    @patch("apps.pedagogico.views.services.get_componentes_curriculares")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()


class GradeComponentesCurricularesViewSetTest(SimpleTestCase):
    """Valida a view de grade curricular por ano letivo."""

    @patch("apps.pedagogico.views.services.get_grade_curricular")
    def test_200_retorna_grade(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_GRADE]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ano-turma/ano-letivo/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data[0]["codigoComponenteCurricular"],
            1,
        )
        self.assertEqual(resp.data[0]["codigoAnoTurma"], "1")
        mock_svc.assert_called_once_with(2024)


class ComponentesRegenciaViewSetTest(SimpleTestCase):
    """Valida a view de componentes de regencia."""

    @patch("apps.pedagogico.views.services.get_componentes_regencia")
    def test_200_retorna_regencia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_REGENCIA]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/anos/2024/regencia/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["anoTurma"], "1")
        self.assertEqual(resp.data[0]["anoLetivo"], 2024)
        self.assertEqual(
            resp.data[0]["codigoComponenteTerritorioSaber"],
            0,
        )
        self.assertEqual(
            resp.data[0]["componentePlanejamentoRegencia"],
            False,
        )
        mock_svc.assert_called_once_with(2024)

    @patch("apps.pedagogico.views.services.get_componentes_regencia")
    def test_204_quando_regencia_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/anos/9/regencia/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with(9)


class ValidarComponentePapViewSetTest(SimpleTestCase):
    """Valida a view de componente PAP."""

    @patch("apps.pedagogico.views.services.validar_componente_pap")
    def test_200_repassa_parametros_do_path(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = True
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/"
            "perfis/P1/validar/pap/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data)
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            login="RF001",
            id_perfil="P1",
        )


class ComponentesFuncionarioViewSetTest(SimpleTestCase):
    """Valida a view de componentes por funcionario."""

    @patch("apps.pedagogico.views.services.get_componentes_funcionario")
    def test_200_retorna_componentes(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/funcionarios/RF001/perfis/P1/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["planejamentoRegencia"], False)
        self.assertEqual(resp.data[0]["turmaCodigo"], None)
        mock_svc.assert_called_once_with(
            login="RF001",
            id_perfil="P1",
        )

    @patch("apps.pedagogico.views.services.get_componentes_funcionario")
    def test_204_quando_lista_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/funcionarios/RF001/perfis/P1/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with(
            login="RF001",
            id_perfil="P1",
        )


class ComponentesTurmaFuncionarioViewSetTest(SimpleTestCase):
    """Valida a view de componentes por turma e funcionário."""

    @patch("apps.pedagogico.views.services.get_componentes_turma_funcionario")
    def test_get_repassa_path_e_filtros(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/perfis/P1/"
            "agrupaComponenteCurricular/true/"
            "?checaMotivoDisponibilizacao=false"
            "&consideraTurmaInfantil=true"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["codigo"], 1)
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            login="RF001",
            id_perfil="P1",
            agrupa_componente_curricular=True,
            checa_motivo_disponibilizacao=False,
            considera_turma_infantil=True,
        )

    @patch("apps.pedagogico.views.services.get_componentes_turma_funcionario")
    def test_get_retorna_204_quando_vazio(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/perfis/P1/"
            "agrupaComponenteCurricular/false/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class ComponentesPlanejamentoViewSetTest(SimpleTestCase):
    """Valida a view de componentes para planejamento."""

    @patch("apps.pedagogico.views.services.get_componentes_planejamento")
    def test_repassa_parametros_do_path(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/"
            "perfis/P1/planejamento/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @patch("apps.pedagogico.views.services.get_componentes_planejamento")
    def test_retorna_204_quando_lista_vazia(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/perfis/P1/"
            "planejamento/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            login="RF001",
            id_perfil="P1",
        )


class ComponentesPorListaTurmasViewSetTest(SimpleTestCase):
    """Valida a view de componentes por lista de turmas."""

    @patch("apps.pedagogico.views.services.get_componentes_por_lista_turmas")
    def test_repassa_turmas_e_planejamento(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/?codigoTurmas=T001&codigoTurmas=T002"
            "&adicionarComponentesPlanejamento=false"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigos_turmas=["T001", "T002"],
            adicionar_componentes_planejamento=False,
        )


class ComponentesTurmasRegularesViewSetTest(SimpleTestCase):
    """Valida a view de componentes de turmas regulares."""

    @patch("apps.pedagogico.views.services.get_componentes_turmas_regulares")
    def test_repassa_lista_de_turmas(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/regulares/"
            "?codigoTurmas=T001&codigoTurmas=T002"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(["T001", "T002"])


class DadosAulaTurmaViewSetTest(SimpleTestCase):
    """Valida a view de dados de aula por turma."""

    @patch("apps.pedagogico.views.services.get_dados_aula_turma")
    def test_repassa_filtros(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [
            {
                "componenteCurricularCodigo": "138",
                "componenteCurricularDescricao": "LINGUA PORTUGUESA",
                "turmaCodigo": "T001",
                "dataInicioTurma": "2024-02-05T00:00:00",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/dados-aula-turma/?ueCodigo=UE001"
            "&anoLetivo=2024&componentesCurriculares=138&semestre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["turmaCodigo"], "T001")
        mock_svc.assert_called_once_with(
            ue_codigo="UE001",
            ano_letivo=2024,
            componentes_curriculares=["138"],
            semestre=1,
        )

    @patch("apps.pedagogico.views.services.get_dados_aula_turma")
    def test_normaliza_array_json_enviado_pelo_swagger(
        self,
        mock_svc: MagicMock,
    ) -> None:
        """Converte o array textual do Swagger em parâmetros separados."""
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/dados-aula-turma/?ueCodigo=000566"
            "&anoLetivo=2024"
            "&componentesCurriculares=%5B%221030%22%2C%20%221056%22%5D"
            "&semestre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_codigo="000566",
            ano_letivo=2024,
            componentes_curriculares=["1030", "1056"],
            semestre=1,
        )


class ComponentesSemAtribuicaoViewSetTest(SimpleTestCase):
    """Valida a view de componentes sem atribuição."""

    @patch("apps.pedagogico.views.services.get_componentes_sem_atribuicao")
    def test_repassa_turma_e_ticks(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = ["ARTE", "EDUCACAO FISICA"]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/sem-atribuicao/" "638396640000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, ["ARTE", "EDUCACAO FISICA"])
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            data_base_tick=638396640000000000,
        )


class ComponentesTurmaAnoViewSetTest(SimpleTestCase):
    """Valida a view de componentes por anos escolares."""

    @patch("apps.pedagogico.views.services.get_componentes_ue_anos")
    def test_200_repassa_anos_escolares(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024"
            "/anos-escolares/?anosEscolares=1&anosEscolares=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data[0]["codigoComponenteTerritorioSaber"],
            None,
        )
        self.assertEqual(resp.data[0]["planejamentoRegencia"], False)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
            anos_escolares=["1", "2"],
        )


class ComponentesTurmaProgramaViewSetTest(SimpleTestCase):
    """Valida a view de componentes de turmas programa."""

    @patch("apps.pedagogico.views.services.get_componentes_turmas_programa")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["turmaCodigo"], None)
        self.assertEqual(resp.data[0]["exibirComponenteEOL"], True)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
        )


# Agrupamento de Território do Saber retornado pelo sidecar.
_AGRUPAMENTO: dict[str, Any] = {
    "codigo": 9001,
    "codigo_componente_territorio_saber": 1214,
    "codigo_componente_curricular_pai": None,
    "descricao": "TERRIT SABER / EXP PEDAG 1",
    "regencia": False,
    "planejamento_regencia": False,
    "territorio_saber": True,
    "turma_codigo": "2524172",
    "exibir_componente_eol": True,
    "professor": "6232191",
    "codigos_territorios_agrupamento": [1214],
}


class AgrupamentosCorrelacionadosViewSetTest(SimpleTestCase):
    """Valida a view de agrupamentos correlacionados por cod_agrupamento."""

    @patch("apps.pedagogico.views.services.get_agrupamentos_correlacionados")
    def test_200_sem_data_base_tick(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/1214/territorio-saber/agrupamentos-correlacionados/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["codigo"], 9001)
        self.assertEqual(resp.data[0]["territorioSaber"], True)
        self.assertEqual(resp.data[0]["codigosTerritoriosAgrupamento"], [1214])
        mock_svc.assert_called_once_with(
            codigo_componente=1214,
            data_base_tick=None,
        )

    @patch("apps.pedagogico.views.services.get_agrupamentos_correlacionados")
    def test_200_com_data_base_tick(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/1214/territorio-saber/"
            "agrupamentos-correlacionados/?dataBaseTick=638527968000000000"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_componente=1214,
            data_base_tick=638527968000000000,
        )


class AgrupamentosCorrelacionadosLoteViewSetTest(SimpleTestCase):
    """Valida a view de agrupamentos correlacionados em lote."""

    @patch("apps.pedagogico.views.services.post_agrupamentos_correlacionados")
    def test_200_repassa_ids(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos-correlacionados/",
            [1214, 1236],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ids=[1214, 1236],
            data_base_tick=None,
        )

    @patch("apps.pedagogico.views.services.post_agrupamentos_correlacionados")
    def test_200_com_data_base_tick(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/"
            "agrupamentos-correlacionados/?dataBaseTick=638527968000000000",
            [1214],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ids=[1214],
            data_base_tick=638527968000000000,
        )

    @patch("apps.pedagogico.views.services.post_agrupamentos_correlacionados")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos-correlacionados/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()

    @patch("apps.pedagogico.views.services.post_agrupamentos_correlacionados")
    def test_400_quando_payload_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos-correlacionados/",
            [1214, "abc"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()


class AgrupamentosTerritorioViewSetTest(SimpleTestCase):
    """Valida a view de agrupamentos de Território do Saber por IDs."""

    @patch("apps.pedagogico.views.services.post_agrupamentos_territorio")
    def test_200_repassa_ids(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos/",
            [1214, 1236],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["codigo"], 9001)
        mock_svc.assert_called_once_with(ids=[1214, 1236])

    @patch("apps.pedagogico.views.services.post_agrupamentos_territorio")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()

    @patch("apps.pedagogico.views.services.post_agrupamentos_territorio")
    def test_400_quando_payload_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos/",
            ["abc"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()
