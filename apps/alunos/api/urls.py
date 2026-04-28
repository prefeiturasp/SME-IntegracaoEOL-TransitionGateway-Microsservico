from django.urls import path

from apps.alunos.api.views import AlunosProxyView, HealthAlunosView

urlpatterns = [
    path(
        "alunos/health/",
        HealthAlunosView.as_view(),
        name="alunos-health",
    ),
    path(
        "eol/alunos/<path:path>",
        AlunosProxyView.as_view(),
        name="alunos-proxy",
    ),
]
