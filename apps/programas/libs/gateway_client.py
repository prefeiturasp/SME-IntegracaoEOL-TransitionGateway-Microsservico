from django.conf import settings

from apps.core.libs.gateway_client import SidecarClient

_client = SidecarClient(settings.SIDECAR_PROGRAMAS_URL, "programas")


def get_client() -> SidecarClient:
    return _client
