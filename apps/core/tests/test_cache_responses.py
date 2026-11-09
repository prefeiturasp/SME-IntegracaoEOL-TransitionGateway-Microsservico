"""Valida contratos reutilizaveis do cache de respostas serializadas."""

from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.core.cache_responses import resposta_serializada_cacheada


class ItemSerializer(serializers.Serializer):
    """Contrato de um objeto simples."""

    codigo = serializers.IntegerField()


class ItemDetalhadoSerializer(ItemSerializer):
    """Outro contrato para a mesma origem de dados."""

    descricao = serializers.CharField()


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "core-cache-responses-test",
        }
    }
)
class CacheResponsesTest(SimpleTestCase):
    """Confirma isolamento de contrato e cache de objetos e listas."""

    def setUp(self) -> None:
        cache.clear()
        self.addCleanup(cache.clear)
        breaker = self.enterContext(
            patch("apps.core.cache.get_circuit_breaker")
        )
        breaker.return_value.call.side_effect = lambda func, *args: func(*args)
        self.request = Request(APIRequestFactory().get("/"))
        self.request.accepted_renderer = JSONRenderer()
        self.request.accepted_media_type = "application/json"

    def test_objeto_unico_preserva_contrato_e_reutiliza_cache(self) -> None:
        buscar = MagicMock(return_value={"codigo": "138"})
        for _ in range(2):
            resposta = resposta_serializada_cacheada(
                self.request,
                chave="dominio:objeto:v1:138",
                buscar=buscar,
                serializer_class=ItemSerializer,
                ttl=5,
                many=False,
            )
            self.assertEqual(resposta.content, b'{"codigo":138}')
        buscar.assert_called_once()

    def test_mesma_chave_com_serializers_distintos_nao_colide(self) -> None:
        buscar = MagicMock(return_value=[{"codigo": 138, "descricao": "A"}])
        for serializer in [ItemSerializer, ItemDetalhadoSerializer]:
            resposta = resposta_serializada_cacheada(
                self.request,
                chave="dominio:lista:v1",
                buscar=buscar,
                serializer_class=serializer,
                ttl=5,
            )
            self.assertEqual(resposta.status_code, 200)
        self.assertIn(b'"descricao":"A"', resposta.content)
        self.assertEqual(buscar.call_count, 2)

    def test_erro_de_serializacao_nao_e_cacheado(self) -> None:
        buscar = MagicMock(return_value=[{"codigo": "invalido"}])
        for _ in range(2):
            with self.assertRaises(ValueError):
                resposta_serializada_cacheada(
                    self.request,
                    chave="dominio:lista:v1",
                    buscar=buscar,
                    serializer_class=ItemSerializer,
                    ttl=5,
                )
        self.assertEqual(buscar.call_count, 2)
