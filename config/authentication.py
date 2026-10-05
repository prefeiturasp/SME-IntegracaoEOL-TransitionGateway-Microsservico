"""Autenticação por API Key usada pelo MSC."""

from typing import Any

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class _ApiKeyUser:
    is_authenticated = True


class ApiKeyAuthentication(BaseAuthentication):
    """Autentica requisições via API Key no header configurado."""

    def authenticate(self, request: Request) -> tuple | None:
        """Autentica a requisição a partir da API Key no header.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Tupla `(usuário, None)` quando a chave é válida ou `None`
            quando o header de API Key não está presente.

        Raises:
            AuthenticationFailed: Quando a API Key informada é inválida.
        """
        header = settings.API_KEY_HEADER.replace("-", "_").upper()
        key = request.META.get(f"HTTP_{header}") or request.headers.get(
            settings.API_KEY_HEADER
        )

        if not key:
            return None

        if key != settings.API_KEY:
            raise AuthenticationFailed("API Key inválida.")

        return (_ApiKeyUser(), None)


class ApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """Descreve a ApiKeyAuthentication para o drf-spectacular."""

    target_class = "config.authentication.ApiKeyAuthentication"
    name = "ApiKeyAuth"

    def get_security_definition(self, auto_schema: Any) -> dict[str, str]:
        """Retorna o security scheme OpenAPI para o header de API Key."""
        return {
            "type": "apiKey",
            "in": "header",
            "name": settings.API_KEY_HEADER,
        }
