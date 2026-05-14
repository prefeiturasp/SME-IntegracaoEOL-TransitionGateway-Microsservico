"""Testes das funcoes de service do dominio programasedu."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.programasedu import services


class ListarTurmasPapTest(SimpleTestCase):
    """Testes de services.listar_turmas_pap."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {"codigoTurma": "X", "turmaNome": "1A"}
        ]
        mock_get.return_value = mock_resp

        result = services.listar_turmas_pap(
            ano_letivo=2026, codigo_escola="123"
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/turmas-pap/2026/ues/123"
        )
        self.assertEqual(
            result, [{"codigoTurma": "X", "turmaNome": "1A"}]
        )


class VerificarAlunosPapTest(SimpleTestCase):
    """Testes de services.verificar_alunos_pap."""

    @patch.object(services._client, "get")
    def test_propaga_codigos_alunos(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.verificar_alunos_pap(
            ano_letivo=2026, codigos_alunos=["1", "2"]
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/alunos-pap/2026",
            params={"codigos_alunos": ["1", "2"]},
        )


class ListarAlunosPapAnoCorrenteTest(SimpleTestCase):
    """Testes de services.listar_alunos_pap_ano_corrente."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_ano_corrente()

        mock_get.assert_called_once_with("/api/v1/programasedu/alunos/pap/ano-corrente")


class ListarAlunosPapPorAnoTest(SimpleTestCase):
    """Testes de services.listar_alunos_pap_por_ano."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_por_ano(ano_letivo=2026)

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-letivo/2026"
        )
