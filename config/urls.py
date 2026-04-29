from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from config import settings

API_PREFIX = "api/v1/"

DOMAINS = {
    "pedagogico": settings.SIDECAR_PEDAGOGICO_URL,
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
]


# urlpatterns += [
#     path(
#         f"{API_PREFIX}{dominio}/health/",
#         DomainHealthView.as_view(dominio=dominio, sidecar_url=url),
#     )
#     for dominio, url in DOMAINS.items()
# ]

# urlpatterns += [
#     path(
#         f"{API_PREFIX}eol/{dominio}/<path:path>",
#         DomainProxyView.as_view(dominio=dominio, sidecar_url=url),
#     )
#     for dominio, url in DOMAINS.items()
# ]
