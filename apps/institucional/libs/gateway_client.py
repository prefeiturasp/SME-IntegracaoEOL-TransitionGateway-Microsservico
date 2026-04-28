from django.conf import settings

from apps.core.libs.gateway_client import SidecarClient

_client = SidecarClient(settings.SIDECAR_INSTITUCIONAL_URL, "institucional")


def get_client() -> SidecarClient:
    return _client
