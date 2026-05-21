from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.institucional import services

_BASE = "/api/v1/institucional"


class GetDREsTest(SimpleTestCase):
    @patch("apps.institucional.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_dres()

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/")
        self.assertEqual(result, [])


class GetDRETest(SimpleTestCase):
    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [{"codigoDRE": "BT"}]

        result = services.get_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/")
        self.assertEqual(result[0]["codigoDRE"], "BT")


class GetEscolasPorDRETest(SimpleTestCase):
    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_escolas_por_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/escola/")
        self.assertEqual(result, [])


class GetEscolaTest(SimpleTestCase):
    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_escola(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "codigoEscola": "019308"
        }

        result = services.get_escola("019308")

        mock_client.get.assert_called_once_with(f"{_BASE}/escolas/019308/")
        self.assertEqual(result["codigoEscola"], "019308")


class GetEquipamentosTest(SimpleTestCase):
    @patch("apps.institucional.services._client")
    def test_sem_filtros_nao_passa_params(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_equipamentos()

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/", params=None
        )
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_com_codigo_eol_passa_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoEol": "019716"}
        ]

        result = services.get_equipamentos(codigo_eol="019716")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/", params={"codigoEol": "019716"}
        )
        self.assertEqual(result[0]["codigoEol"], "019716")

    @patch("apps.institucional.services._client")
    def test_com_multiplos_filtros(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        services.get_equipamentos(tipos_escola=["1", "2"], tipos_unidade=["1"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/",
            params={"tiposEscola": ["1", "2"], "tiposUnidade": ["1"]},
        )
