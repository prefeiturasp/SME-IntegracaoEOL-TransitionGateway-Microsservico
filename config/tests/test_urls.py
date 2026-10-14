"""Valida o roteamento principal do gateway."""

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class AbrangenciaRemovidaTest(SimpleTestCase):
    """Garante que o dominio Abrangencia nao e mais servido pelo gateway."""

    def test_rota_post_estrutura_vigente_nao_existe(self) -> None:
        """A rota de estrutura vigente por turmas nao resolve no gateway."""
        with self.assertRaises(Resolver404):
            resolve("/api/abrangencia/estrutura-vigente")

    def test_rota_get_estrutura_vigente_por_dre_nao_existe(self) -> None:
        """A rota de estrutura vigente por DRE nao resolve no gateway."""
        with self.assertRaises(Resolver404):
            resolve("/api/abrangencia/estrutura-vigente/108100")

    def test_app_abrangencia_nao_esta_instalado(self) -> None:
        """O app de abrangencia nao consta nos apps instalados."""
        self.assertNotIn("apps.abrangencia", settings.INSTALLED_APPS)
