"""Preserva contrato e trabalho evitado nas respostas de contagem."""

import gzip
import zlib
from copy import deepcopy
from secrets import token_urlsafe
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

from apps.alunos import services
from apps.alunos.serializers import QuantidadeMatriculadosSerializer
from apps.alunos.views import QuantidadeMatriculadosView
from apps.core import cache as cache_leitura

_URL = "/api/alunos/ano-letivo/2026/matriculados/quantidade"
_LINHA = {
    "quantidade": "28",
    "ordem": "2",
    "modalidade": "EF",
    "ano": 3,
    "turma": "3B",
    "dre_codigo": "001",
    "ue_codigo": "000002",
}
_ESPERADO = {
    "quantidade": 28,
    "ordem": 2,
    "modalidade": "EF",
    "ano": "3",
    "turma": "3B",
    "dreCodigo": "001",
    "ueCodigo": "000002",
}


class QuantidadeSerializerPerformanceTest(SimpleTestCase):
    """Preserva coerções e dispensa resolução genérica em linhas completas."""

    def test_linhas_completas_nao_resolvem_atributos_por_campo(self) -> None:
        """Converte uma lista sem repetir a descoberta dos atributos."""
        original = deepcopy(_LINHA)
        with patch.object(
            serializers.Field,
            "get_attribute",
            side_effect=AssertionError("Resolução genérica repetida"),
        ):
            resultado = QuantidadeMatriculadosSerializer(
                [_LINHA, _LINHA], many=True
            ).data
        self.assertEqual(resultado, [_ESPERADO, _ESPERADO])
        self.assertEqual(_LINHA, original)

    def test_preserva_nulos_objetos_e_campos_ausentes(self) -> None:
        """Mantém os caminhos alternativos do contrato de representação."""
        self.assertEqual(
            QuantidadeMatriculadosSerializer(SimpleNamespace(**_LINHA)).data,
            _ESPERADO,
        )
        nulos = dict.fromkeys(_LINHA)
        self.assertEqual(
            QuantidadeMatriculadosSerializer(nulos).data,
            dict.fromkeys(_ESPERADO),
        )
        parcial = {"quantidade": 1}
        self.assertEqual(
            QuantidadeMatriculadosSerializer(parcial).data,
            {**dict.fromkeys(_ESPERADO), "quantidade": 1},
        )
        with self.assertRaises(KeyError):
            _ = QuantidadeMatriculadosSerializer({"ordem": 1}).data


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "contagem-representacao-tests",
        }
    },
)
class QuantidadeRespostaPerformanceTest(SimpleTestCase):
    """Reutiliza o corpo sem compartilhar autenticação ou headers."""

    def setUp(self) -> None:
        """Isola o armazenamento e a comunicação externa."""
        cache.clear()
        self.addCleanup(cache.clear)
        chave_teste = token_urlsafe(32)
        self.enterContext(override_settings(API_KEY=chave_teste))
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY=chave_teste)
        self.origem = self.enterContext(patch.object(services._client, "get"))
        self.origem.return_value = httpx.Response(
            200,
            json=[_LINHA] * 20,
            request=httpx.Request("GET", "https://alunos.test/quantidade"),
        )

    def test_hit_nao_serializa_novamente_nem_repete_id(self) -> None:
        """Reutiliza dados mas mantém os headers próprios de cada chamada."""
        primeira = self.client.get(_URL, HTTP_X_REQUEST_ID="contagem-um")
        self.assertEqual(primeira.status_code, 200)
        self.assertEqual(primeira.json(), [_ESPERADO] * 20)
        with patch.object(
            QuantidadeMatriculadosSerializer,
            "to_representation",
            side_effect=AssertionError("Serializer repetido em hit"),
        ):
            segunda = self.client.get(_URL, HTTP_X_REQUEST_ID="contagem-dois")
        self.assertEqual(primeira.content, segunda.content)
        self.assertEqual(segunda.headers["X-Request-ID"], "contagem-dois")
        self.origem.assert_called_once()
        self.assertEqual(APIClient().get(_URL).status_code, 403)

    def test_mantem_negociacao_de_gzip_e_indentacao(self) -> None:
        """Não entrega corpo comprimido ou formatado ao cliente errado."""
        normal = self.client.get(_URL, HTTP_ACCEPT_ENCODING="identity")
        compacta = self.client.get(_URL, HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(compacta.headers["Content-Encoding"], "gzip")
        self.assertEqual(gzip.decompress(compacta.content), normal.content)
        indentada = self.client.get(
            _URL, HTTP_ACCEPT="application/json; indent=4"
        )
        self.assertEqual(indentada.json(), normal.json())
        self.assertIn(b"\n", indentada.content)
        self.assertNotIn("Content-Encoding", normal.headers)
        self.assertIn("Accept-Encoding", compacta.headers["Vary"])
        self.origem.assert_called_once()

    def test_mantem_formato_html_e_rejeita_formato_nao_suportado(self) -> None:
        """Mantém a negociação mesmo quando a representação está pronta."""
        normal = self.client.get(_URL)
        navegavel = self.client.get(_URL, HTTP_ACCEPT="text/html")
        self.assertEqual(navegavel.status_code, 200)
        self.assertIn("text/html", navegavel.headers["Content-Type"])
        self.assertIn(b"dreCodigo", navegavel.content)
        self.assertEqual(
            self.client.get(_URL, HTTP_ACCEPT="application/xml").status_code,
            406,
        )
        self.assertEqual(self.client.get(_URL).content, normal.content)
        self.origem.assert_called_once()

    def test_preserva_formatacao_de_renderer_json_personalizado(self) -> None:
        """Mantém a representação definida por um renderer personalizado."""

        class JsonAsciiRenderer(JSONRenderer):
            """Representa caracteres Unicode com sequências ASCII."""

            ensure_ascii = True

        self.origem.return_value = httpx.Response(
            200,
            json=[{**_LINHA, "turma": "3ºA"}],
            request=httpx.Request("GET", "https://alunos.test/quantidade"),
        )
        with patch.object(
            QuantidadeMatriculadosView, "renderer_classes", [JsonAsciiRenderer]
        ):
            resposta = self.client.get(_URL)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [{**_ESPERADO, "turma": "3ºA"}])
        self.assertIn(b"\\u00ba", resposta.content)

    def test_filtros_distintos_nao_compartilham_respostas(self) -> None:
        """Não mistura listas de turmas que possuem dígitos em comum."""
        self.client.get(_URL + "?turma=12&turma=3")
        self.client.get(_URL + "?turma=1&turma=23")
        self.client.get(_URL + "?ue_codigo=000002")
        self.assertEqual(self.origem.call_count, 3)

    def test_chave_versionada_e_ttl_nao_renovado_no_hit(self) -> None:
        """Mantém os filtros e as 24 horas sem prolongar a validade."""
        parametros = {
            "dre_codigo": " 100000 ",
            "ue_codigo": " 000005 ",
            "turma": ["9100006"],
            "modalidade": ["5"],
            "ano": ["3"],
        }
        with patch.object(cache, "set", wraps=cache.set) as gravar:
            primeira = self.client.get(_URL, parametros)
            self.client.get(_URL, parametros)
        gravar.assert_called_once()
        chave, valor, segundos = gravar.call_args.args
        self.assertEqual(
            chave,
            "quantidade-alunos-json:v1:2026:100000:000005:9100006:5:3",
        )
        self.assertEqual(segundos, 86400)
        self.assertEqual(zlib.decompress(valor), primeira.content)

    def test_separador_entre_itens_da_lista(self) -> None:
        """Listas distintas não colidem na identificação da representação."""
        with patch.object(cache, "set", wraps=cache.set) as gravar:
            self.client.get(_URL, {"turma": ["12", "3"]})
            self.client.get(_URL, {"turma": ["1", "23"]})
        self.assertEqual(
            [chamada.args[0] for chamada in gravar.call_args_list],
            [
                "quantidade-alunos-json:v1:2026:::12,3::",
                "quantidade-alunos-json:v1:2026:::1,23::",
            ],
        )

    def test_lista_vazia_e_head_reutilizam_corpo(self) -> None:
        """Uma resposta vazia continua sendo um resultado armazenável."""
        self.origem.return_value = httpx.Response(
            200,
            json=[],
            request=httpx.Request("GET", "https://alunos.test/quantidade"),
        )
        self.assertEqual(self.client.get(_URL).json(), [])
        resposta = self.client.head(_URL)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.content, b"")
        self.origem.assert_called_once()

    def test_cache_indisponivel_nao_impede_resposta(self) -> None:
        """Falhas de leitura ou gravação não substituem os dados por erro."""
        with (
            patch.object(cache, "get", side_effect=ConnectionError),
            patch.object(cache, "set", side_effect=ConnectionError),
            self.assertLogs(cache_leitura.logger, level="WARNING"),
        ):
            resposta = self.client.get(_URL)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [_ESPERADO] * 20)

    def test_formato_invalido_nao_impede_resposta(self) -> None:
        """Recalcula uma representação que não pode ser descompactada."""
        cache.set("quantidade-alunos-json:v1:2026:::::", b"invalido")
        with self.assertLogs("apps.alunos.respostas", level="WARNING"):
            resposta = self.client.get(_URL)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [_ESPERADO] * 20)

    def test_isola_formato_antigo_e_demais_filtros(self) -> None:
        """Isola o corpo serializado da lista antiga e de cada consulta."""
        cache.set("quantidade-alunos:2026:::::", [{"quantidade": -1}])
        for filtro in (
            {},
            {"dre_codigo": "001"},
            {"ue_codigo": "000002"},
            {"ano": ["3"]},
            {"modalidade": ["5"]},
        ):
            self.assertEqual(
                self.client.get(_URL, filtro).json(), [_ESPERADO] * 20
            )
        self.assertEqual(self.origem.call_count, 5)

    def test_nao_armazena_erro_da_origem(self) -> None:
        """Uma consulta com erro pode recuperar na chamada seguinte."""
        for codigo in (401, 403, 404, 503, 601):
            with self.subTest(status=codigo):
                cache.clear()
                self.origem.reset_mock()
                resposta = httpx.Response(
                    codigo,
                    json={"detail": "Erro de teste"},
                    request=httpx.Request(
                        "GET", "https://alunos.test/quantidade"
                    ),
                )
                self.origem.side_effect = [
                    httpx.HTTPStatusError(
                        "Erro de teste",
                        request=resposta.request,
                        response=resposta,
                    ),
                    self.origem.return_value,
                ]
                erro = self.client.get(_URL)
                self.assertEqual(erro.status_code, codigo)
                self.assertEqual(erro.json(), {"detail": "Erro de teste"})
                self.assertEqual(self.client.get(_URL).status_code, 200)
                self.assertEqual(self.origem.call_count, 2)
