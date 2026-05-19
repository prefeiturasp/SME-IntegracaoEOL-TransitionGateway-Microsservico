"""Comunicação HTTP com serviços externos."""

from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings

from apps.core.logging_context import get_request_id


class ServiceClient:
    """Executa chamadas HTTP para serviços externos.

    Args:
        base_url: URL base do serviço externo.
        dominio: Nome do domínio associado ao cliente.
        api_key: Chave de autenticação enviada ao serviço externo.
        api_key_header: Nome do header usado para enviar a chave.
    """

    def __init__(
        self,
        base_url: str,
        dominio: str,
        api_key: str = "",
        api_key_header: str = "X-API-Key",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.dominio = dominio
        self._api_key = api_key
        self._api_key_header = api_key_header

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        request_id = get_request_id()
        if request_id:
            headers["X-Request-ID"] = request_id
        if self._api_key:
            headers[self._api_key_header] = self._api_key
        return headers

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        """Executa uma requisição GET.

        Args:
            path: Caminho relativo da requisição.
            params: Parâmetros de query enviados na requisição.

        Returns:
            Resposta HTTP recebida do serviço externo.
        """
        with httpx.Client(timeout=settings.GATEWAY_TIMEOUT_SECONDS) as client:
            return client.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                params=params,
                follow_redirects=True,
            )

    def post(
        self,
        path: str,
        payload: dict | list | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        """Executa uma requisição POST.

        Args:
            path: Caminho relativo da requisição.
            payload: Corpo JSON enviado na requisição.
            params: Parâmetros de query enviados na requisição.

        Returns:
            Resposta HTTP recebida do serviço externo.
        """
        with httpx.Client(timeout=settings.GATEWAY_TIMEOUT_SECONDS) as client:
            return client.post(
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=payload,
                params=params,
                follow_redirects=True,
            )

    def json_or_none(self, resp: httpx.Response) -> Any:
        """Retorna JSON ou None para respostas sem conteúdo.

        Args:
            resp: Resposta HTTP que será convertida.

        Returns:
            Corpo da resposta como JSON, texto ou `None`.
        """
        if resp.status_code == 204 or not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text.strip() or None

    def is_healthy(self) -> bool:
        """Verifica se o serviço externo responde ao health check.

        Returns:
            `True` quando o serviço responde sem erro de servidor.
        """
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
