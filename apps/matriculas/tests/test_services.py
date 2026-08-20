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


class GetMatriculasAnosAnterioresTest(SimpleTestCase):
    """Valida a consulta de matrículas históricas."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_params_corretos(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"turma_codigo": "9001", "quantidade": 35}]
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_matriculas_anos_anteriores(
            ano_letivo=2025,
            ue_codigo="100001",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/anos-anteriores",
            params={"ano_letivo": 2025, "ue_codigo": "100001"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTotalMatriculasPorTurnoUeTest(SimpleTestCase):
    """Valida a consulta de totais de matrículas por turno na UE."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_path_correto(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"turno": "MANHA", "quantidade": 125}]
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_total_matriculas_por_turno_ue("100001")

        mock_get.assert_called_once_with(
            f"{_BASE}/escolas/100001/quantidades"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTotalMatriculasPorTurnoDreTest(SimpleTestCase):
    """Valida a consulta de totais de matrículas por turno na DRE."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_path_correto(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"turno": "TARDE", "quantidade": 300}]
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_total_matriculas_por_turno_dre("100000")

        mock_get.assert_called_once_with(
            f"{_BASE}/escolas/dre/100000/quantidades"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetQuantidadeAlunosPorTurmaEscolaTest(SimpleTestCase):
    """Valida a consulta de quantidade de alunos por turma na escola."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_path_correto(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"turma_codigo": "9001", "quantidade": 35}]
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_quantidade_alunos_por_turma_escola("100001")

        mock_get.assert_called_once_with(
            "/api/v1/alunos/escolas/100001/alunos/quantidade"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetMatriculasAlunoEscolaTest(SimpleTestCase):
    """Valida a consulta de matrículas de aluno na escola."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_path_correto(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"codigo_matricula": 998877, "codigo_aluno": 1234567}]
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_matriculas_aluno_escola("100001", "1234567")

        mock_get.assert_called_once_with(
            "/api/v1/alunos/escolas/100001/aluno/1234567/matriculas"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)
