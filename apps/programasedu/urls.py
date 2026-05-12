"""Mapeamento das rotas legadas do domínio programas educacionais."""

from django.urls import path

from apps.programasedu.views import (
    ObterAlunosPapAnoCorrenteView,
    ObterAlunosPapPorAnoLetivoView,
    ObterTurmasPapView,
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
]
