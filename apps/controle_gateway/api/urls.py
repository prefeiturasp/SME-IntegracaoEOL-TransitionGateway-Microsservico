from django.urls import path

from apps.controle_gateway.api.views import GatewayHealthView

urlpatterns = [
    path(
        "gateway/health/",
        GatewayHealthView.as_view(),
        name="gateway-health",
    ),
]
