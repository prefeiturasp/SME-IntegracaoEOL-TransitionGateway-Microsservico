# Configuração da app institucional no TransitionGateway.
# Registrada em INSTALLED_APPS como 'apps.institucional'.
# Este app atua como gateway proxy para o sidecar institucional

from django.apps import AppConfig


class InstitucionalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institucional"
    verbose_name = "Institucional"
