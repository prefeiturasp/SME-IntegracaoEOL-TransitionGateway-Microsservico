"""Autenticação por API Key usada pelo MSC."""

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class _ApiKeyUser:
    is_authenticated = True


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> tuple | None:
        header = settings.API_KEY_HEADER.replace("-", "_").upper()
        key = request.META.get(f"HTTP_{header}") or request.headers.get(
            settings.API_KEY_HEADER
        )

        if not key:
            return None

        if key != settings.API_KEY:
            raise AuthenticationFailed("API Key inválida.")

        return (_ApiKeyUser(), None)
