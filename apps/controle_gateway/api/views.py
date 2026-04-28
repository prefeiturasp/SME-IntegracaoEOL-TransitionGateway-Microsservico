from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.libs.gateway_client import SidecarClient


class GatewayHealthView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        sidecars = {
            "institucional": settings.SIDECAR_INSTITUCIONAL_URL,
            "professores": settings.SIDECAR_PROFESSORES_URL,
            "alunos": settings.SIDECAR_ALUNOS_URL,
            "pedagogico": settings.SIDECAR_PEDAGOGICO_URL,
            "programas": settings.SIDECAR_PROGRAMAS_URL,
        }

        resultado = {}
        todos_saudaveis = True

        for dominio, url in sidecars.items():
            client = SidecarClient(url, dominio)
            saudavel = client.is_healthy()
            resultado[dominio] = "healthy" if saudavel else "unhealthy"
            if not saudavel:
                todos_saudaveis = False

        status_geral = "healthy" if todos_saudaveis else "degraded"
        status_http = 200 if todos_saudaveis else 207

        return Response(
            {"status": status_geral, "dominios": resultado},
            status=status_http,
        )
