from django.urls import path

from apps.institucional.api.views import (
    HealthInstitucionalView,
    InstitucionalProxyView,
)

urlpatterns = [
    path(
        "institucional/health/",
        HealthInstitucionalView.as_view(),
        name="institucional-health",
    ),
    # <path:path> captura qualquer sub-rota do contrato EOL
    path(
        "eol/institucional/<path:path>",
        InstitucionalProxyView.as_view(),
        name="institucional-proxy",
    ),
]
