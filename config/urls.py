"""Roteamento principal: schema, docs e domínios."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.alunos.urls import turma_urlpatterns as alunos_turma_urlpatterns
from apps.matriculas.urls import escola_urlpatterns as matriculas_escola_urlpatterns
from apps.pedagogico.urls import turma_urlpatterns, ue_urlpatterns
from config import settings

API_PREFIX = "api/v1/"

DOMAINS = {
    "pedagogico": settings.SIDECAR_PEDAGOGICO_URL,
    "professores": settings.SIDECAR_PROFESSORES_URL,
    "institucional": settings.SIDECAR_INSTITUCIONAL_URL,
    "programasedu": settings.SIDECAR_PROGRAMASEDU_URL,
    "alunos": settings.SIDECAR_ALUNOS_URL,
    "matriculas": settings.SIDECAR_ALUNOS_URL,
}


urlpatterns = [
    path(
        f"{API_PREFIX}schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        f"{API_PREFIX}docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(
        f"{API_PREFIX}componentes-curriculares/",
        include("apps.pedagogico.urls"),
    ),
    path(
        "api/turmas/",
        include((alunos_turma_urlpatterns, "alunos-turmas")),
    ),
    path(
        "api/escolas/",
        include((matriculas_escola_urlpatterns, "matriculas-escolas")),
    ),
    path("api/turmas/", include((turma_urlpatterns, "turmas"))),
    path("api/", include((ue_urlpatterns, "ues"))),
    path("api/", include("apps.professores.urls")),
    path("api/", include("apps.institucional.urls")),
    path("api/", include("apps.programasedu.urls")),
    path("api/matriculas/", include("apps.matriculas.urls")),
    path(f"{API_PREFIX}alunos/", include("apps.alunos.urls")),
    path(f"{API_PREFIX}matriculas/", include("apps.matriculas.urls")),
]
