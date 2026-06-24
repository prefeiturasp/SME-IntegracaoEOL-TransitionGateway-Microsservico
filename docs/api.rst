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

.. autoclass:: apps.institucional.views.EscolasPorDREView

.. autoclass:: apps.institucional.views.EscolasPorDREeTipoView

.. autoclass:: apps.institucional.views.EscolaDetalheView

.. autoclass:: apps.institucional.views.EquipamentosView

Pedagógico
----------

.. automodule:: apps.pedagogico.serializers
   :members:

.. automodule:: apps.pedagogico.services
   :members:

.. automodule:: apps.pedagogico.views

.. autoclass:: apps.pedagogico.views.ComponentesCurricularesViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaViewSet

.. autoclass:: apps.pedagogico.views.ComponentesTurmaProgramaViewSet

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
