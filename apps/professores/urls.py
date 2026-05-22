"""Rotas do domínio de professores."""

from django.urls import path

from apps.professores.views import (
    EscolaFuncionariosCargoView,
    EscolaFuncionariosView,
    FuncionarioAtivoView,
    FuncionariosBuscarPorListaRfView,
    NomeServidorView,
    NomeUsuarioEolView,
    ProfessorBuscarPorRfView,
    ProfessorDisciplinaTurmasView,
    ProfessorView,
    ValidadeProfessorView,
)


urlpatterns = [
    path(
        "professores/<str:codigo_rf>/BuscarPorRf/<int:ano_letivo>/",
        ProfessorBuscarPorRfView.as_view(),
    ),
    path(
        f"professores/<str:codigo_rf>/disciplina/<str:disciplina_id>/turmas/",
        ProfessorDisciplinaTurmasView.as_view(),
    ),
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
    path(
        "funcionarios/nome-usuario-eol/<str:registro_funcional>/",
        NomeUsuarioEolView.as_view(),
    ),
    path(
        "funcionarios/BuscarPorListaRF/",
        FuncionariosBuscarPorListaRfView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/cargos/<str:codigo_cargo>/",
        EscolaFuncionariosCargoView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/",
        EscolaFuncionariosView.as_view(),
    ),
]
