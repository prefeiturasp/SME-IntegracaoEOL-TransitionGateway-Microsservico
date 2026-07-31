"""Bases de views reutilizáveis entre domínios."""

from typing import cast

import httpx
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.responses import api_unavailable_response


class DomainAPIView(APIView):
    """APIView base para APIs de domínio chamadas pelo gateway."""

    api_domain: str = ""

    def handle_exception(self, exc: Exception) -> Response:
        """Converta falhas de transporte da API de domínio em 503."""
        if isinstance(exc, httpx.RequestError):
            return api_unavailable_response(self.api_domain)
        return cast(Response, super().handle_exception(exc))
