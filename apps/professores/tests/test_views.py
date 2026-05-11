"""Testes das views do domínio professores."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


class _UsuarioAutenticado:
    is_authenticated = True


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=_UsuarioAutenticado())
    return client


class ProfessoresUrlsTest(SimpleTestCase):
    """Testes dos nomes dos parametros nas rotas."""

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


class ProfessorViewTest(SimpleTestCase):
    """Testes de GET /api/professores/{rf_professor}/."""

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
    """Testes de GET /api/professores/{codigo_rf}/validade/."""

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
    """Testes de GET /api/acessos/funcionario-ativo/{registro_funcional}/."""

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
    """Testes de GET /api/funcionarios/nome-servidor/{registro_funcional}/."""

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
