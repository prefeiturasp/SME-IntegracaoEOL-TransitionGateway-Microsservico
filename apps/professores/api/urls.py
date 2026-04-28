from django.urls import path

from apps.professores.api.views import (
    HealthProfessoresView,
    ProfessoresProxyView,
)

urlpatterns = [
    path(
        "professores/health/",
        HealthProfessoresView.as_view(),
        name="professores-health",
    ),
    path(
        "eol/professores/<path:path>",
        ProfessoresProxyView.as_view(),
        name="professores-proxy",
    ),
]
