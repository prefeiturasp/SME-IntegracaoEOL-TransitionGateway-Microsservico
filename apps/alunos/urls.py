"""Rotas do domínio de alunos."""

from django.urls import path

from apps.alunos.views import (
    AlunoInformacoesView,
    AlunoNecessidadesEspeciaisView,
    AlunosListView,
    AlunoTurmasView,
)

urlpatterns = [
    path("alunos", AlunosListView.as_view(), name="alunos-list"),
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
