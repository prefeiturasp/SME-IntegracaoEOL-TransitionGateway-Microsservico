"""Testes das funções de service do domínio professores."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.professores import services


class GetProfessorTest(SimpleTestCase):
    """Testes de services.get_professor."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigoRf":"123456","nome":"Fulano de Tal"}'
        mock_resp.json.return_value = {
            "codigoRf": "123456",
            "nome": "Fulano de Tal",
        }
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        mock_get.assert_called_once_with("/api/v1/professores/123456")
        self.assertEqual(result, "Fulano de Tal")

    @patch.object(services._client, "get")
    def test_retorna_texto_quando_sidecar_envia_string(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'"Fulano de Tal"'
        mock_resp.json.return_value = "Fulano de Tal"
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertEqual(result, "Fulano de Tal")

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertIsNone(result)

    @patch.object(services._client, "get")
    def test_retorna_texto_quando_resposta_nao_tem_json(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html></html>"
        mock_resp.json.side_effect = ValueError("sem json")
        mock_resp.text = "<html></html>"
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertEqual(result, "<html></html>")


class GetValidadeProfessorTest(SimpleTestCase):
    """Testes de services.get_validade_professor."""

    @patch("apps.professores.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = True
        mock_client.get.return_value = mock_resp

        result = services.get_validade_professor("123456")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/123456/validade"
        )
        self.assertTrue(result)


class GetFuncionarioAtivoTest(SimpleTestCase):
    """Testes de services.get_funcionario_ativo."""

    @patch("apps.professores.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = True
        mock_client.get.return_value = mock_resp

        result = services.get_funcionario_ativo("RF001")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/acessos/funcionario-ativo/RF001"
        )
        self.assertTrue(result)


class GetNomeServidorTest(SimpleTestCase):
    """Testes de services.get_nome_servidor."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"nome": "Maria", "cpf": "000.000.000-00"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"nome": "Maria", "cpf": "000.000.000-00"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_nome_servidor("RF001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/nome-servidor/RF001"
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_nome_servidor("RF001")

        self.assertIsNone(result)
