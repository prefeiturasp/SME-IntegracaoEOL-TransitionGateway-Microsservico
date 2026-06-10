"""Valida os serviços do domínio de matrículas."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.matriculas import services

_BASE = "/api/v1/alunos/matriculas"


class GetMatriculasAnoAtualTest(SimpleTestCase):
    """Valida a consulta de matrículas do ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_params_corretos(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"turma_codigo": "9001", "quantidade": 35}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_matriculas_ano_atual(
            ano_letivo=2026,
            ue_codigo="100001",
        )

        mock_get.assert_called_once_with(
            _BASE,
            params={"ano_letivo": 2026, "ue_codigo": "100001"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)
