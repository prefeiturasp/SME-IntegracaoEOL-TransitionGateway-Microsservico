"""Valida cache do JSON final pelo fluxo autenticado das views."""

from time import time
from typing import Any
from unittest.mock import patch
from zoneinfo import ZoneInfo

import httpx
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone, translation
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

from apps.pedagogico import services
from apps.pedagogico.serializers import (
    ComponenteBaseSerializer,
    ComponenteCurricularSerializer,
    ComponenteRegenciaSerializer,
    GradeCurricularSerializer,
    ItinerarioEnsinoMedioSerializer,
    ModalidadeEnsinoListSerializer,
)
from apps.pedagogico.views import ComponentesRegenciaViewSet

_BASE = "/api/v1/componentes-curriculares"
_REGENCIA = f"{_BASE}/anos/1/regencia"
_TURMAS = f"{_BASE}/ues/UE1/turmas"
_AGRUPAMENTOS = f"{_BASE}/138/territorio-saber/agrupamentos-correlacionados"
_GRADE = f"{_BASE}/ano-turma/ano-letivo/2026"
_LISTA_TURMAS = f"{_BASE}/turmas"
_LOTE = f"{_BASE}/territorio-saber/agrupamentos-correlacionados"
_ITINERARIOS = "/api/turmas/itinerario/ensino-medio"
_MODALIDADES = "/api/escolas/modalidades_ensino"
_ITEM_GRADE = {
    "codigo_componente_curricular": 138,
    "descricao_componente_curricular": "PORTUGUES",
    "codigo_ano_turma": "1",
    "descricao_serie_ensino": "1 ano",
    "codigo_serie_ensino": 1,
    "modalidade": 5,
}
_ITEM = {
    "codigo": 138,
    "descricao": "Educa\u00e7\u00e3o",
    "ano_turma": "1",
    "ano_letivo": 2026,
    "codigo_componente_territorio_saber": None,
    "codigo_componente_curricular_pai": None,
    "regencia": False,
    "planejamento_regencia": False,
    "territorio_saber": True,
    "tipo_escola": None,
    "turno_turma": 0,
    "componente_planejamento_regencia": False,
    "turma_codigo": "T1",
    "exibir_componente_eol": True,
    "professor": None,
    "codigos_territorios_agrupamento": [1214],
    "inicio_atribuicao": "2026-02-04T03:00:00Z",
    "fim_atribuicao": None,
}


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pedagogico-json-test",
        }
    }
)
class CacheEndpointsTest(SimpleTestCase):
    """Exercita cache real e serializers reais com HTTP simulado."""

    def setUp(self) -> None:
        cache.clear()
        self.addCleanup(cache.clear)
        breaker = self.enterContext(
            patch("apps.core.cache.get_circuit_breaker")
        )
        breaker.return_value.call.side_effect = lambda func, *args: func(*args)
        self.origem = self.enterContext(patch.object(services._client, "get"))
        self.origem.return_value = httpx.Response(
            200,
            json=[_ITEM],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=User(username="teste"))

    def test_cache_aquecido_evita_http_serializer_e_renderer(self) -> None:
        """JSON aquecido preserva o contrato sem repetir as tres etapas."""
        consultas = [
            (_REGENCIA, ComponenteRegenciaSerializer),
            (_TURMAS, ComponenteBaseSerializer),
            (_AGRUPAMENTOS, ComponenteCurricularSerializer),
        ]
        for url, serializer in consultas:
            with self.subTest(url=url):
                cache.clear()
                self.origem.reset_mock()
                esperado = JSONRenderer().render(
                    serializer([_ITEM], many=True).data
                )
                primeiro = self.client.get(url)
                self.assertEqual(primeiro.status_code, 200)
                self.assertEqual(primeiro.content, esperado)
                with (
                    patch.object(
                        serializer,
                        "to_representation",
                        side_effect=AssertionError,
                    ),
                    patch.object(
                        JSONRenderer, "render", side_effect=AssertionError
                    ),
                ):
                    segundo = self.client.get(url)
                self.assertEqual(segundo.status_code, 200)
                self.assertEqual(segundo.content, primeiro.content)
                self.origem.assert_called_once()

    def test_isola_todos_os_filtros(self) -> None:
        urls = [
            _REGENCIA,
            f"{_BASE}/anos/2/regencia",
            _TURMAS,
            f"{_TURMAS}?turmas=T1",
            f"{_TURMAS}?turmas=T2",
            f"{_BASE}/ues/UE2/turmas?turmas=T1",
            _AGRUPAMENTOS,
            f"{_BASE}/139/territorio-saber/agrupamentos-correlacionados",
            f"{_AGRUPAMENTOS}?dataBaseTick=638527968000000000",
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.origem.call_count, len(urls))

    def test_ordem_e_repeticoes_das_turmas_compartilham_cache(self) -> None:
        primeiro = self.client.get(f"{_TURMAS}?turmas=T2&turmas=T1&turmas=T1")
        segundo = self.client.get(f"{_TURMAS}?turmas=T1&turmas=T2")
        self.assertEqual(primeiro.content, segundo.content)
        self.origem.assert_called_once()
        self.assertEqual(
            self.origem.call_args.kwargs["params"],
            {"turmas": ["T1", "T2"]},
        )

    def test_vazios_preservam_status_com_cache_aquecido(self) -> None:
        self.origem.return_value = httpx.Response(
            200,
            json=[],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        for url in [_REGENCIA, _TURMAS, _AGRUPAMENTOS]:
            with self.subTest(url=url):
                self.origem.reset_mock()
                for _ in range(2):
                    resposta = self.client.get(url)
                    self.assertEqual(
                        resposta.status_code, 204 if url == _REGENCIA else 200
                    )
                    self.assertEqual(
                        resposta.content, b"" if url == _REGENCIA else b"[]"
                    )
                self.origem.assert_called_once()

    def test_erro_http_nao_e_cacheado(self) -> None:
        self.origem.return_value = httpx.Response(
            503,
            json={"detail": "indisponivel"},
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        for url in [_REGENCIA, _TURMAS, _AGRUPAMENTOS]:
            with self.subTest(url=url):
                self.origem.reset_mock()
                for _ in range(2):
                    with self.assertRaises(httpx.HTTPStatusError):
                        self.client.get(url)
                self.assertEqual(self.origem.call_count, 2)

    def test_json_invalido_nao_e_cacheado(self) -> None:
        self.origem.return_value = httpx.Response(
            200,
            text="json invalido",
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        for _ in range(2):
            with self.assertRaises(ValueError):
                self.client.get(_REGENCIA)
        self.assertEqual(self.origem.call_count, 2)

    def test_ttl_regencia_e_atribuicoes(self) -> None:
        with patch.object(cache, "set", wraps=cache.set) as gravar:
            for url in [_REGENCIA, _TURMAS, _AGRUPAMENTOS]:
                self.client.get(url)
        self.assertEqual(
            [chamada.args[2] for chamada in gravar.call_args_list],
            [720 * 60, 5 * 60, 5 * 60],
        )
        self.assertTrue(
            all(
                isinstance(chamada.args[1], bytes)
                for chamada in gravar.call_args_list
            )
        )

    def test_expiracao_renova_atribuicoes_e_preserva_regencia(self) -> None:
        instante = time()
        with patch("time.time", return_value=instante):
            for url in [_REGENCIA, _TURMAS, _AGRUPAMENTOS]:
                self.client.get(url)
        self.origem.reset_mock()
        with patch("time.time", return_value=instante + 301):
            for url in [_REGENCIA, _TURMAS, _AGRUPAMENTOS]:
                self.client.get(url)
        self.assertEqual(self.origem.call_count, 2)

    def test_cache_indisponivel_consulta_origem(self) -> None:
        with (
            patch.object(cache, "get", side_effect=ConnectionError),
            patch.object(cache, "set", side_effect=ConnectionError),
            self.assertLogs("apps.core.cache", level="WARNING"),
        ):
            resposta = self.client.get(_REGENCIA)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()[0]["codigo"], 138)
        self.origem.assert_called_once()

    def test_json_indentado_e_browsable_api_com_cache_aquecido(self) -> None:
        primeiro = self.client.get(_REGENCIA)
        indentado = self.client.get(
            _REGENCIA, HTTP_ACCEPT="application/json; indent=4"
        )
        self.assertEqual(primeiro.json(), indentado.json())
        self.assertIn(b"\n", indentado.content)
        html = self.client.get(_REGENCIA, HTTP_ACCEPT="text/html")
        self.assertEqual(html.status_code, 200)
        self.assertIn("text/html", html["Content-Type"])
        self.origem.assert_called_once()

    def test_renderer_personalizado_e_preservado(self) -> None:
        class JsonAsciiRenderer(JSONRenderer):
            ensure_ascii = True

        primeiro = self.client.get(_REGENCIA)
        with patch.object(
            ComponentesRegenciaViewSet, "renderer_classes", [JsonAsciiRenderer]
        ):
            personalizado = self.client.get(_REGENCIA)
        self.assertEqual(primeiro.json(), personalizado.json())
        self.assertIn(b"\\u00e7", personalizado.content)
        self.origem.assert_called_once()

    def test_cache_nao_dispensa_autenticacao(self) -> None:
        self.client.get(_REGENCIA)
        resposta = APIClient().get(_REGENCIA)
        self.assertIn(resposta.status_code, [401, 403])
        self.origem.assert_called_once()

    def test_isola_fuso_e_idioma(self) -> None:
        with timezone.override(ZoneInfo("UTC")), translation.override("pt-br"):
            utc = self.client.get(_REGENCIA)
        with (
            timezone.override(ZoneInfo("America/Sao_Paulo")),
            translation.override("pt-br"),
        ):
            local = self.client.get(_REGENCIA)
        with timezone.override(ZoneInfo("UTC")), translation.override("en"):
            self.client.get(_REGENCIA)
        self.assertEqual(utc.status_code, 200)
        self.assertEqual(local.status_code, 200)
        self.assertEqual(self.origem.call_count, 3)

    def test_novos_endpoints_cacheiam_json_final(self) -> None:
        casos = [
            (_GRADE, GradeCurricularSerializer, [_ITEM_GRADE], True),
            (_LISTA_TURMAS, ComponenteCurricularSerializer, [_ITEM], True),
            (_LOTE, ComponenteCurricularSerializer, [_ITEM], True),
            (
                _ITINERARIOS,
                ItinerarioEnsinoMedioSerializer,
                [{"id": 9, "nome": " Itinerario ", "serie": "2"}],
                True,
            ),
            (
                _MODALIDADES,
                ModalidadeEnsinoListSerializer,
                ["Infantil", "Fundamental"],
                False,
            ),
        ]
        for url, serializer, payload, many in casos:
            with self.subTest(url=url):
                cache.clear()
                with patch.object(services._client, "post") as post:
                    origem = post if url == _LOTE else self.origem
                    origem.reset_mock()
                    origem.return_value = httpx.Response(
                        200,
                        json=payload,
                        request=httpx.Request(
                            "GET", "https://pedagogico.test"
                        ),
                    )

                    def consultar(endereco: str = url) -> Any:
                        if endereco == _LOTE:
                            return self.client.post(
                                endereco,
                                "[138, 139]",
                                content_type="application/json",
                            )
                        return self.client.get(endereco)

                    if url == _ITINERARIOS:
                        validador = serializer(data=payload, many=True)
                        validador.is_valid(raise_exception=True)
                        esperado = validador.validated_data
                    else:
                        esperado = serializer(payload, many=many).data
                    primeiro = consultar()
                    self.assertEqual(primeiro.status_code, 200)
                    self.assertEqual(
                        primeiro.content, JSONRenderer().render(esperado)
                    )
                    with (
                        patch.object(
                            serializer,
                            "to_representation",
                            side_effect=AssertionError,
                        ),
                        patch.object(
                            serializer,
                            "to_internal_value",
                            side_effect=AssertionError,
                        ),
                        patch.object(
                            JSONRenderer, "render", side_effect=AssertionError
                        ),
                    ):
                        segundo = consultar()
                    self.assertEqual(segundo.content, primeiro.content)
                    origem.assert_called_once()

    def test_grade_e_lista_turmas_isolam_filtros_e_ordem(self) -> None:
        self.origem.return_value = httpx.Response(
            200,
            json=[{**_ITEM, **_ITEM_GRADE}],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        urls = [
            _GRADE,
            f"{_BASE}/ano-turma/ano-letivo/2025",
            f"{_LISTA_TURMAS}?codigoTurmas=T1&codigoTurmas=T2",
            f"{_LISTA_TURMAS}?codigoTurmas=T2&codigoTurmas=T1",
            f"{_LISTA_TURMAS}?codigoTurmas=T1&codigoTurmas=T1",
            f"{_LISTA_TURMAS}?codigoTurmas=T1",
            f"{_LISTA_TURMAS}?codigoTurmas=T1&adicionarComponentesPlanejamento=false",
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.origem.call_count, len(urls))
        self.client.get(
            f"{_LISTA_TURMAS}?codigoTurmas=T1&adicionarComponentesPlanejamento=true"
        )
        self.assertEqual(self.origem.call_count, len(urls))

    def test_lote_isola_ids_ordem_e_data_e_valida_antes_do_cache(self) -> None:
        with patch.object(services._client, "post") as post:
            post.return_value = self.origem.return_value
            consultas = [
                (_LOTE, [138, 139]),
                (_LOTE, [139, 138]),
                (_LOTE, [138]),
                (f"{_LOTE}?dataBaseTick=638527968000000000", [138]),
            ]
            for url, ids in consultas:
                self.assertEqual(
                    self.client.post(url, ids, format="json").status_code, 200
                )
            self.assertEqual(post.call_count, len(consultas))
            self.client.post(_LOTE, [138, 139], format="json")
            self.assertEqual(post.call_count, len(consultas))
            self.assertEqual(
                post.call_args_list[0].kwargs["payload"], [138, 139]
            )
            self.assertEqual(
                post.call_args_list[1].kwargs["payload"], [139, 138]
            )
            self.assertEqual(
                self.client.post(
                    _LOTE, {"ids": [138]}, format="json"
                ).status_code,
                400,
            )
            vazio = self.client.post(_LOTE, [], format="json")
            self.assertEqual(vazio.status_code, 200)
            self.assertEqual(vazio.json(), [])
            self.assertEqual(post.call_count, len(consultas))

    def test_catalogos_invalidos_ou_vazios_nao_envenenam_cache(self) -> None:
        for url, payload, status in [
            (_ITINERARIOS, [{"id": 9, "nome": "A", "serie": "invalida"}], 502),
            (_MODALIDADES, [], 404),
        ]:
            with self.subTest(url=url):
                self.origem.reset_mock()
                self.origem.return_value = httpx.Response(
                    200,
                    json=payload,
                    request=httpx.Request("GET", "https://pedagogico.test"),
                )
                for _ in range(2):
                    self.assertEqual(self.client.get(url).status_code, status)
                self.assertEqual(self.origem.call_count, 2)
        self.origem.return_value = httpx.Response(
            200,
            json=["Infantil"],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        self.assertEqual(self.client.get(_MODALIDADES).json(), ["Infantil"])

    def test_vazios_dos_novos_endpoints_preservam_contrato(self) -> None:
        self.origem.return_value = httpx.Response(
            200,
            json=[],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        for url in [_GRADE, _LISTA_TURMAS, _ITINERARIOS]:
            with self.subTest(url=url):
                self.origem.reset_mock()
                for _ in range(2):
                    resposta = self.client.get(url)
                    self.assertEqual(resposta.status_code, 200)
                    self.assertEqual(resposta.json(), [])
                self.origem.assert_called_once()

    def test_novos_endpoints_nao_cacheiam_erros_http(self) -> None:
        erro = httpx.Response(
            503,
            json={"detail": "indisponivel"},
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        self.origem.return_value = erro
        for url in [_GRADE, _LISTA_TURMAS]:
            with self.subTest(url=url):
                self.origem.reset_mock()
                for _ in range(2):
                    with self.assertRaises(httpx.HTTPStatusError):
                        self.client.get(url)
                self.assertEqual(self.origem.call_count, 2)
        with patch.object(services._client, "post", return_value=erro) as post:
            for _ in range(2):
                with self.assertRaises(httpx.HTTPStatusError):
                    self.client.post(_LOTE, [138], format="json")
            self.assertEqual(post.call_count, 2)

    def test_novos_endpoints_aplicam_ttls_de_catalogo_e_atribuicoes(
        self,
    ) -> None:
        self.origem.return_value = httpx.Response(
            200,
            json=[{**_ITEM, **_ITEM_GRADE}],
            request=httpx.Request("GET", "https://pedagogico.test"),
        )
        with (
            patch.object(cache, "set", wraps=cache.set) as gravar,
            patch.object(
                services, "get_itinerarios_ensino_medio", return_value=[]
            ),
            patch.object(
                services, "get_modalidades_ensino", return_value=["Infantil"]
            ),
            patch.object(
                services._client, "post", return_value=self.origem.return_value
            ),
        ):
            for url in [_GRADE, _LISTA_TURMAS, _ITINERARIOS, _MODALIDADES]:
                self.client.get(url)
            self.client.post(_LOTE, [138], format="json")
        self.assertEqual(
            [chamada.args[2] for chamada in gravar.call_args_list],
            [720 * 60, 5 * 60, 720 * 60, 720 * 60, 5 * 60],
        )
