"""Rotas do domínio pedagógico."""

from django.urls import path

from apps.pedagogico.views import (
    ComponentesCurricularesViewSet,
    ComponentesFuncionarioViewSet,
    ComponentesPlanejamentoViewSet,
    ComponentesPorListaTurmasViewSet,
    ComponentesRegenciaViewSet,
    ComponentesSemAtribuicaoViewSet,
    ComponentesTurmaAnoViewSet,
    ComponentesTurmaFuncionarioViewSet,
    ComponentesTurmaProgramaViewSet,
    ComponentesTurmasRegularesViewSet,
    ComponentesTurmaViewSet,
    DadosAulaTurmaViewSet,
    DadosTurmaViewSet,
    GradeComponentesCurricularesViewSet,
    ListarTurmasViewSet,
    TurmasProgramaViewSet,
    TurmasRegularesViewSet,
    ValidarComponentePapViewSet,
)

turma_urlpatterns = [
    path(
        "turmas-regulares/",
        TurmasRegularesViewSet.as_view(),
    ),
    path(
        "turmas-programa/",
        TurmasProgramaViewSet.as_view(),
    ),
    path(
        "listar-turmas/",
        ListarTurmasViewSet.as_view(),
    ),
    path(
        "<str:codigo_turma>/dados/",
        DadosTurmaViewSet.as_view(),
    ),
]

urlpatterns = [
    path(
        "turmas/regulares/",
        ComponentesTurmasRegularesViewSet.as_view(),
    ),
    path(
        "turmas/",
        ComponentesPorListaTurmasViewSet.as_view(),
    ),
    path(
        "dados-aula-turma/",
        DadosAulaTurmaViewSet.as_view(),
    ),
    path(
        "anos/<int:ano_turma>/regencia/",
        ComponentesRegenciaViewSet.as_view(),
    ),
    path(
        "turmas/<str:codigo_turma>/funcionarios/<str:login>/"
        "perfis/<str:id_perfil>/agrupaComponenteCurricular/"
        "<str:agrupa_componente_curricular>/",
        ComponentesTurmaFuncionarioViewSet.as_view(),
    ),
    path(
        "turmas/<str:codigo_turma>/funcionarios/<str:login>/"
        "perfis/<str:id_perfil>/planejamento/",
        ComponentesPlanejamentoViewSet.as_view(),
    ),
    path(
        "turmas/<str:codigo_turma>/sem-atribuicao/" "<int:data_base_tick>/",
        ComponentesSemAtribuicaoViewSet.as_view(),
    ),
    path(
        "turmas/<str:codigo_turma>/funcionarios/<str:login>/"
        "perfis/<str:id_perfil>/validar/pap/",
        ValidarComponentePapViewSet.as_view(),
    ),
    path(
        "funcionarios/<str:login>/perfis/<str:id_perfil>/",
        ComponentesFuncionarioViewSet.as_view(),
    ),
    path(
        "ues/<str:ue_id>/modalidades/<int:modalidade>/anos/<int:ano_letivo>/anos-escolares/",
        ComponentesTurmaAnoViewSet.as_view(),
    ),
    path(
        "ues/<str:ue_id>/modalidades/<int:modalidade>/anos/<int:ano_letivo>/",
        ComponentesTurmaProgramaViewSet.as_view(),
    ),
    path(
        "ues/<str:ue_id>/turmas/",
        ComponentesTurmaViewSet.as_view(),
    ),
    path(
        "ano-turma/ano-letivo/<int:ano_letivo>/",
        GradeComponentesCurricularesViewSet.as_view(),
    ),
    path(
        "",
        ComponentesCurricularesViewSet.as_view(),
    ),
]
