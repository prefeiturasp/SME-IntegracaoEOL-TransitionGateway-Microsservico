"""Valida os serviços do domínio de alunos."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.alunos import services

_BASE = "/api/v1/alunos"


class GetInformacoesAlunoTest(SimpleTestCase):
    """Valida a consulta de informações do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de informações do aluno."""
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
        """Valida retorno None quando a consulta responde com status 204."""
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
        """Valida a consulta de necessidades especiais do aluno."""
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


class BuscarAlunosAtivosAutocompleteTest(SimpleTestCase):
    """Valida a consulta de autocomplete de alunos ativos."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_params_corretos(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"codigo_aluno": 123456, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.buscar_alunos_ativos_autocomplete(
            ue_codigo="100001",
            aluno_nome="Fulano",
            data_referencia=datetime(2026, 2, 3, 10, 0, 0),
            aluno_codigo=0,
            limite=5,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/autocomplete/ativos",
            params={
                "aluno_codigo": 0,
                "limite": 5,
                "aluno_nome": "Fulano",
                "data_referencia": "2026-02-03T10:00:00",
            },
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_omite_params_opcionais_vazios(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = services.buscar_alunos_ativos_autocomplete(
            ue_codigo="100001",
            aluno_nome=None,
            data_referencia=None,
            aluno_codigo=123456,
            limite=10,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/autocomplete/ativos",
            params={"aluno_codigo": 123456, "limite": 10},
        )
        self.assertEqual(result, [])


class GetResponsavelResumidoTest(SimpleTestCase):
    """Valida a consulta de dados resumidos do responsável."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"cpf": "12345678900", "codigo_aluno": "123456"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_responsavel_resumido("12345678900")

        mock_get.assert_called_once_with(
            f"{_BASE}/responsaveis/12345678900/resumido"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetInformacoesAlunosTurmaTest(SimpleTestCase):
    """Valida a consulta de informações dos alunos da turma."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_aluno": 123456, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_informacoes_alunos_turma("9001")

        mock_get.assert_called_once_with(f"{_BASE}/9001/turma/informacoes")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_sem_corpo(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_informacoes_alunos_turma("9001")

        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [])


class GetTurmasAlunoTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de turmas do aluno."""
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


class GetTurmasAlunoComProgramaTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno incluindo programa."""

    @patch.object(services._client, "get")
    def test_chama_turmas_com_filtros_desativados(
        self, mock_get: MagicMock
    ) -> None:
        """Valida a consulta com filtros de tipo e situação desativados."""
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("123456")

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/turmas/",
            params={"tipo_turma": "false", "filtrar_situacao": "false"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_codigo_invalido_retorna_lista_vazia(
        self, mock_get: MagicMock
    ) -> None:
        """Sidecar 400 (ex.: "00000") vira lista vazia, sem propagar erro."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("00000")

        self.assertEqual(result, [])
        mock_resp.raise_for_status.assert_not_called()

    @patch.object(services._client, "get")
    def test_aluno_sem_turmas_retorna_lista_vazia(
        self, mock_get: MagicMock
    ) -> None:
        """Sidecar 404 (aluno sem turmas) vira lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("123456")

        self.assertEqual(result, [])
        mock_resp.raise_for_status.assert_not_called()


class ListarAlunosTest(SimpleTestCase):
    """Valida a consulta de listagem de alunos."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de listagem de alunos."""
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
