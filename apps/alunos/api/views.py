import logging

import pybreaker
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from tenacity import RetryError

from apps.core.api.serializers import HealthStatusSerializer
from apps.alunos.libs.gateway_client import get_client

logger = logging.getLogger("gateway_apps")


class HealthAlunosView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    serializer_class = HealthStatusSerializer

    def get(self, request: Request) -> Response:
        client = get_client()
        saudavel = client.is_healthy()
        serializer = HealthStatusSerializer(
            {
                "status": "healthy" if saudavel else "unhealthy",
                "dominio": "alunos",
                "sidecar_url": client.base_url,
            }
        )
        return Response(serializer.data, status=200 if saudavel else 503)


class AlunosProxyView(APIView):
    def get(self, request: Request, path: str = "") -> Response:
        request_id = request.headers.get("X-Request-ID")
        client = get_client()
        try:
            response = client.get(
                f"/{path}",
                params=dict(request.query_params),
                request_id=request_id,
            )
            return Response(response.json(), status=response.status_code)
        except pybreaker.CircuitBreakerError:
            logger.error("[alunos] Circuit breaker aberto")
            return Response(
                {"erro": "Serviço alunos temporariamente indisponível"},
                status=503,
            )
        except (RetryError, Exception) as exc:
            logger.error("[alunos] Falha na comunicação: %s", exc)
            return Response(
                {"erro": "Erro de comunicação com o sidecar"}, status=502
            )
