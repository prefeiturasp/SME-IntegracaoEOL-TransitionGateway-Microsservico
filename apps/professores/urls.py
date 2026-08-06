"""Rotas do domínio de professores."""

from django.urls import path, register_converter

from apps.professores.views import (
    AdministradorSgpEscolaView,
    BuscaTurmasAtribuidasProfessoresEscolaView,
    EscolaFuncionariosCargosView,
    EscolaFuncionariosCargoView,
    EscolaFuncionariosFuncaoAtividadeView,
    EscolaFuncionariosFuncaoExternaView,
    EscolaFuncionariosFuncoesAtividadesView,
    EscolaFuncionariosFuncoesExternasView,
    EscolaFuncionariosView,
    FuncionarioAtivoView,
    FuncionarioPerfilTurmaDisciplinasPlanejamentoView,
    FuncionarioPerfilTurmaDisciplinasView,
    FuncionarioPerfilTurmasView,
    FuncionariosBuscarPorListaRfView,
    FuncionariosBuscarTurmasElegiveisView,
    FuncionariosCargoView,
    FuncionariosPerfisDreView,
    FuncionariosPerfisView,
    FuncionariosSupervisoresView,
    FuncionariosTurmasView,
    FuncionariosUeView,
    FuncionariosView,
    FuncionarioTurmaDisciplinasView,
    NomeServidorView,
    NomeUsuarioEolView,
    ProfessorAtribuicaoTurmaDisciplinaView,
    ProfessorAutoCompleteView,
    ProfessorBuscarPorRfDreUeView,
    ProfessorBuscarPorRfView,
    ProfessorBuscarTurmasAtribuidasView,
    ProfessorBuscaTurmasAtribuidasEscolaView,
    ProfessorDisciplinaTurmasView,
    ProfessorEhEmeiView,
    ProfessoresBuscarPorListaRfAnoView,
    ProfessoresTitularesPorTurmaView,
    ProfessorStatusAtribuicaoView,
    ProfessorTurmasView,
    ProfessorVerificarAtribuicaoDataTickView,
    ProfessorVerificarAtribuicaoDataView,
    ProfessorVerificarAtribuicaoPeriodoView,
    ProfessorVerificarAtribuicaoTurmaDisciplinaDataView,
    ProfessorVerificarRecorrenciaDatasView,
    ProfessorView,
    ValidadeProfessorView,
)


class _BooleanConverter:
    """Converte os literais de rota ``true`` e ``false`` em booleanos."""

    regex = "(?i:true|false)"

    def to_python(self, value: str) -> bool:
        """Converta o valor textual recebido pela rota.

        Args:
            value: Literal booleano capturado na URL.

        Returns:
            Valor booleano convertido.
        """
        return value.lower() == "true"

    def to_url(self, value: bool) -> str:
        """Converta o booleano para construção reversa da URL.

        Args:
            value: Booleano usado na construção da URL.

        Returns:
            Literal booleano em letras minúsculas.
        """
        return str(value).lower()


register_converter(_BooleanConverter, "bool")

