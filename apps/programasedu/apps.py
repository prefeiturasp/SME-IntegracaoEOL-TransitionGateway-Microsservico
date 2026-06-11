"""Configuração do app de programas educacionais."""

from django.apps import AppConfig


class ProgramasEduConfig(AppConfig):
    """Configura o app de programas educacionais."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programasedu"
    verbose_name = "Programas Educacionais"
