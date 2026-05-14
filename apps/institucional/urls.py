# Rotas do domínio institucional — prefixo "api/" em config/urls.py.

from django.urls import path

from apps.institucional.views import (
    DREDetalheView,
    DREListView,
    EscolaDetalheView,
    EscolasPorDREeTipoView,
    EscolasPorDREView,
    EquipamentosView,
)

urlpatterns = [
    # DREs — /api/DREs/
    path(
        "DREs/",
        DREListView.as_view(),
        name="dre-list",
    ),
    path(
        "DREs/<str:codigo_eol_dre>/",
        DREDetalheView.as_view(),
        name="dre-detalhe",
    ),
    path(
        "DREs/<str:codigo_eol_dre>/escola/",
        EscolasPorDREView.as_view(),
        name="escolas-por-dre",
    ),
    path(
        "DREs/<str:codigo_eol_dre>/escolas/<str:tipo_escola>/",
        EscolasPorDREeTipoView.as_view(),
        name="escolas-por-dre-tipo",
    ),
    # Escolas — equipamentos declarado antes do detalhe para evitar colisão
    path(
        "escolas/equipamentos/",
        EquipamentosView.as_view(),
        name="escola-equipamentos",
    ),
    path(
        "escolas/<str:codigo_escola_eol>/",
        EscolaDetalheView.as_view(),
        name="escola-detalhe",
    ),
]
