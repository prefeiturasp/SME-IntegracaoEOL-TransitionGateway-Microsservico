"""Rotas do domínio de abrangência."""

from django.urls import path

from apps.abrangencia.views import (
    EstruturaVigentePorDreView,
    EstruturaVigenteView,
)

urlpatterns = [
    path(
        "abrangencia/estrutura-vigente/",
        EstruturaVigenteView.as_view(),
        name="abrangencia-estrutura-vigente",
    ),
    path(
        "abrangencia/estrutura-vigente/<str:codigo_dre>/",
        EstruturaVigentePorDreView.as_view(),
        name="abrangencia-estrutura-vigente-por-dre",
    ),
]
