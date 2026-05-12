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
        "alunos/turmas-pap/<int:anoLetivo>/ues/<str:codigoEscola>/",
        ObterTurmasPapView.as_view(),
        name="obter-turmas-pap",
    ),
    path(
        "alunos/alunos-pap/<int:anoLetivo>/",
        VerificarSeAlunosSaoTurmaProgramaPapView.as_view(),
        name="verificar-alunos-turma-pap",
    ),
    path(
        "alunos/pap/ano-corrente/",
        ObterAlunosPapAnoCorrenteView.as_view(),
        name="obter-alunos-pap-ano-corrente",
    ),
    path(
        "alunos/pap/ano-letivo/<int:anoLetivo>/",
        ObterAlunosPapPorAnoLetivoView.as_view(),
        name="obter-alunos-pap-por-ano-letivo",
    ),
]
