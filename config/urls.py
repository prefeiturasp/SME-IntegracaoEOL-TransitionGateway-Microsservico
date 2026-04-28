from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

_API_V1 = "api/v1/"

urlpatterns = [
    path(
        f"{_API_V1}schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        f"{_API_V1}docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(_API_V1, include("apps.controle_gateway.api.urls")),
    path(_API_V1, include("apps.institucional.api.urls")),
    path(_API_V1, include("apps.professores.api.urls")),
    path(_API_V1, include("apps.alunos.api.urls")),
    path(_API_V1, include("apps.pedagogico.api.urls")),
    path(_API_V1, include("apps.programas.api.urls")),
]
