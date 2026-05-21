"""Valida as views do domínio pedagógico."""

from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/v1/componentes-curriculares"


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
