"""Rotas do domínio de matrículas."""

from django.urls import path

from apps.matriculas.views import (
    MatriculasAnoAtualView,
    MatriculasAnosAnterioresView,
)

urlpatterns = [
    path("", MatriculasAnoAtualView.as_view(), name="matriculas-list"),
    path(
        "anos-anteriores",
        MatriculasAnosAnterioresView.as_view(),
        name="matriculas-anos-anteriores",
    ),
]
