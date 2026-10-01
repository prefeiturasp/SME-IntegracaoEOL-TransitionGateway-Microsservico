"""Health checks do gateway e dos domínios integrados."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

import httpx
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api_clients import DomainName, get_api_client

_DOMINIOS: tuple[DomainName, ...] = (
    "alunos",
    "institucional",
    "pedagogico",
    "professores",
    "programasedu",
)

_HEALTH_PATHS: dict[DomainName, str] = {
    "alunos": "/api/v1/alunos/health/",
    "institucional": "/api/v1/institucional/health/",
    "pedagogico": "/api/v1/pedagogico/health/",
    "professores": "/api/v1/professores/health/",
    "programasedu": "/api/v1/programasedu/health/",
}


def _latency_ms(start: float) -> float:
    """Calcula a duração da chamada.

    Args:
        start: Instante inicial medido em monotonic.

    Returns:
        Tempo em milissegundos.
    """
    return round((time.monotonic() - start) * 1000, 2)


def _verificar_dominio(dominio: DomainName) -> dict[str, Any]:
    """Consulta o health check de um domínio.

    Args:
        dominio: Domínio consultado.

    Returns:
        Resultado da consulta ao domínio.
    """
    start = time.monotonic()
    path = _HEALTH_PATHS[dominio]
    try:
        response = get_api_client(dominio).get(path)
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": _latency_ms(start),
            "error": str(exc),
        }

    return {
        "ok": status.is_success(response.status_code),
        "status_code": response.status_code,
        "latency_ms": _latency_ms(start),
    }


def _response_health(checks: Mapping[str, dict[str, Any]]) -> Response:
    """Monta resposta HTTP do health check.

    Args:
        checks: Resultado das consultas por domínio.

    Returns:
        Resposta com o status consolidado.
    """
    ok = all(item["ok"] for item in checks.values())
    status_code = (
        status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return Response(
        {
            "status": "ok" if ok else "degraded",
            "checks": checks,
        },
        status=status_code,
    )


class GatewayHealthView(APIView):
    """Informa a disponibilidade dos domínios integrados."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="gateway_health",
        summary="Verificar health dos domínios",
        tags=["Health"],
        responses={200: OpenApiTypes.OBJECT, 503: OpenApiTypes.OBJECT},
    )
    def get(self, request: Request) -> Response:
        """Retorna o health check consolidado.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resultado consolidado por domínio.
        """
        checks: dict[str, dict[str, Any]] = {
            dominio: _verificar_dominio(dominio) for dominio in _DOMINIOS
        }
        return _response_health(checks)


class DomainHealthView(APIView):
    """Informa a disponibilidade de um domínio integrado."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="gateway_domain_health",
        summary="Verificar health de um domínio",
        tags=["Health"],
        responses={
            200: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            503: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request: Request, dominio: str) -> Response:
        """Retorna o health check de um domínio.

        Args:
            request: Requisição HTTP recebida.
            dominio: Domínio consultado.

        Returns:
            Resultado do domínio informado.
        """
        if dominio not in _DOMINIOS:
            return Response(
                {"detail": "Domínio inválido."},
                status=status.HTTP_404_NOT_FOUND,
            )
        check = _verificar_dominio(dominio)  # type: ignore[arg-type]
        return _response_health({dominio: check})
