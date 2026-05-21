"""Valida a conversão de respostas HTTP em dados Python."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.core import logging_context
from apps.core.http_client import ServiceClient


def _make_client() -> ServiceClient:
    return ServiceClient(
        base_url="https://fake-sidecar",
        dominio="test",
    )


class ServiceClientTest(SimpleTestCase):
    """Valida chamadas HTTP e health check."""

    @patch("apps.core.http_client.httpx.Client")
    def test_get_envia_headers_e_params(
        self, mock_client_cls: MagicMock
    ) -> None:
        token = logging_context.request_id_ctx.set("req-1")
        svc = ServiceClient(
            base_url="https://fake-sidecar/",
            dominio="test",
            api_key="secret",
            api_key_header="X-Test-Key",
        )
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response

        result = svc.get("/path", params={"a": "b"})
        logging_context.request_id_ctx.reset(token)

        self.assertEqual(result, mock_response)
        mock_client.get.assert_called_once_with(
            "https://fake-sidecar/path",
            headers={
                "Accept": "application/json",
                "X-Request-ID": "req-1",
                "X-Test-Key": "secret",
            },
            params={"a": "b"},
            follow_redirects=True,
        )

    @patch("apps.core.http_client.httpx.Client")
    def test_post_envia_payload_e_params(
        self, mock_client_cls: MagicMock
    ) -> None:
        svc = _make_client()
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_client.post.return_value = mock_response

        result = svc.post("/path", payload={"x": 1}, params={"a": "b"})

        self.assertEqual(result, mock_response)
        mock_client.post.assert_called_once_with(
            "https://fake-sidecar/path",
            headers={"Accept": "application/json", "X-Request-ID": "-"},
            json={"x": 1},
            params={"a": "b"},
            follow_redirects=True,
        )

    @patch("apps.core.http_client.httpx.Client")
    def test_is_healthy_retorna_true_para_status_menor_500(
        self, mock_client_cls: MagicMock
    ) -> None:
        svc = _make_client()
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.return_value = MagicMock(status_code=204)

        self.assertTrue(svc.is_healthy())

        mock_client.get.assert_called_once_with(
            "https://fake-sidecar/health/",
            headers={"Accept": "application/json", "X-Request-ID": "-"},
        )

    @patch("apps.core.http_client.httpx.Client")
    def test_is_healthy_retorna_false_para_status_500(
        self, mock_client_cls: MagicMock
    ) -> None:
        svc = _make_client()
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.get.return_value = MagicMock(status_code=500)

        self.assertFalse(svc.is_healthy())

    @patch("apps.core.http_client.httpx.Client")
    def test_is_healthy_retorna_false_quando_falha(
        self, mock_client_cls: MagicMock
    ) -> None:
        svc = _make_client()
        mock_client_cls.side_effect = RuntimeError("offline")

        self.assertFalse(svc.is_healthy())


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
