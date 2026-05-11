"""Testes de responses do core."""

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.response import Response as DrfResponse

from apps.core.responses import Response, detail_response


class DetailResponseTest(SimpleTestCase):
    """Testes de `detail_response`."""

    def test_exporta_response_do_drf(self) -> None:
        self.assertIs(Response, DrfResponse)

    def test_retorna_detail_com_status_padrao_400(self) -> None:
        response = detail_response("Campo obrigatorio.")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Campo obrigatorio."})

    def test_permite_status_customizado(self) -> None:
        response = detail_response(
            "Nao encontrado.",
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Nao encontrado."})
