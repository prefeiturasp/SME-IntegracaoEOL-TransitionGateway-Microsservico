"""Valida os serviços do domínio de professores."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.professores import services


class GetProfessorTest(SimpleTestCase):
    """Valida a extração do nome do professor."""

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
    """Valida a consulta de validade do professor."""

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
    """Valida a consulta de funcionário ativo."""

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
    """Valida a consulta de nome do servidor."""

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


class GetNomeUsuarioEolTest(SimpleTestCase):
    """Valida a consulta de nome de usuário EOL."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'"NOME USUARIO EOL"'
        mock_resp.json.return_value = "NOME USUARIO EOL"
        mock_get.return_value = mock_resp

        result = services.get_nome_usuario_eol("RF001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/nome-usuario-eol/RF001"
        )
        self.assertEqual(result, "NOME USUARIO EOL")

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_nome_usuario_eol("RF001")

        self.assertIsNone(result)


class GetProfessorPorRfTest(SimpleTestCase):
    """Valida a busca de professor por RF e ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf("000001", 2026)

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRf/2026"
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_chama_path_com_buscar_outros_cargos(
        self, mock_get: MagicMock
    ) -> None:
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf("000001", 2026, True)

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRf/2026",
            params={"buscar_outros_cargos": True},
        )
        self.assertEqual(result, payload)


class GetProfessoresPorListaRfTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [{"codigo_rf": "000001", "nome": "NOME PROFESSOR"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'[{"codigo_rf":"000001","nome":"NOME"}]'
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_professores_por_lista_rf(["000001"])

        mock_post.assert_called_once_with(
            "/api/v1/professores/funcionarios/BuscarPorListaRF/",
            payload=["000001"],
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaTest(SimpleTestCase):
    """Valida a busca de funcionários por escola."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "cd_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola("000123")

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios"
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaPorCargoTest(SimpleTestCase):
    """Valida a busca de funcionários por escola e cargo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "cd_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_cargo("000123", "14")

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios/cargos/14"
        )
        self.assertEqual(result, payload)


class GetTurmasProfessorDisciplinaTest(SimpleTestCase):
    """Valida a busca de turmas por professor e disciplina."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "codigo_turma": "3030050",
                "data_disponibilizacao_aulas": "2026-12-22T00:00:00",
                "data_atribuicao_aula": "2026-03-30T00:00:00",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_turmas_professor_disciplina(
            "000001",
            "5",
            ["3030050"],
        )

        mock_post.assert_called_once_with(
            "/api/v1/professores/000001/disciplina/5/turmas",
            payload=["3030050"],
        )
        self.assertEqual(result, payload)
