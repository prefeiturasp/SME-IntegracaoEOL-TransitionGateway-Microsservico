"""Rotas do domínio pedagógico."""

from django.urls import path

from apps.pedagogico.views import (
    ComponentesCurricularesViewSet,
    ComponentesTurmaAnoViewSet,
    ComponentesTurmaProgramaViewSet,
    ComponentesTurmaViewSet,
    GradeComponentesCurricularesViewSet,
)

urlpatterns = [
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
