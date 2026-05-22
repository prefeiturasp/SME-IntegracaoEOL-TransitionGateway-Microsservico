"""Valida os serviços do domínio de programas educacionais."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.programasedu import services


class ListarTurmasPapTest(SimpleTestCase):
    """Valida a consulta de turmas PAP."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de turmas PAP."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"codigoTurma": "X", "turmaNome": "1A"}]
        mock_get.return_value = mock_resp

        result = services.listar_turmas_pap(
            ano_letivo=2026, codigo_escola="123"
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/turmas-pap/2026/ues/123"
        )
        self.assertEqual(result, [{"codigoTurma": "X", "turmaNome": "1A"}])


class VerificarAlunosPapTest(SimpleTestCase):
    """Valida a verificação de alunos em turmas PAP."""

    @patch.object(services._client, "get")
    def test_propaga_codigos_alunos(self, mock_get: MagicMock) -> None:
        """Verifica que os codigos dos alunos sao enviados como parametro."""
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
    """Valida a consulta de alunos PAP do ano corrente."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de alunos PAP do ano corrente."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_ano_corrente()

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-corrente"
        )


class ListarAlunosPapPorAnoTest(SimpleTestCase):
    """Valida a consulta de alunos PAP por ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de alunos PAP por ano letivo."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_por_ano(ano_letivo=2026)

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-letivo/2026"
        )


class ListarComponentesTurmasProgramaAlunoTest(SimpleTestCase):
    """Valida a consulta de componentes das turmas de programa do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de componentes do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="123", ano_letivo=2026
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/123/turmas-programa/2026"
            "/componentes-curriculares"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="7410182", ano_letivo=2026
        )

        self.assertEqual(result, [])


class ObterDadosSrmPaeeAlunoTest(SimpleTestCase):
    """Valida a consulta de dados de SRM/PAEE colaborativo do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de SRM/PAEE do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.obter_dados_srm_paee_aluno(codigo_aluno="123")

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/srm-paee/aluno/123"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.obter_dados_srm_paee_aluno(codigo_aluno="7410182")

        self.assertEqual(result, [])
