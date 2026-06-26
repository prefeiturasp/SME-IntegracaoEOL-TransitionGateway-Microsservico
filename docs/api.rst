Referência de código
====================

Esta página publica as docstrings dos principais módulos do projeto. Detalhes
de endpoints, status HTTP e contratos externos devem permanecer no OpenAPI ou
em páginas técnicas específicas.

Core
----

.. automodule:: apps.core.http_client

.. autoclass:: apps.core.http_client.ServiceClient
   :members: get, post, json_or_none, is_healthy

.. autofunction:: apps.core.responses.detail_response

.. automodule:: apps.core.logging_context
   :members:

.. automodule:: apps.core.middleware

.. autoclass:: apps.core.middleware.RequestIDMiddleware

.. autoclass:: apps.core.middleware.LoggingContextMiddleware

Institucional
-------------

.. automodule:: apps.institucional.serializers
   :members:

.. automodule:: apps.institucional.services
   :members:

.. automodule:: apps.institucional.views

.. autoclass:: apps.institucional.views.DREListView

.. autoclass:: apps.institucional.views.DREDetalheView

.. autoclass:: apps.institucional.views.SubprefeiturasPorDREView

.. autoclass:: apps.institucional.views.UesPorDREView

.. autoclass:: apps.institucional.views.UnidadesPorDREView

.. autoclass:: apps.institucional.views.EscolasPorDREView

.. autoclass:: apps.institucional.views.EscolasPorDREeTipoView

.. autoclass:: apps.institucional.views.DadosEscolaView

.. autoclass:: apps.institucional.views.TiposEscolasView

.. autoclass:: apps.institucional.views.EscolaDetalheView

.. autoclass:: apps.institucional.views.UnidadeEolView

.. autoclass:: apps.institucional.views.SincronizacoesInstitucionaisView

.. autoclass:: apps.institucional.views.UnidadesParceirasView

.. autoclass:: apps.institucional.views.EquipamentosView

.. autoclass:: apps.institucional.views.TodasUnidadesView

.. autoclass:: apps.institucional.views.TiposUnidadeEducacaoView

Pedagógico
----------

.. automodule:: apps.pedagogico.serializers
   :members:

.. automodule:: apps.pedagogico.services
   :members:

.. automodule:: apps.pedagogico.views

.. autoclass:: apps.pedagogico.views.TurmasRegularesViewSet

.. autoclass:: apps.pedagogico.views.TurmasProgramaViewSet

.. autoclass:: apps.pedagogico.views.ListarTurmasViewSet

.. autoclass:: apps.pedagogico.views.DadosTurmaViewSet

.. autoclass:: apps.pedagogico.views.TurmasHistoricasGeraisProfessorViewSet

.. autoclass:: apps.pedagogico.views.SincronizacaoInstitucionalTurmaViewSet

.. autoclass:: apps.pedagogico.views.SincronizacoesInstitucionaisAnosLetivosViewSet

.. autoclass:: apps.pedagogico.views.ItinerariosEnsinoMedioViewSet

.. autoclass:: apps.pedagogico.views.ComponentesCurricularesViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaProgramaViewSet

.. autoclass:: apps.pedagogico.views.ComponentesRegenciaViewSet

.. autoclass:: apps.pedagogico.views.ValidarComponentePapViewSet

.. autoclass:: apps.pedagogico.views.ComponentesFuncionarioViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaFuncionarioViewSet

.. autoclass:: apps.pedagogico.views.ComponentesPlanejamentoViewSet

.. autoclass:: apps.pedagogico.views.ComponentesPorListaTurmasViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmasRegularesViewSet

.. autoclass:: apps.pedagogico.views.DadosAulaTurmaViewSet

.. autoclass:: apps.pedagogico.views.ComponentesSemAtribuicaoViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaAnoViewSet

.. autoclass:: apps.pedagogico.views.GradeComponentesCurricularesViewSet

