"""Configuração do app professores."""

from django.apps import AppConfig


class ProfessoresConfig(AppConfig):
    """App de tradução dos contratos legados de professores."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.professores"
    verbose_name = "Professores"
