"""Testes dos endpoints de health check."""

from typing import Any
from unittest.mock import Mock, patch

import httpx
from django.test import Client, SimpleTestCase


def _response(status_code: int) -> httpx.Response:
    """Monta resposta HTTP usada nos testes.

    Args:
        status_code: Código HTTP retornado.

    Returns:
        Resposta HTTP simulada.
    """
    request = httpx.Request("GET", "https://servico/api/v1/health/")
    return httpx.Response(status_code, json={"status": "ok"}, request=request)


class GatewayHealthCheckTest(SimpleTestCase):
    """Valida health checks expostos pelo gateway."""

    def setUp(self) -> None:
        self.client = Client()

    @patch("apps.core.health.get_api_client")
    def test_health_agregado_retorna_checks(self, get_api_client: Any) -> None:
        client = Mock()
        client.get.return_value = _response(200)
        get_api_client.return_value = client

        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("checks", response.json())

    @patch("apps.core.health.get_api_client")
    def test_health_agregado_retorna_ok(self, get_api_client: Any) -> None:
        client = Mock()
        client.get.return_value = _response(200)
        get_api_client.return_value = client

        response = self.client.get("/api/v1/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(client.get.call_count, 5)

    @patch("apps.core.health.get_api_client")
    def test_health_do_dominio_retorna_degraded(
        self, get_api_client: Any
    ) -> None:
        client = Mock()
        client.get.return_value = _response(503)
        get_api_client.return_value = client

        response = self.client.get("/api/v1/health/professores/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"]["professores"]["ok"], False)

    def test_health_do_dominio_invalido_retorna_404(self) -> None:
        response = self.client.get("/api/v1/health/matriculas/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Domínio inválido."})