.. autoclass:: apps.pedagogico.views.AgrupamentosCorrelacionadosViewSet

.. autoclass:: apps.pedagogico.views.AgrupamentosCorrelacionadosLoteViewSet

.. autoclass:: apps.pedagogico.views.AgrupamentosTerritorioViewSet

Professores
-----------

.. automodule:: apps.professores.serializers
   :members:

.. automodule:: apps.professores.services
   :members:

.. automodule:: apps.professores.views

.. autoclass:: apps.professores.views.ProfessorView

.. autoclass:: apps.professores.views.ValidadeProfessorView

.. autoclass:: apps.professores.views.ProfessorBuscarPorRfView

.. autoclass:: apps.professores.views.ProfessorBuscarPorRfDreUeView

.. autoclass:: apps.professores.views.ProfessoresBuscarPorListaRfAnoView

.. autoclass:: apps.professores.views.ProfessorAutoCompleteView

.. autoclass:: apps.professores.views.ProfessorEhEmeiView

.. autoclass:: apps.professores.views.ProfessorTurmasView

.. autoclass:: apps.professores.views.ProfessorDisciplinaTurmasView

.. autoclass:: apps.professores.views.FuncionarioAtivoView

.. autoclass:: apps.professores.views.NomeServidorView

.. autoclass:: apps.professores.views.NomeUsuarioEolView

.. autoclass:: apps.professores.views.FuncionariosBuscarPorListaRfView

.. autoclass:: apps.professores.views.EscolaFuncionariosView

.. autoclass:: apps.professores.views.EscolaFuncionariosCargosView

.. autoclass:: apps.professores.views.EscolaFuncionariosCargoView

.. autoclass:: apps.professores.views.EscolaFuncionariosFuncoesAtividadesView

.. autoclass:: apps.professores.views.EscolaFuncionariosFuncaoAtividadeView

.. autoclass:: apps.professores.views.EscolaFuncionariosFuncoesExternasView

.. autoclass:: apps.professores.views.EscolaFuncionariosFuncaoExternaView

Alunos
------

.. automodule:: apps.alunos.serializers
   :members:

.. automodule:: apps.alunos.services
   :members:

.. automodule:: apps.alunos.views

.. autoclass:: apps.alunos.views.AlunoAutocompleteAtivosView

.. autoclass:: apps.alunos.views.AlunoInformacoesView

.. autoclass:: apps.alunos.views.ResponsavelResumidoView

.. autoclass:: apps.alunos.views.InformacoesAlunosTurmaView

.. autoclass:: apps.alunos.views.AlunosAtivosDataAulaTicksView

.. autoclass:: apps.alunos.views.AlunoNecessidadesEspeciaisView

.. autoclass:: apps.alunos.views.AlunoTurmasView

.. autoclass:: apps.alunos.views.AlunosListView

Matrículas
----------

.. automodule:: apps.matriculas.serializers
   :members:

.. automodule:: apps.matriculas.services
   :members:

.. automodule:: apps.matriculas.views

.. autoclass:: apps.matriculas.views.MatriculasAnoAtualView

Programas educacionais
----------------------

.. automodule:: apps.programasedu.serializers
   :members:

.. automodule:: apps.programasedu.services
   :members:

.. automodule:: apps.programasedu.views

.. autoclass:: apps.programasedu.views.ObterTurmasPapView

.. autoclass:: apps.programasedu.views.VerificarSeAlunosSaoTurmaProgramaPapView

.. autoclass:: apps.programasedu.views.ObterAlunosPapAnoCorrenteView

.. autoclass:: apps.programasedu.views.ObterAlunosPapPorAnoLetivoView

.. autoclass:: apps.programasedu.views.ObterComponentesCurricularesTurmasProgramaAlunoView

.. autoclass:: apps.programasedu.views.ObterDadosSrmPaeeAlunoView

.. autoclass:: apps.programasedu.views.ObterTurmaSrmERegularDoAlunoView
