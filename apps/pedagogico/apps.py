from django.apps import AppConfig


class PedagogicoConfig(AppConfig):
    """Configura o app Django do domínio pedagógico."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pedagogico"
    verbose_name = "Pedagogico"
