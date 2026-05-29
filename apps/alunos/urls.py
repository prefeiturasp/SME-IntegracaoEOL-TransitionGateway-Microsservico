"""Rotas do domínio de alunos."""

from django.urls import path, re_path

from apps.alunos.views import (
    AlunoInformacoesView,
    AlunoNecessidadesEspeciaisView,
    AlunosListView,
    AlunoTurmasLegadoView,
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
    re_path(
        r"^(?P<codigo_aluno>[^/]+)/turmas/anosLetivos/"
        r"(?P<ano_letivo>[^/]+)/historico/(?P<historico>[^/]+)/"
        r"filtrar-situacao/(?P<filtrar_situacao>[^/]+)/"
        r"tipo-turma/(?P<tipo_turma>[^/]+)$",
        AlunoTurmasLegadoView.as_view(),
        name="aluno-turmas-com-filtros",
    ),
]
