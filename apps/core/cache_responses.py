"""Cache compartilhado da representacao final de respostas DRF."""

import hashlib
import json
from collections.abc import Callable
from typing import Any, cast

from django.http import HttpResponse
from django.utils import timezone, translation
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core import cache


def resposta_serializada_cacheada(
    request: Request,
    *,
    chave: str,
    buscar: Callable[[], Any],
    serializer_class: type[serializers.BaseSerializer],
    ttl: int,
    many: bool = True,
    status_vazio: int = 200,
    validar: bool = False,
) -> HttpResponse | Response:
    """Busca, serializa e renderiza apenas quando o cache expira.

    Use dentro de views que ja executaram autenticacao e permissoes.
    A chave deve incluir o dominio, todos os filtros e, para dados
    personalizados, o usuario ou escopo de acesso.

    Args:
        request: Requisicao autenticada com formato negociado.
        chave: Identificador versionado da consulta e seus filtros.
        buscar: Funcao que consulta os dados brutos na origem.
        serializer_class: Serializer do contrato publico.
        ttl: Expiracao em minutos.
        many: Serializa uma lista quando True; um objeto quando False.
        status_vazio: Status usado para listas vazias, como 204.
        validar: Valida a origem e armazena os dados validados do serializer.

    Returns:
        JSON pronto ou resposta para o renderer negociado.
    """
    contexto = [
        chave,
        f"{serializer_class.__module__}.{serializer_class.__qualname__}",
        many,
        status_vazio,
        validar,
        timezone.get_current_timezone_name(),
        translation.get_language(),
    ]
    identificador = hashlib.sha256(json.dumps(contexto).encode()).hexdigest()

    def representar() -> bytes:
        dados = buscar()
        if many and status_vazio != 200 and dados == []:
            return b""
        if validar:
            serializer = serializer_class(data=dados, many=many)
            if not serializer.is_valid():
                raise ValueError(
                    "Resposta da origem invalida para o serializer."
                )
            representacao = serializer.validated_data
        else:
            representacao = serializer_class(dados, many=many).data
        return cast(
            bytes,
            JSONRenderer().render(representacao),
        )

    corpo = cache.obter_ou_calcular(
        f"resposta-json:v1:{identificador}", representar, ttl
    )
    if many and status_vazio != 200 and corpo == b"":
        return Response(status=status_vazio)

    renderer = request.accepted_renderer
    json_renderer = cast(JSONRenderer, renderer)
    if (
        renderer.__class__ is JSONRenderer
        and json_renderer.get_indent(request.accepted_media_type, {}) is None
    ):
        return HttpResponse(corpo, content_type=renderer.media_type)
    return Response(json.loads(corpo))
