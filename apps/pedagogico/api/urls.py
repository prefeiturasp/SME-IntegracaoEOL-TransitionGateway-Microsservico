from django.urls import path

from apps.pedagogico.api.views import HealthPedagogicoView, PedagogicoProxyView

urlpatterns = [
    path(
        "pedagogico/health/",
        HealthPedagogicoView.as_view(),
        name="pedagogico-health",
    ),
    path(
        "eol/pedagogico/<path:path>",
        PedagogicoProxyView.as_view(),
        name="pedagogico-proxy",
    ),
]
