from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/v1/componentes-curriculares"


_CC: dict[str, Any] = {
    "codigo": 1,
    "codigoComponenteTerritorioSaber": None,
    "codigoComponenteCurricularPai": None,
    "descricao": "Matematica",
    "regencia": False,
    "planejamentoRegencia": False,
    "territorioSaber": False,
    "turmaCodigo": None,
    "exibirComponenteEOL": True,
    "professor": None,
    "codigosTerritoriosAgrupamento": [],
}

_BASE_CC = {"codigo": 1, "descricao": "Matematica"}

_GRADE = {
    "codigoComponenteCurricular": 1,
    "descricaoComponenteCurricular": "Matematica",
    "codigoAnoTurma": "1",
    "descricaoSerieEnsino": "1o Ano",
    "codigoSerieEnsino": 1,
    "modalidade": 5,
}


def _cliente_autenticado() -> APIClient:
    client = APIClient()

    user = User(username="teste")
    client.force_authenticate(user=user)

    return client


class ComponentesTurmaViewSetTest(SimpleTestCase):
    @patch("apps.pedagogico.views.services" ".get_componentes_por_turmas_ue")
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
    @patch("apps.pedagogico.views.services.get_componentes_curriculares")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()


class GradeComponentesCurricularesViewSetTest(SimpleTestCase):
    @patch("apps.pedagogico.views.services.get_grade_curricular")
    def test_200_retorna_grade(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_GRADE]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ano-turma/ano-letivo/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(2024)


class ComponentesTurmaAnoViewSetTest(SimpleTestCase):
    @patch("apps.pedagogico.views.services.get_componentes_ue_anos")
    def test_200_repassa_anos_escolares(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024"
            "/anos-escolares/?anosEscolares=1&anosEscolares=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
            anos_escolares=["1", "2"],
        )


class ComponentesTurmaProgramaViewSetTest(SimpleTestCase):
    @patch("apps.pedagogico.views.services" ".get_componentes_turmas_programa")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
        )
