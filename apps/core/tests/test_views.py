"""Valida bases de views compartilhadas."""

import httpx
from django.test import SimpleTestCase
from rest_framework import status

from apps.core.views import DomainAPIView


class DomainAPIViewTest(SimpleTestCase):
    """Valida tratamento centralizado de falhas de transporte."""

    def test_converte_request_error_em_503_do_dominio(self) -> None:
        class AlunosAPIView(DomainAPIView):
            api_domain = "alunos"

        response = AlunosAPIView().handle_exception(
            httpx.ConnectError("erro de conexao")
        )

        self.assertEqual(
            response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE
        )
        self.assertEqual(
            response.data,
            {"detail": "Serviço de alunos indisponível."},
        )
