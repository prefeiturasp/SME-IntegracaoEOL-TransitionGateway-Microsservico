"""Roteamento principal: schema, docs e domínios."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from config import settings

API_PREFIX = "api/v1/"

DOMAINS = {
    "pedagogico": settings.SIDECAR_PEDAGOGICO_URL,
    "professores": settings.SIDECAR_PROFESSORES_URL,
    "institucional": settings.SIDECAR_INSTITUCIONAL_URL,
    "programasedu": settings.SIDECAR_PROGRAMASEDU_URL,
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
    path("api/", include("apps.professores.urls")),
    path("api/", include("apps.institucional.urls")),
    path("api/", include("apps.programasedu.urls")),
]
