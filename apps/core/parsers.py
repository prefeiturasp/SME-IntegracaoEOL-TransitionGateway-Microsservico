"""Parsers compartilhados pelas APIs do gateway."""

from rest_framework.parsers import JSONParser


class JsonPatchParser(JSONParser):
    """Processa payload ``application/json-patch+json`` como JSON."""

    media_type = "application/json-patch+json"
