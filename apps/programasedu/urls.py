"""Rotas do domínio de programas educacionais."""

from django.urls import path

from apps.programasedu.views import (
    ObterAlunosPapAnoCorrenteView,
    ObterAlunosPapPorAnoLetivoView,
    ObterComponentesCurricularesTurmasProgramaAlunoView,
    ObterDadosSrmPaeeAlunoView,
    ObterTurmasPapView,
    ObterTurmaSrmERegularDoAlunoView,
    VerificarSeAlunosSaoTurmaProgramaPapView,
)

urlpatterns = [
    path(
        "alunos/turmas-pap/<int:ano_letivo>/ues/<str:codigo_escola>/",
        ObterTurmasPapView.as_view(),
        name="obter-turmas-pap",
    ),
    path(
        "alunos/alunos-pap/<int:ano_letivo>/",
        VerificarSeAlunosSaoTurmaProgramaPapView.as_view(),
        name="verificar-alunos-turma-pap",
    ),
    path(
        "alunos/pap/ano-corrente/",
        ObterAlunosPapAnoCorrenteView.as_view(),
        name="obter-alunos-pap-ano-corrente",
    ),
    path(
        "alunos/pap/ano-letivo/<int:ano_letivo>/",
        ObterAlunosPapPorAnoLetivoView.as_view(),
        name="obter-alunos-pap-por-ano-letivo",
    ),
    path(
        "alunos/<str:codigo_aluno>/turmas-programa/<int:ano_letivo>"
        "/componentes-curriculares/",
        ObterComponentesCurricularesTurmasProgramaAlunoView.as_view(),
        name="obter-componentes-turmas-programa-aluno",
    ),
    path(
        "alunos/srm-paee/aluno/<str:codigo_aluno>/",
        ObterDadosSrmPaeeAlunoView.as_view(),
        name="obter-dados-srm-paee-aluno",
    ),
    path(
        "alunos/paee/turma-srm-e-regular/aluno/<str:codigo_aluno>/",
        ObterTurmaSrmERegularDoAlunoView.as_view(),
        name="obter-turma-srm-e-regular-do-aluno",
    ),
]
