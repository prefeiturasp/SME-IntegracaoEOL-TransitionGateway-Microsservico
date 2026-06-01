"""Valida os serviços do domínio de alunos."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.alunos import services

_BASE = "/api/v1/alunos"


class GetInformacoesAlunoTest(SimpleTestCase):
    """Valida a consulta de informações do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"codigo_aluno": 123456, "nome_aluno": "Fulano de Tal"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = (
            b'{"codigo_aluno": 123456, "nome_aluno": "Fulano de Tal"}'
        )
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_informacoes_aluno("123456")

        mock_get.assert_called_once_with(f"{_BASE}/123456/informacoes")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_informacoes_aluno("123456")

        mock_resp.raise_for_status.assert_called_once_with()
        self.assertIsNone(result)


class GetNecessidadesEspeciaisAlunoTest(SimpleTestCase):
    """Valida a consulta de necessidades especiais do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_aluno": 123456,
                "tipo_necessidade_especial": 10,
                "descricao_necessidade_especial": "Deficiencia Visual",
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_necessidades_especiais_aluno("123456")

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/necessidades-especiais"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTurmasAlunoTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno("123456")

        mock_get.assert_called_once_with(f"{_BASE}/123456/turmas/")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_chama_path_legado_com_filtros(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno(
            "123456",
            ano_letivo="2026",
            historico="false",
            filtrar_situacao="true",
            tipo_turma="false",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/turmas/anos_letivos/2026/"
            "historico/false/filtrar-situacao/true/tipo-turma/false"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class ListarAlunosTest(SimpleTestCase):
    """Valida a consulta de listagem de alunos."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_aluno": 1, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.listar_alunos(["1", "2"])

        mock_get.assert_called_once_with(
            f"{_BASE}/alunos",
            params={"codigos_aluno": ["1", "2"]},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)
