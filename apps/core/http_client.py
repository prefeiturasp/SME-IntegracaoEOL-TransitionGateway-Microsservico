"""Comunicação HTTP com serviços externos."""

from __future__ import annotations

from typing import Any

import httpx
from sme_sidecar_sdk.config import get_settings
from sme_sidecar_sdk.resilience.timeout import build_sync_client


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
        self._client: httpx.Client | None = None

    def _http_client(self) -> httpx.Client:
        """Retorna o cliente HTTP persistente.

        Returns:
            Cliente HTTP configurado com timeout e keep-alive.
        """
        if self._client is None:
            self._client = build_sync_client(
                get_settings(),
                follow_redirects=True,
            )
        return self._client

    def _headers(self) -> dict[str, str]:
        """Monta os headers padrão da requisição.

        Returns:
            Headers com Accept, X-Request-ID e API Key quando disponíveis.
        """
        headers = {"Accept": "application/json"}
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

        Raises:
            httpx.HTTPError: Em caso de falha de transporte ou timeout.
        """
        return self._http_client().get(
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
        """Executa uma requisição POST.

        Args:
            path: Caminho relativo da requisição.
            payload: Corpo JSON enviado na requisição.
            params: Parâmetros de query enviados na requisição.

        Returns:
            Resposta HTTP recebida do serviço externo.

        Raises:
            httpx.HTTPError: Em caso de falha de transporte ou timeout.
        """
        return self._http_client().post(
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=payload,
            params=params,
        )

    def put(
        self,
        path: str,
        payload: dict | list | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        """Executa uma requisição PUT.

        Args:
            path: Caminho relativo da requisição.
            payload: Corpo JSON enviado na requisição.
            params: Parâmetros de query enviados na requisição.

        Returns:
            Resposta HTTP recebida do serviço externo.

        Raises:
            httpx.HTTPError: Em caso de falha de transporte ou timeout.
        """
        return self._http_client().put(
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=payload,
            params=params,
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
            response = self._http_client().get(
                f"{self.base_url}/health/",
                headers=self._headers(),
            )
            return response.status_code < 500
        except Exception:
            return False

    def close(self) -> None:
        """Fecha conexões HTTP mantidas pelo cliente."""
        if self._client is not None:
            self._client.close()
            self._client = None