urlpatterns = [
    path(
        "funcionarios/turmas/<str:codigo_turma>/disciplinas/",
        FuncionarioTurmaDisciplinasView.as_view(),
    ),
    path(
        "funcionarios/<str:login>/perfis/<str:id_perfil>/turmas/"
        "<str:codigo_turma>/disciplinas/planejamento/",
        FuncionarioPerfilTurmaDisciplinasPlanejamentoView.as_view(),
    ),
    path(
        "funcionarios/<str:login>/perfis/<str:id_perfil>/turmas/"
        "<str:codigo_turma>/disciplinas/",
        FuncionarioPerfilTurmaDisciplinasView.as_view(),
    ),
    path(
        "funcionarios/<str:login>/perfis/<str:id_perfil>/turmas/",
        FuncionarioPerfilTurmasView.as_view(),
    ),
    path(
        "funcionarios/turmas/",
        FuncionariosTurmasView.as_view(),
    ),
    path(
        "funcionarios/BuscarTurmasElegiveis/",
        FuncionariosBuscarTurmasElegiveisView.as_view(),
    ),
    path(
        "funcionarios/",
        FuncionariosView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/BuscarPorRf/<int:ano_letivo>/",
        ProfessorBuscarPorRfView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/BuscarPorRfDreUe/<int:ano_letivo>/",
        ProfessorBuscarPorRfDreUeView.as_view(),
    ),
    path(
        "professores/<int:ano_letivo>/BuscarPorListaRF/",
        ProfessoresBuscarPorListaRfAnoView.as_view(),
    ),
    path(
        "professores/<int:ano_letivo>/AutoComplete/<str:dre_id>/",
        ProfessorAutoCompleteView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/ehEmei/",
        ProfessorEhEmeiView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/",
        ProfessorTurmasView.as_view(),
    ),
    path(
        "professores/<str:codigo_turma>/titulares/"
        "realizaAgrupamentoComponente/<bool:realiza_agrupamento>",
        ProfessoresTitularesPorTurmaView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/disciplina/<str:disciplina_id>/turmas/",
        ProfessorDisciplinaTurmasView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/validade/",
        ValidadeProfessorView.as_view(),
    ),
    path(
        "professores/<str:rf_professor>/",
        ProfessorView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/atribuicao/verificar/data/",
        ProfessorVerificarAtribuicaoDataView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/componentes/"
        "<str:componente_curricular_id>/atribuicao/periodo/inicio/"
        "<str:data_inicio_periodo>/fim/<str:data_fim_periodo>",
        ProfessorVerificarAtribuicaoPeriodoView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/atribuicao/status/",
        ProfessorStatusAtribuicaoView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/disciplinas/<str:disciplina_id>/atribuicao/verificar/datatick/",
        ProfessorVerificarAtribuicaoDataTickView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/disciplinas/"
        "<str:disciplina_id>/atribuicao/recorrencia/verificar/datas",
        ProfessorVerificarRecorrenciaDatasView.as_view(),
    ),
    path(
        "professores/<str:codigo_turma>/disciplinas/<str:disciplina_id>/atribuicao/data/",
        ProfessorAtribuicaoTurmaDisciplinaView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/<str:codigo_turma>/disciplinas/<str:disciplina_id>/atribuicao/verificar/data",
        ProfessorVerificarAtribuicaoTurmaDisciplinaDataView.as_view(),
    ),
    path(
        "acessos/funcionario-ativo/<str:registro_funcional>/",
        FuncionarioAtivoView.as_view(),
    ),
    path(
        "funcionarios/nome-servidor/<str:registro_funcional>/",
        NomeServidorView.as_view(),
    ),
    path(
        "funcionarios/nome-usuario-eol/<str:registro_funcional>/",
        NomeUsuarioEolView.as_view(),
    ),
    path(
        "funcionarios/BuscarPorListaRF/",
        FuncionariosBuscarPorListaRfView.as_view(),
    ),
    path(
        "funcionarios/ue/<str:codigo_ue>/",
        FuncionariosUeView.as_view(),
    ),
    path(
        "funcionarios/cargos/<str:codigo_cargo>/",
        FuncionariosCargoView.as_view(),
    ),
    path(
        "funcionarios/perfis/<str:id_perfil>/",
        FuncionariosPerfisView.as_view(),
    ),
    path(
        "funcionarios/perfis/<str:id_perfil>/dres/<str:codigo_dre>/",
        FuncionariosPerfisDreView.as_view(),
    ),
    path(
        "funcionarios/supervisores/<str:codigo_dre>/",
        FuncionariosSupervisoresView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/funcoes-atividades/"
        "<str:codigo_funcao_atividade>/",
        EscolaFuncionariosFuncaoAtividadeView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/funcoes-atividades/",
        EscolaFuncionariosFuncoesAtividadesView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/funcoes-externas/"
        "<str:codigo_funcao_externa>/",
        EscolaFuncionariosFuncaoExternaView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/funcoes-externas/",
        EscolaFuncionariosFuncoesExternasView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/cargos/",
        EscolaFuncionariosCargosView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/cargos/<str:codigo_cargo>/",
        EscolaFuncionariosCargoView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/funcionarios/",
        EscolaFuncionariosView.as_view(),
    ),
    path(
        "escolas/<str:codigo_ue>/administrador-sgp/",
        AdministradorSgpEscolaView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/escolas/<str:codigo_eol_escola>/turmas/anos_letivos/<int:ano_letivo>/",
        ProfessorBuscaTurmasAtribuidasEscolaView.as_view(),
    ),
    path(
        "professores/escolas/<str:codigo_eol_escola>/turmas/anos_letivos/<int:ano_letivo>/",
        BuscaTurmasAtribuidasProfessoresEscolaView.as_view(),
    ),
    path(
        "professores/<str:codigo_rf>/turmas/anos_letivos/<int:ano_letivo>/",
        ProfessorBuscarTurmasAtribuidasView.as_view(),
    ),
]
