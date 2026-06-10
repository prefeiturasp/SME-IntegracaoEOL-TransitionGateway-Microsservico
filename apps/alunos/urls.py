"""Rotas do domínio de alunos."""

from django.urls import path

from apps.alunos.views import (
    AlunoAutocompleteAtivosView,
    AlunoInformacoesView,
    AlunoNecessidadesEspeciaisView,
    AlunosListView,
    AlunoTurmasView,
    InformacoesAlunosTurmaView,
    ResponsavelResumidoView,
)

urlpatterns = [
    path("alunos", AlunosListView.as_view(), name="alunos-list"),
    path(
        "ues/<str:ue_codigo>/autocomplete/ativos",
        AlunoAutocompleteAtivosView.as_view(),
        name="aluno-autocomplete-ativos",
    ),
    path(
        "responsaveis/<str:cpf_responsavel>/resumido",
        ResponsavelResumidoView.as_view(),
        name="aluno-responsavel-resumido",
    ),
    path(
        "<str:codigo_turma>/turma/informacoes",
        InformacoesAlunosTurmaView.as_view(),
        name="informacoes-alunos-turma",
    ),
    path(
        "<str:codigo_aluno>/informacoes",
        AlunoInformacoesView.as_view(),
        name="aluno-informacoes",
    ),
    path(
        "<str:codigo_aluno>/necessidades-especiais",
        AlunoNecessidadesEspeciaisView.as_view(),
        name="aluno-necessidades-especiais",
    ),
    path(
        "<str:codigo_aluno>/turmas",
        AlunoTurmasView.as_view(),
        name="aluno-turmas",
    ),
    path(
        "<str:codigo_aluno>/turmas/",
        AlunoTurmasView.as_view(),
        name="aluno-turmas-com-barra",
    ),
]
