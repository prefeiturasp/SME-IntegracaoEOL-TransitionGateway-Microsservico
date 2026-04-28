from rest_framework import serializers


class HealthStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    dominio = serializers.CharField(required=False)
    sidecar_url = serializers.CharField(required=False)
