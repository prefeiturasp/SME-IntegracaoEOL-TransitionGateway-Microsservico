"""Configuração do app de professores."""

from django.apps import AppConfig


class ProfessoresConfig(AppConfig):
    """Configura o app de professores."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.professores"
    verbose_name = "Professores"
