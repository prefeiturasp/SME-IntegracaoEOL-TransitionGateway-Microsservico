from django.urls import path
from apps.pedagogico.views import (
    ComponentesFuncionarioComTurmaView,
    ComponentesFuncionarioView,
    ComponentesPlanejamentoFuncionarioView,
    ComponentesRegenciaView,
    ValidarPapView,
    ComponentesUeAnosEscolaresView,
    ComponentesUeModalidadeView,
    ComponentesPorTurmasUeView,
    ComponentesPlanejamentoView,
    ComponentesRegularesView,
    CatalogoComponentesView,
    DadosAulaTurmaView,
    AnoTurmaAnoLetivoView,
    ComponentesSemAtribuicaoView,
    AgrupamentosCorrelacionadosView,
    AgrupamentosCorrelacionadosLoteView,
    AgrupamentosTerritorioView,
)

urlpatterns = [
    # legado 1
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:idPerfil>"
        "/agrupaComponenteCurricular/<str:flag>/",
        ComponentesFuncionarioComTurmaView.as_view(),
    ),
    # legado 2
    path(
        "funcionarios/<str:login>/perfis/<str:idPerfil>/",
        ComponentesFuncionarioView.as_view(),
    ),
    # legado 3
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:idPerfil>/planejamento/",
        ComponentesPlanejamentoFuncionarioView.as_view(),
    ),
    # legado 4
    path(
        "anos/<int:anoTurma>/regencia/",
        ComponentesRegenciaView.as_view(),
    ),
    # legado 5
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:idPerfil>/validar/pap/",
        ValidarPapView.as_view(),
    ),
    # legado 6
    path(
        "ues/<str:id>/modalidades/<int:mod>/anos/<int:ano>/anos-escolares/",
        ComponentesUeAnosEscolaresView.as_view(),
    ),
    # legado 7
    path(
        "ues/<str:id>/modalidades/<int:mod>/anos/<int:ano>/",
        ComponentesUeModalidadeView.as_view(),
    ),
    # legado 8
    path(
        "ues/<str:id>/turmas/",
        ComponentesPorTurmasUeView.as_view(),
    ),
    # legado 9
    path(
        "turmas/",
        ComponentesPlanejamentoView.as_view(),
    ),
    # legado 10
    path(
        "turmas/regulares/",
        ComponentesRegularesView.as_view(),
    ),
    # legado 11
    path(
        "",
        CatalogoComponentesView.as_view(),
    ),
    # legado 12
    path(
        "dados-aula-turma/",
        DadosAulaTurmaView.as_view(),
    ),
    # legado 16
    path(
        "ano-turma/ano-letivo/<int:anoLetivo>/",
        AnoTurmaAnoLetivoView.as_view(),
    ),
    # legado 17
    path(
        "turmas/<str:cod>/sem-atribuicao/<str:dataBaseTick>/",
        ComponentesSemAtribuicaoView.as_view(),
    ),
    # legado 13
    path(
        "<int:codigoComponente>"
        "/territorio-saber/agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosView.as_view(),
    ),
    # legado 14
    path(
        "territorio-saber/agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosLoteView.as_view(),
    ),
    # legado 15
    path(
        "territorio-saber/agrupamentos/",
        AgrupamentosTerritorioView.as_view(),
    ),
]
