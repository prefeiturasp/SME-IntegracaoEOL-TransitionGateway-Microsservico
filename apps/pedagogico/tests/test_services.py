"""Valida os serviços do domínio pedagógico."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.pedagogico import services

# Prefixo das rotas de componentes curriculares no sidecar pedagógico.
_BASE = "/api/v1/pedagogico/componentes-curriculares"


class GetComponentesUeAnosTest(SimpleTestCase):
    """Valida a consulta de componentes por anos escolares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os anos escolares como query params."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_ue_anos(
            "UE001",
            5,
            2024,
            ["1", "2"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024",
            params={"anos_escolares": ["1", "2"]},
        )

        self.assertEqual(result, [])


class GetComponentesTurmasProgramaTest(SimpleTestCase):
    """Valida a consulta de componentes de turmas programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de turmas programa por UE e modalidade."""
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


class GetComponentesRegenciaTest(SimpleTestCase):
    """Valida a consulta de componentes de regência."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_regencia(2024)

        mock_client.get.assert_called_once_with(f"{_BASE}/anos/2024/regencia")

        self.assertEqual(result, [])


class ValidarComponentePapTest(SimpleTestCase):
    """Valida a consulta de componente PAP por turma e funcionário."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = True

        result = services.validar_componente_pap("T001", "RF001", "P1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/T001/pap",
            params={"login": "RF001", "idPerfil": "P1"},
        )

        self.assertTrue(result)


class GetComponentesFuncionarioTest(SimpleTestCase):
    """Valida a consulta de componentes por funcionário."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_funcionario("RF001", "P1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/funcionarios/RF001",
            params={"idPerfil": "P1"},
        )

        self.assertEqual(result, [])


class GetComponentesPorTurmasUeTest(SimpleTestCase):
    """Valida a consulta de componentes por turmas de uma UE."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        """Monta o path e repassa as turmas como query param."""
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
    """Valida a consulta do catálogo de componentes curriculares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_base_sem_params(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Consulta o catálogo na rota base, sem query params."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_curriculares()

        mock_client.get.assert_called_once_with(_BASE)

        self.assertEqual(result, [])


class GetGradeCurricularTest(SimpleTestCase):
    """Valida a consulta da grade curricular."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Monta o path da grade curricular pelo ano letivo."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_grade_curricular(2024)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/grade-curricular/2024"
        )

        self.assertEqual(result, [])
