from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class GatewayHealthViewTest(TestCase):
    def test_retorna_200_quando_todos_saudaveis(self) -> None:
        with patch(
            "apps.controle_gateway.api.views.SidecarClient.is_healthy",
            return_value=True,
        ):
            response = self.client.get(reverse("gateway-health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_retorna_207_quando_algum_indisponivel(self) -> None:
        with patch(
            "apps.controle_gateway.api.views.SidecarClient.is_healthy",
            return_value=False,
        ):
            response = self.client.get(reverse("gateway-health"))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(response.json()["status"], "degraded")
