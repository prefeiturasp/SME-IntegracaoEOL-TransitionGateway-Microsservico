from django.urls import path

from apps.programas.api.views import HealthProgramasView, ProgramasProxyView

urlpatterns = [
    path(
        "programas/health/",
        HealthProgramasView.as_view(),
        name="programas-health",
    ),
    path(
        "eol/programas/<path:path>",
        ProgramasProxyView.as_view(),
        name="programas-proxy",
    ),
]
