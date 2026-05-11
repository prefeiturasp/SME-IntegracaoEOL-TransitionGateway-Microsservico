"""Testes das funções de service do domínio pedagógico."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.pedagogico import services

_BASE = "/api/v1/pedagogico/componentes-curriculares"


class GetComponentesUeAnosTest(SimpleTestCase):
    """Testes de services.get_componentes_ue_anos."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_ue_anos(
            "UE001",
            5,
            2024,
            ["1", "2"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024",
            params={"anosEscolares": ["1", "2"]},
        )

        self.assertEqual(result, [])


class GetComponentesTurmasProgramaTest(SimpleTestCase):
    """Testes de services.get_componentes_turmas_programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_turmas_programa(
            "UE001",
            5,
            2024,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024/turmas-programa"
        )

        self.assertEqual(result, [])


class GetComponentesPorTurmasUeTest(SimpleTestCase):
    """Testes de services.get_componentes_por_turmas_ue."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_por_turmas_ue(
            "UE001",
            ["T001", "T002"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/turmas",
            params={"turmas": ["T001", "T002"]},
        )

        self.assertEqual(result, [])


class GetCatalogoComponentesTest(SimpleTestCase):
    """Testes de services.get_componentes_curriculares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_base_sem_params(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_curriculares()

        mock_client.get.assert_called_once_with(_BASE)

        self.assertEqual(result, [])


class GetGradeCurricularTest(SimpleTestCase):
    """Testes de services.get_grade_curricular."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_grade_curricular(2024)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/grade-curricular/2024"
        )

        self.assertEqual(result, [])
