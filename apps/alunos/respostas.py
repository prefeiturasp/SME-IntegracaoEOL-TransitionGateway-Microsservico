"""Representações de leitura das contagens de alunos."""

import json
import logging
import zlib
from typing import Any

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from apps.alunos import services
from apps.alunos.serializers import QuantidadeMatriculadosSerializer
from apps.core import cache

logger = logging.getLogger(__name__)


def resposta_quantidade_matriculados(
    request: Request, ano_letivo: str, filtros: dict[str, Any]
) -> HttpResponse:
    """Retorna as contagens no formato de apresentação solicitado.

    Args:
        request: Requisição autenticada com formato já negociado.
        ano_letivo: Ano letivo consultado.
        filtros: Filtros de DRE, UE, modalidades, anos e turmas.

    Returns:
        Contagens representadas no contrato público.
    """
    chave = "quantidade-alunos-json:v1:{}:{}:{}:{}:{}:{}".format(
        ano_letivo,
        (filtros.get("dre_codigo") or "").strip(),
        (filtros.get("ue_codigo") or "").strip(),
        ",".join(filtros.get("turma") or []),
        ",".join(filtros.get("modalidade") or []),
        ",".join(filtros.get("ano") or []),
    )

    def representar() -> bytes:
        """Representa as contagens preservando os conversores dos campos."""
        dados = services.get_quantidade_matriculados(
            ano_letivo=ano_letivo, **filtros
        )
        corpo = JSONRenderer().render(
            QuantidadeMatriculadosSerializer(dados, many=True).data
        )
        return zlib.compress(corpo, level=1)

    armazenado = cache.obter_ou_calcular(
        chave, representar, cache.TTL_LEGADO_PADRAO_MINUTOS
    )
    try:
        corpo = zlib.decompress(armazenado)
    except (TypeError, zlib.error):
        logger.warning("Representação de contagem armazenada inválida")
        corpo = zlib.decompress(representar())

    renderer = request.accepted_renderer
    if (
        renderer.__class__ == JSONRenderer
        and renderer.get_indent(request.accepted_media_type, {}) is None
    ):
        return HttpResponse(corpo, content_type=renderer.media_type)
    return Response(json.loads(corpo))
