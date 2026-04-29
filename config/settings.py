import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.pedagogico",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.RequestIDMiddleware",
    "apps.core.middleware.LoggingContextMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

API_KEY = os.getenv("API_KEY", "dev-key-default")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "config.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Gateway EOL",
    "DESCRIPTION": "Porta de entrada única para os domínios internos.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}

SIDECAR_PEDAGOGICO_URL = os.getenv(
    "SIDECAR_PEDAGOGICO_URL", "http://localhost:9004"
)

GATEWAY_TIMEOUT_SECONDS = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "10"))


ELASTIC_APM = {
    "SERVICE_NAME": os.getenv("ELASTIC_APM_SERVICE_NAME", "transition-gateway"),
    "SERVER_URL": os.getenv("ELASTIC_APM_SERVER_URL", "http://localhost:8200"),
    "SECRET_TOKEN": os.getenv("ELASTIC_APM_SECRET_TOKEN", ""),
    "ENVIRONMENT": os.getenv("ELASTIC_APM_ENVIRONMENT", "local"),
    "ENABLED": os.getenv("ELASTIC_APM_ENABLED", "1") == "1",
    "DEBUG": os.getenv("ELASTIC_APM_DEBUG", "1" if DEBUG else "0") == "1",
    "CAPTURE_HEADERS": os.getenv("ELASTIC_APM_CAPTURE_HEADERS", "1") == "1",
    "TRANSACTION_SAMPLE_RATE": float(
        os.getenv("ELASTIC_APM_TRANSACTION_SAMPLE_RATE", "0.3")
    ),
    "METRICS_INTERVAL": os.getenv("ELASTIC_APM_METRICS_INTERVAL", "10s"),
    "FLUSH_INTERVAL": os.getenv("ELASTIC_APM_FLUSH_INTERVAL", "10s"),
    "MAX_BATCH_EVENT_COUNT": int(
        os.getenv("ELASTIC_APM_MAX_BATCH_EVENT_COUNT", "1000")
    ),
    "MAX_QUEUE_EVENT_COUNT": int(
        os.getenv("ELASTIC_APM_MAX_QUEUE_EVENT_COUNT", "1000")
    ),
    "TRANSACTION_MAX_SPANS": int(
        os.getenv("ELASTIC_APM_TRANSACTION_MAX_SPANS", "500")
    ),
    "LOG_LEVEL": os.getenv("ELASTIC_APM_LOG_LEVEL", "INFO"),
}
