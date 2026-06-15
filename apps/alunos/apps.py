"""Configuração do app de alunos."""

from django.apps import AppConfig


class AlunosConfig(AppConfig):
    """Configura o app de alunos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.alunos"
    verbose_name = "Alunos"
