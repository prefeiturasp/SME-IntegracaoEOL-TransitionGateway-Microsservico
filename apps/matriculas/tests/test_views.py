"""Valida as views do domínio de matrículas."""

from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


def _request_error() -> httpx.RequestError:
    request = httpx.Request("GET", "https://sidecar.local/test")
    return httpx.ConnectError("Sidecar indisponivel", request=request)


class MatriculasUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_rota_matriculas(self) -> None:
        match = resolve("/api/v1/matriculas/")

        self.assertEqual(match.kwargs, {})


class MatriculasAnoAtualViewTest(SimpleTestCase):
    """Valida a view de matrículas do ano letivo."""

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_retorna_matriculas_com_camel_case(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {"turma_codigo": "9001", "quantidade": 35}
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [{"turmaCodigo": "9001", "quantidade": 35}],
        )
        mock_service.assert_called_once_with(
            ano_letivo=2026,
            ue_codigo="100001",
        )

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_aceita_query_params_snake_case(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/?ano_letivo=2026&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            ano_letivo=2026,
            ue_codigo="100001",
        )

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_400_quando_ano_letivo_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "ano_letivo e ue_codigo são obrigatórios."},
        )
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_400_quando_ue_codigo_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "ano_letivo e ue_codigo são obrigatórios."},
        )
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_400_quando_ano_letivo_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=abc&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "ano_letivo deve ser um inteiro válido."},
        )
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de matriculas indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
