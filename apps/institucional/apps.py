"""Configuração do app institucional."""

from django.apps import AppConfig


class InstitucionalConfig(AppConfig):
    """Configura o app de gateway para o domínio institucional."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institucional"
    verbose_name = "Institucional"
