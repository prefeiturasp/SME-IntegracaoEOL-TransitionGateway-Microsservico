"""Valida as views do domínio de professores."""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


class ProfessoresUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_preserva_rf_professor(self) -> None:
        match = resolve("/api/professores/123456/")

        self.assertEqual(match.kwargs, {"rf_professor": "123456"})

    def test_preserva_codigo_rf(self) -> None:
        match = resolve("/api/professores/123456/validade/")

        self.assertEqual(match.kwargs, {"codigo_rf": "123456"})

    def test_preserva_registro_funcional_funcionario_ativo(self) -> None:
        match = resolve("/api/acessos/funcionario-ativo/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_registro_funcional_nome_servidor(self) -> None:
        match = resolve("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_registro_funcional_nome_usuario_eol(self) -> None:
        match = resolve("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_codigo_rf_e_ano_letivo_buscar_por_rf(self) -> None:
        match = resolve("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "ano_letivo": 2026},
        )

    def test_resolve_funcionarios_buscar_por_lista_rf(self) -> None:
        match = resolve("/api/funcionarios/BuscarPorListaRF/")

        self.assertEqual(match.kwargs, {})

    def test_preserva_codigo_ue_funcionarios_escola(self) -> None:
        match = resolve("/api/escolas/000123/funcionarios/")

        self.assertEqual(match.kwargs, {"codigo_ue": "000123"})

    def test_preserva_codigo_ue_e_cargo_funcionarios_escola(self) -> None:
        match = resolve("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(
            match.kwargs,
            {"codigo_ue": "000123", "codigo_cargo": "14"},
        )

    def test_preserva_professor_disciplina_turmas(self) -> None:
        match = resolve("/api/professores/000001/disciplina/5/turmas")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "disciplina_id": "5"},
        )


class ProfessorViewTest(SimpleTestCase):
    """Valida a resposta da view de professor."""

    @patch("apps.professores.views.services.get_professor")
    def test_200_retorna_nome(self, mock_service: MagicMock) -> None:
        mock_service.return_value = "Fulano de Tal"
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), "Fulano de Tal")
        mock_service.assert_called_once_with("123456")

    @patch("apps.professores.views.services.get_professor")
    def test_204_quando_professor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), {"detail": "Codigo RF e obrigatorio."})


class ValidadeProfessorViewTest(SimpleTestCase):
    """Valida a resposta da view de validade do professor."""

    @patch("apps.professores.views.services.get_validade_professor")
    def test_200_retorna_booleano(self, mock_service: MagicMock) -> None:
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/validade/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.json())
        mock_service.assert_called_once_with("123456")

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/validade/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoRF."},
        )


class FuncionarioAtivoViewTest(SimpleTestCase):
    """Valida a resposta da view de funcionário ativo."""

    @patch("apps.professores.views.services.get_funcionario_ativo")
    def test_200_retorna_booleano(self, mock_service: MagicMock) -> None:
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get("/api/acessos/funcionario-ativo/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.json())
        mock_service.assert_called_once_with("RF001")

    def test_400_quando_registro_funcional_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/acessos/funcionario-ativo/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o registro funcional."},
        )


class NomeServidorViewTest(SimpleTestCase):
    """Valida a resposta da view de nome do servidor."""

    @patch("apps.professores.views.services.get_nome_servidor")
    def test_200_retorna_nome_e_cpf(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {
            "nome": "Maria Silva",
            "cpf": "000.000.000-00",
        }
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["nome"], "Maria Silva")
        self.assertEqual(data["cpf"], "000.000.000-00")
        mock_service.assert_called_once_with("RF001")

    @patch("apps.professores.views.services.get_nome_servidor")
    def test_204_quando_servidor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class NomeUsuarioEolViewTest(SimpleTestCase):
    """Valida a resposta da view de nome de usuário EOL."""

    @patch("apps.professores.views.services.get_nome_usuario_eol")
    def test_200_retorna_nome_usuario_eol(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "NOME USUARIO EOL"
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), "NOME USUARIO EOL")
        mock_service.assert_called_once_with("RF001")

    @patch("apps.professores.views.services.get_nome_usuario_eol")
    def test_204_quando_usuario_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_registro_funcional_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o registro funcional."},
        )


class ProfessorBuscarPorRfViewTest(SimpleTestCase):
    """Valida a busca de professor por RF e ano letivo."""

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_retorna_professor(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {"codigoRF": "000001", "nome": "NOME PROFESSOR"},
        )
        mock_service.assert_called_once_with("000001", 2026, None)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_repassa_buscar_outros_cargos(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=true"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with("000001", 2026, True)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_repassa_buscar_outros_cargos_false(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=false"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with("000001", 2026, False)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_204_quando_professor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoRF."},
        )

    def test_400_quando_buscar_outros_cargos_invalido(self) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=sim"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "buscar_outros_cargos deve ser booleano."},
        )


class FuncionariosBuscarPorListaRfViewTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF."""

    @patch("apps.professores.views.services.get_professores_por_lista_rf")
    def test_200_retorna_professores(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {"codigo_rf": "000001", "nome": "NOME PROFESSOR"},
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [{"codigoRF": "000001", "nome": "NOME PROFESSOR"}],
        )
        mock_service.assert_called_once_with(["000001"])

    @patch("apps.professores.views.services.get_professores_por_lista_rf")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_lista_vazia(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_quando_item_nao_e_texto(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001", 123],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class EscolaFuncionariosViewTest(SimpleTestCase):
    """Valida a busca de funcionários por escola."""

    @patch("apps.professores.views.services.get_funcionarios_escola")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "cd_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        self.assertEqual(resp.json()[0]["nomeServidor"], "NOME SERVIDOR")
        self.assertIsNone(resp.json()[0]["cargo"])
        mock_service.assert_called_once_with("000123")

    @patch("apps.professores.views.services.get_funcionarios_escola")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoUE."},
        )


class EscolaFuncionariosCargoViewTest(SimpleTestCase):
    """Valida a busca de funcionários por escola e cargo."""

    @patch("apps.professores.views.services.get_funcionarios_escola_por_cargo")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "cd_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        mock_service.assert_called_once_with("000123", "14")

    def test_400_quando_codigo_cargo_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoCargo."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoUE."},
        )

    @patch("apps.professores.views.services.get_funcionarios_escola_por_cargo")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class ProfessorDisciplinaTurmasViewTest(SimpleTestCase):
    """Valida a busca de turmas por professor e disciplina."""

    @patch("apps.professores.views.services.get_turmas_professor_disciplina")
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_turma": "3030050",
                "data_disponibilizacao_aulas": "2026-12-22T00:00:00",
                "data_atribuicao_aula": "2026-03-30T00:00:00",
            },
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoTurma"], "3030050")
        mock_service.assert_called_once_with("000001", "5", ["3030050"])

    @patch("apps.professores.views.services.get_turmas_professor_disciplina")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_lista_vazia(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/%20/disciplina/5/turmas",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar o codigoRF."},
        )

    def test_400_quando_disciplina_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/%20/turmas",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "E necessario informar a disciplina."},
        )
