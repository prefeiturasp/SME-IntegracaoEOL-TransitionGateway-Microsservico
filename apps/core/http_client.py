"""Comunicação HTTP do gateway com os sidecars."""

from __future__ import annotations

import httpx
from django.conf import settings

from apps.core.logging_context import get_request_id


class ServiceClient:
    """Cliente HTTP do gateway — timeout simples, sem retry nem breaker.

    Resiliência é responsabilidade do sidecar de cada domínio.
    O gateway interpreta 502/503 do sidecar para degradação parcial.
    """

    def __init__(self, base_url: str, dominio: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.dominio = dominio

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        request_id = get_request_id()
        if request_id:
            headers["X-Request-ID"] = request_id
        return headers

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        with httpx.Client(timeout=settings.GATEWAY_TIMEOUT_SECONDS) as client:
            return client.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                params=params,
            )

    def post(
        self,
        path: str,
        payload: dict | list | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        with httpx.Client(timeout=settings.GATEWAY_TIMEOUT_SECONDS) as client:
            return client.post(
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=payload,
                params=params,
            )

    def is_healthy(self) -> bool:
        try:
            timeout = settings.GATEWAY_TIMEOUT_SECONDS
            with httpx.Client(timeout=timeout) as client:
                response = client.get(
                    f"{self.base_url}/health/",
                    headers=self._headers(),
                )
                return response.status_code < 500
        except Exception:
            return False
