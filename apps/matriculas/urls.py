"""Rotas do domínio de matrículas."""

from django.urls import path

from apps.matriculas.views import (
    MatriculasAlunoEscolaView,
    MatriculasAnoAtualView,
    MatriculasAnosAnterioresView,
    QuantidadeAlunosPorTurmaEscolaView,
    TotalMatriculasPorTurnoDreView,
    TotalMatriculasPorTurnoUeView,
)

urlpatterns = [
    path("", MatriculasAnoAtualView.as_view(), name="matriculas-list"),
    path(
        "anos-anteriores",
        MatriculasAnosAnterioresView.as_view(),
        name="matriculas-anos-anteriores",
    ),
    path(
        "escolas/<str:ue_codigo>/quantidades",
        TotalMatriculasPorTurnoUeView.as_view(),
        name="matriculas-quantidades-ue",
    ),
    path(
        "escolas/dre/<str:dre_codigo>/quantidades",
        TotalMatriculasPorTurnoDreView.as_view(),
        name="matriculas-quantidades-dre",
    ),
]


escola_urlpatterns = [
    path(
        "<str:codigo_escola>/alunos/quantidade/",
        QuantidadeAlunosPorTurmaEscolaView.as_view(),
        name="quantidade-alunos-por-turma-escola",
    ),
    path(
        "<str:codigo_escola>/alunos/<str:codigo_aluno>/matriculas/",
        MatriculasAlunoEscolaView.as_view(),
        name="matriculas-aluno-escola",
    ),
]
