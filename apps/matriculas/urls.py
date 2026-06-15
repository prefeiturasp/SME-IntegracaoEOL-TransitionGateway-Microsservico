"""Rotas do domínio de matrículas."""

from django.urls import path

from apps.matriculas.views import MatriculasAnoAtualView

urlpatterns = [
    path("", MatriculasAnoAtualView.as_view(), name="matriculas-list"),
]
