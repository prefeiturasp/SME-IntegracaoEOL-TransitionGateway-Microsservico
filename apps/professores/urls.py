"""Mapeamento das rotas legadas do domínio professores."""

from django.urls import path

from apps.professores.views import (
    FuncionarioAtivoView,
    NomeServidorView,
    ProfessorView,
    ValidadeProfessorView,
)

urlpatterns = [
    path(
        "professores/<str:codigo_rf>/validade/",
        ValidadeProfessorView.as_view(),
    ),
    path(
        "professores/<str:rf_professor>/",
        ProfessorView.as_view(),
    ),
    path(
        "acessos/funcionario-ativo/<str:registro_funcional>/",
        FuncionarioAtivoView.as_view(),
    ),
    path(
        "funcionarios/nome-servidor/<str:registro_funcional>/",
        NomeServidorView.as_view(),
    ),
]
