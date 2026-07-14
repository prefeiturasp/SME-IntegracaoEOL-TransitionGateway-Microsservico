"""Rotas do domínio pedagógico."""

from django.urls import path

from apps.pedagogico.views import (
    AgrupamentosCorrelacionadosLoteViewSet,
    AgrupamentosCorrelacionadosViewSet,
    AgrupamentosTerritorioViewSet,
    AlunosAtivosTurmaRedisMultplexViewSet,
    AlunosAtivosTurmaSemRedisViewSet,
    AlunosTurmaConsideraInativosViewSet,
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
    ItinerariosEnsinoMedioViewSet,
    ListagemTurmasComponentesViewSet,
    ListarTurmasViewSet,
    SincronizacaoInstitucionalTurmaViewSet,
    SincronizacoesInstitucionaisAnosLetivosViewSet,
    TurmasHistoricasGeraisProfessorViewSet,
    TurmasProgramaViewSet,
    TurmasRegularesViewSet,
    ValidarComponentePapViewSet,
)

_TURMA_FUNCIONARIO_PREFIXO = (
    "turmas/<str:codigo_turma>/funcionarios/<str:login>/"
)

turma_urlpatterns = [
    path(
        "anos-letivos/<int:ano_letivo>/professor/"
        + "<str:professor_rf>/turmas-historicas-geral/",
        TurmasHistoricasGeraisProfessorViewSet.as_view(),
        name="turmas-historicas-gerais-professor",
    ),
    path(
        "itinerario/ensino-medio/",
        ItinerariosEnsinoMedioViewSet.as_view(),
        name="itinerarios-ensino-medio",
    ),
    path(
        "ue/<str:codigo_ue>/" + "sincronizacoes-institucionais/anos-letivos/",
        SincronizacoesInstitucionaisAnosLetivosViewSet.as_view(),
        name="sincronizacoes-institucionais-anos-letivos",
    ),
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
        "ues/<str:codigo_ue>/modalidades/<int:modalidade>/anos/"
        "<int:ano_letivo>/componentes/",
        ListagemTurmasComponentesViewSet.as_view(),
        name="listagem-turmas-componentes",
    ),
    path(
        "<str:codigo_turma>/sem-redis/",
        AlunosAtivosTurmaSemRedisViewSet.as_view(),
        name="alunos-ativos-turma-sem-redis",
    ),
    path(
        "<str:codigo_turma>/redis-Multplex/",
        AlunosAtivosTurmaRedisMultplexViewSet.as_view(),
        name="alunos-ativos-turma-redis-multplex",
    ),
    path(
        "<str:codigo_turma>/considera-inativos/<str:considera_inativos>/",
        AlunosTurmaConsideraInativosViewSet.as_view(),
        name="alunos-turma-considera_inativos",
    ),
    path(
        "<str:codigo_turma>/dados/",
        DadosTurmaViewSet.as_view(),
    ),
]

ue_urlpatterns = [
    path(
        "ues/<str:codigo_ue>/turmas/<str:codigo_turma>/"
        + "sincronizacoes-institucionais/",
        SincronizacaoInstitucionalTurmaViewSet.as_view(),
        name="sincronizacao-institucional-turma",
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
        _TURMA_FUNCIONARIO_PREFIXO
        + "perfis/<str:id_perfil>/agrupaComponenteCurricular/"
        + "<str:agrupa_componente_curricular>/",
        ComponentesTurmaFuncionarioViewSet.as_view(),
    ),
    path(
        _TURMA_FUNCIONARIO_PREFIXO + "perfis/<str:id_perfil>/planejamento/",
        ComponentesPlanejamentoViewSet.as_view(),
    ),
    path(
        "turmas/<str:codigo_turma>/sem-atribuicao/" + "<int:data_base_tick>/",
        ComponentesSemAtribuicaoViewSet.as_view(),
    ),
    path(
        _TURMA_FUNCIONARIO_PREFIXO + "perfis/<str:id_perfil>/validar/pap/",
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
        "territorio-saber/agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosLoteViewSet.as_view(),
    ),
    path(
        "territorio-saber/agrupamentos/",
        AgrupamentosTerritorioViewSet.as_view(),
    ),
    path(
        "<int:codigo_componente>/territorio-saber/"
        + "agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosViewSet.as_view(),
    ),
    path(
        "",
        ComponentesCurricularesViewSet.as_view(),
    ),
]
