"""Configuração da app core."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configura o app compartilhado core."""

    name = "apps.core"
    label = "core"

    def ready(self) -> None:
        """Inicializa resiliência e observabilidade no boot do processo."""
        from sme_sidecar_sdk import runtime

        runtime.configure()
