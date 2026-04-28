"""Cliente HTTP base com circuit breaker, retry e X-Request-ID."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import pybreaker
from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("gateway_apps")


def _make_breaker(dominio: str) -> pybreaker.CircuitBreaker:
    return pybreaker.CircuitBreaker(
        fail_max=settings.GATEWAY_CIRCUIT_BREAKER_FAIL_MAX,
        reset_timeout=settings.GATEWAY_CIRCUIT_BREAKER_RESET_TIMEOUT,
        name=f"cb_{dominio}",
    )


class SidecarClient:
    """Circuit breaker e retry por instância — falhas de domínios são isoladas."""

    def __init__(self, base_url: str, dominio: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.dominio = dominio
        self._breaker = _make_breaker(dominio)
        self._timeout = settings.GATEWAY_TIMEOUT_SECONDS
        self._max_attempts = settings.GATEWAY_RETRY_MAX_ATTEMPTS

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> httpx.Response:
        return self._breaker.call(
            self._get_with_retry, path, params, request_id
        )

    def post(
        self,
        path: str,
        payload: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> httpx.Response:
        return self._breaker.call(
            self._post_with_retry, path, payload, request_id
        )

    def _get_with_retry(
        self,
        path: str,
        params: dict[str, Any] | None,
        request_id: str | None,
    ) -> httpx.Response:
        @retry(
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=True,
        )
        def _execute() -> httpx.Response:
            headers = self._build_headers(request_id)
            url = f"{self.base_url}{path}"
            logger.debug("[%s] GET %s", self.dominio, url)
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response

        return _execute()

    def _post_with_retry(
        self,
        path: str,
        payload: dict[str, Any] | None,
        request_id: str | None,
    ) -> httpx.Response:
        @retry(
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=True,
        )
        def _execute() -> httpx.Response:
            headers = self._build_headers(request_id)
            url = f"{self.base_url}{path}"
            logger.debug("[%s] POST %s", self.dominio, url)
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response

        return _execute()

    def _build_headers(self, request_id: str | None) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if request_id:
            headers["X-Request-ID"] = request_id
        return headers

    def is_healthy(self) -> bool:
        """Sonda sem passar pelo circuit breaker para não contaminar estado."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base_url}/health/")
                return response.status_code < 500
        except Exception:
            return False
