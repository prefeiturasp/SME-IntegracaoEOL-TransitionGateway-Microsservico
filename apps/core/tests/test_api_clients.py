"""Valida o registry de clientes das APIs de domínio."""

from typing import cast

from django.test import SimpleTestCase

from apps.core.api_clients import DomainName, close_api_clients, get_api_client


class ApiClientsTest(SimpleTestCase):
    """Valida a separação de clientes por domínio."""

    def tearDown(self) -> None:
        close_api_clients()

    def test_reaproveita_cliente_do_mesmo_dominio(self) -> None:
        """Retorna a mesma instância em chamadas repetidas do domínio."""
        primeiro = get_api_client("pedagogico")
        segundo = get_api_client("pedagogico")

        self.assertIs(primeiro, segundo)

    def test_cria_clientes_distintos_por_dominio(self) -> None:
        """Mantém nomes lógicos separados para circuit breakers."""
        pedagogico = get_api_client("pedagogico")
        professores = get_api_client("professores")
        institucional = get_api_client("institucional")

        self.assertIsNot(pedagogico, professores)
        self.assertIsNot(pedagogico, institucional)
        self.assertEqual(pedagogico.dominio, "pedagogico")
        self.assertEqual(professores.dominio, "professores")
        self.assertEqual(institucional.dominio, "institucional")

    def test_matriculas_nao_e_dominio_de_client(self) -> None:
        """Matrículas deve ser atendido pelo client da API de alunos."""
        with self.assertRaises(KeyError):
            get_api_client(cast(DomainName, "matriculas"))
