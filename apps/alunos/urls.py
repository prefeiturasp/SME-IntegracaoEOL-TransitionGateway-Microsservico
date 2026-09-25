"""Rotas do domínio de alunos."""

from django.urls import path

from apps.alunos.views import (
    AcompanhamentoEscolarTurmaView,
    AlunoAutocompleteAtivosView,
    AlunoAutocompleteUeView,
    AlunoInformacoesView,
    AlunoMatriculasTurmaView,
    AlunoNecessidadesEspeciaisView,
    AlunosAtivosDataAulaTicksView,
    AlunosAtivosDataAulaView,
    AlunosAtivosPeriodoTurmaView,
    AlunosAtivosTurmaView,
    AlunosCalculoFrequenciaTurmaView,
    AlunosDataMatriculaTicksView,
    AlunosDataMatriculaView,
    AlunosDaUeView,
    AlunosListView,
    AlunosPorAnoView,
    AlunosTurmaAnoLetivoView,
    AlunoTurmaConsideraInativosView,
    AlunoTurmasComHistoricoView,
    AlunoTurmasPorSituacaoView,
    AlunoTurmasView,
    CodigosTurmasRegularesAlunoView,
    CodigoTurmaAlunoComponenteCurricularView,
    DadosAcompanhamentoEscolarView,
    DadosResponsavelView,
    FiliacaoAlunoView,
    InformacoesAlunosTurmaView,
    MatriculasTurmasAlunoView,
    ObterNomesAlunosView,
    QuantidadeMatriculadosCCView,
    QuantidadeMatriculadosView,
    ResponsaveisView,
    ResponsavelAlunoView,
    ResponsavelResumidoView,
    TodosAlunosTurmaView,
    TotalAlunosAtivosPeriodoView,
    TotalAlunosTurmasPeriodoView,
)

turma_urlpatterns = [
    # Rotas de 1º segmento literal vêm antes das que abrem com
    # <str:codigo_turma>, senão o código da turma capturaria o literal.
    path(
        "todos-alunos/anoTurma/<str:ano_turma>/"  # NOSONAR
        "modalidade/<str:modalidade_turma>/"  # NOSONAR
        "anoLetivo/<str:ano_letivo>/dre/<str:codigo_dre>/"  # NOSONAR
        "inicio/<str:data_inicio_ticks>/fim/<str:data_fim_ticks>",
        TotalAlunosTurmasPeriodoView.as_view(),
        name="total-alunos-turmas-periodo",
    ),
    path(
        "alunos/<str:codigo_aluno>",
        MatriculasTurmasAlunoView.as_view(),
        name="matriculas-turmas-aluno",
    ),
    path(
        "<str:codigo_turma>/alunos-ativos/"  # NOSONAR
        "data-aula-ticks/<str:data_ticks>",
        AlunosAtivosDataAulaTicksView.as_view(),
        name="alunos-ativos-data-aula-ticks",
    ),
    path(
        "<str:codigo_turma>/alunos-ativos/data-aula/<str:data_aula>",
        AlunosAtivosDataAulaView.as_view(),
        name="alunos-ativos-data-aula",
    ),
    path(
        "<str:codigo_turma>/data-matricula-ticks/"  # NOSONAR
        "<str:data_matricula_ticks>",
        AlunosDataMatriculaTicksView.as_view(),
        name="alunos-data-matricula-ticks",
    ),
    path(
        "<str:codigo_turma>/data-matricula/<str:data_matricula>",
        AlunosDataMatriculaView.as_view(),
        name="alunos-data-matricula",
    ),
    path(
        "<str:codigo_turma>/aluno/<str:codigo_aluno>/"  # NOSONAR
        "considera-inativos/<str:considera_inativos>",
        AlunoTurmaConsideraInativosView.as_view(),
        name="aluno-turma-considera-inativos",
    ),
    path(
        "<str:codigo_turma>/aluno/<str:codigo_aluno>/matriculas",
        AlunoMatriculasTurmaView.as_view(),
        name="aluno-matriculas-turma",
    ),
    path(
        "<str:codigo_turma>/calculo-frequencia",
        AlunosCalculoFrequenciaTurmaView.as_view(),
        name="alunos-calculo-frequencia-turma",
    ),
    path(
        "<str:codigo_turma>/acompanhamento-escolar/todos-alunos",
        AcompanhamentoEscolarTurmaView.as_view(),
        name="acompanhamento-escolar-turma",
    ),
    path(
        "<str:codigo_turma>/todos-alunos",
        TodosAlunosTurmaView.as_view(),
        name="todos-alunos-turma",
    ),
    path(
        "<str:codigo_turma>/alunos/anosLetivos/<str:ano_letivo>",
        AlunosTurmaAnoLetivoView.as_view(),
        name="alunos-turma-ano-letivo",
    ),
    path(
        "anos-letivos/<str:ano_letivo>/alunos/<str:codigo_aluno>/"  # NOSONAR
        "regulares",
        CodigosTurmasRegularesAlunoView.as_view(),
        name="codigos-turmas-regulares-aluno",
    ),
    path(
        "anos-letivos/<str:ano_letivo>/alunos/<str:codigo_aluno>/"  # NOSONAR
        "componentes-curriculares/<str:componente_curricular_codigo>",
        CodigoTurmaAlunoComponenteCurricularView.as_view(),
        name="codigo-turma-aluno-componente-curricular",
    ),
]

