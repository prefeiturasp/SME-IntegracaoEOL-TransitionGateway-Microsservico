from django.conf import settings

from apps.core.libs.gateway_client import SidecarClient

_client = SidecarClient(settings.SIDECAR_ALUNOS_URL, "alunos")


def get_client() -> SidecarClient:
    return _client
