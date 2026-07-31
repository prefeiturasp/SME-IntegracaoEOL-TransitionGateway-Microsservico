"""Valida a conversão de respostas HTTP em dados Python."""

from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase
from sme_sidecar_sdk import build_http_client
from sme_sidecar_sdk.observability.context import correlation_context

from apps.core.http_client import ServiceClient


def _make_client() -> ServiceClient:
    """Cria um ServiceClient apontando para um sidecar fictício."""
    return ServiceClient(
        base_url="https://fake-sidecar",
        dominio="test",
    )


class JsonOrNoneTest(SimpleTestCase):
    """Valida respostas com JSON, texto e corpo vazio."""

    def setUp(self) -> None:
        self.svc = _make_client()

    def test_retorna_none_para_status_204(self) -> None:
        resp = MagicMock()
        resp.status_code = 204
        resp.content = b""

        self.assertIsNone(self.svc.json_or_none(resp))

    def test_retorna_none_para_body_vazio(self) -> None:
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b""

        self.assertIsNone(self.svc.json_or_none(resp))

    def test_retorna_dict_para_json_valido(self) -> None:
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b'{"nome": "Fulano"}'
        resp.json.return_value = {"nome": "Fulano"}

        result = self.svc.json_or_none(resp)

        self.assertEqual(result, {"nome": "Fulano"})

    def test_retorna_texto_quando_body_nao_e_json(self) -> None:
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"<html></html>"
        resp.json.side_effect = ValueError("Not JSON")
        resp.text = "<html></html>"

        result = self.svc.json_or_none(resp)

        self.assertEqual(result, "<html></html>")

    def test_retorna_none_quando_body_nao_e_json_e_text_vazio(self) -> None:
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"   "
        resp.json.side_effect = ValueError("Not JSON")
        resp.text = "   "

        result = self.svc.json_or_none(resp)

        self.assertIsNone(result)


class ServiceClientRequestTest(SimpleTestCase):
    """Valida chamadas HTTP executadas pelo ServiceClient."""

    @patch("apps.core.http_client.build_http_client")
    def test_reaproveita_cliente_http_em_gets(
        self, mock_client: MagicMock
    ) -> None:
        svc = _make_client()

        svc.get("/a")
        svc.get("/b")

        mock_client.assert_called_once_with(
            "test",
            base_url="https://fake-sidecar",
            follow_redirects=True,
        )
        instance = mock_client.return_value
        self.assertEqual(instance.get.call_count, 2)
        instance.get.assert_any_call(
            "/a",
            headers={"Accept": "application/json"},
            params=None,
        )
        instance.get.assert_any_call(
            "/b",
            headers={"Accept": "application/json"},
            params=None,
        )

    @patch("apps.core.http_client.build_http_client")
    def test_close_fecha_cliente_http(self, mock_client: MagicMock) -> None:
        svc = _make_client()
        svc.get("/a")

        svc.close()

        mock_client.return_value.close.assert_called_once_with()

    @patch("apps.core.http_client.build_http_client")
    def test_put_envia_payload_json(self, mock_client: MagicMock) -> None:
        """Verifica o envio de corpo JSON em requisições PUT."""
        svc = _make_client()

        svc.put("/recurso", payload={"ativo": True})

        mock_client.assert_called_once_with(
            "test",
            base_url="https://fake-sidecar",
            follow_redirects=True,
        )
        mock_client.return_value.put.assert_called_once_with(
            "https://fake-sidecar/recurso",
            headers={"Accept": "application/json"},
            json={"ativo": True},
            params=None,
        )

    def test_propaga_request_id_pelo_cliente_do_sdk(self) -> None:
        """Propaga o contexto de correlação para o serviço chamado."""
        seen_headers: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen_headers.update(request.headers)
            return httpx.Response(200)

        svc = _make_client()
        svc._client = build_http_client(  # noqa: SLF001
            "test",
            base_url="https://fake-sidecar",
            transport=httpx.MockTransport(handler),
        )

        with correlation_context(correlation_id="gateway-request-123"):
            svc.get("/a")

        self.assertEqual(
            seen_headers["x-request-id"],
            "gateway-request-123",
        )