urlpatterns = [
    path("alunos", AlunosListView.as_view(), name="alunos-list"),
    path(
        "ues/<str:ue_codigo>/autocomplete/ativos",
        AlunoAutocompleteAtivosView.as_view(),
        name="aluno-autocomplete-ativos",
    ),
    path(
        "ues/<str:codigo_ue>/anosLetivos/<str:ano_letivo>",
        AlunosDaUeView.as_view(),
        name="alunos-da-ue",
    ),
    path(
        "ues/<str:codigo_ue>/anosLetivos/<str:ano_letivo>/autocomplete",
        AlunoAutocompleteUeView.as_view(),
        name="aluno-autocomplete-ue",
    ),
    path(
        "dados-acompanhamento-escolar",
        DadosAcompanhamentoEscolarView.as_view(),
        name="dados-acompanhamento-escolar",
    ),
    path(
        "ano-letivo/<str:ano_letivo>/matriculados",
        QuantidadeMatriculadosCCView.as_view(),
        name="quantidade-matriculados-cc",
    ),
    path(
        "ano-letivo/<str:ano_letivo>/matriculados/quantidade",
        QuantidadeMatriculadosView.as_view(),
        name="quantidade-matriculados",
    ),
    path(
        "anoLetivo/<str:ano_letivo>/alunos",
        AlunosPorAnoView.as_view(),
        name="alunos-por-ano",
    ),
    path(
        "responsaveis",
        ResponsaveisView.as_view(),
        name="alunos-responsaveis",
    ),
    path(
        "responsaveis/<str:cpf_responsavel>/resumido",
        ResponsavelResumidoView.as_view(),
        name="aluno-responsavel-resumido",
    ),
    path(
        "responsaveis/<str:cpf_responsavel>",
        DadosResponsavelView.as_view(),
        name="aluno-dados-responsavel",
    ),
    path(
        "obter-nomes-alunos",
        ObterNomesAlunosView.as_view(),
        name="alunos-obter-nomes",
    ),
    path(
        "<str:codigo_aluno>/responsaveis/filiacao",
        FiliacaoAlunoView.as_view(),
        name="aluno-filiacao",
    ),
    path(
        "<str:codigo_aluno>/responsaveis/<str:cpf_responsavel>",
        ResponsavelAlunoView.as_view(),
        name="aluno-atualizar-responsavel",
    ),
    path(
        "<str:codigo_turma>/turma/informacoes",
        InformacoesAlunosTurmaView.as_view(),
        name="informacoes-alunos-turma",
    ),
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
        "<str:codigo_aluno>/turmas/anosLetivos/<str:ano_letivo>/"  # NOSONAR
        "historico/<str:historico>/"  # NOSONAR
        "filtrar-situacao/<str:filtrar_situacao>/"  # NOSONAR
        "tipo-turma/<str:tipo_turma>",
        AlunoTurmasComHistoricoView.as_view(),
        name="aluno-turmas-com-historico",
    ),
    path(
        "<str:codigo_aluno>/turmas/anosLetivos/<str:ano_letivo>/"  # NOSONAR
        "matriculaTurma/<str:filtrar_situacao_matricula>/"  # NOSONAR
        "tipoTurma/<str:tipo_turma>",
        AlunoTurmasPorSituacaoView.as_view(),
        name="aluno-turmas-por-situacao",
    ),
    path(
        "turmas/<str:codigo_turma>/ativos/<str:data_referencia_fim>",
        AlunosAtivosPeriodoTurmaView.as_view(),
        name="alunos-ativos-periodo-turma",
    ),
    path(
        "turmas/<str:codigo_turma>/ativos",
        AlunosAtivosTurmaView.as_view(),
        name="alunos-ativos-turma",
    ),
    path(
        "ativos/anos/<str:ano_turma>/anos-letivos/<str:ano_letivo>/"  # NOSONAR
        "inicio/<str:data_inicio>/fim/<str:data_fim>",
        TotalAlunosAtivosPeriodoView.as_view(),
        name="total-alunos-ativos-periodo",
    ),
]
