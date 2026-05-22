"""Valida a conversão de respostas HTTP em dados Python."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.core.http_client import ServiceClient


def _make_client() -> ServiceClient:
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
