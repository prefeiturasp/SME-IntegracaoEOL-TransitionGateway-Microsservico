"""Mapeamento das rotas legadas L1–L17 para as views do domínio pedagógico."""

from django.urls import path

from apps.pedagogico.views import (
    AgrupamentosCorrelacionadosLoteView,
    AgrupamentosCorrelacionadosView,
    AgrupamentosTerritorioView,
    AnoTurmaAnoLetivoView,
    CatalogoComponentesView,
    ComponentesFuncionarioComTurmaView,
    ComponentesFuncionarioView,
    ComponentesPlanejamentoFuncionarioView,
    ComponentesPlanejamentoView,
    ComponentesPorTurmasUeView,
    ComponentesRegenciaView,
    ComponentesRegularesView,
    ComponentesSemAtribuicaoView,
    ComponentesUeAnosEscolaresView,
    ComponentesUeModalidadeView,
    DadosAulaTurmaView,
    ValidarPapView,
)

urlpatterns = [
    # legado 1
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:id_perfil>"
        "/agrupaComponenteCurricular/<str:flag>/",
        ComponentesFuncionarioComTurmaView.as_view(),
    ),
    # legado 2
    path(
        "funcionarios/<str:login>/perfis/<str:id_perfil>/",
        ComponentesFuncionarioView.as_view(),
    ),
    # legado 3
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:id_perfil>/planejamento/",
        ComponentesPlanejamentoFuncionarioView.as_view(),
    ),
    # legado 4
    path(
        "anos/<int:ano_turma>/regencia/",
        ComponentesRegenciaView.as_view(),
    ),
    # legado 5
    path(
        "turmas/<str:cod>/funcionarios/<str:login>"
        "/perfis/<str:id_perfil>/validar/pap/",
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
    # legado 13
    path(
        "<int:codigo_componente>"
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
    # legado 16
    path(
        "ano-turma/ano-letivo/<int:ano_letivo>/",
        AnoTurmaAnoLetivoView.as_view(),
    ),
    # legado 17
    path(
        "turmas/<str:cod>/sem-atribuicao/<str:data_base_tick>/",
        ComponentesSemAtribuicaoView.as_view(),
    ),
]
