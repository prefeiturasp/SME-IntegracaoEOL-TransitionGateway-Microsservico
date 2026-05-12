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
        "DREs/<str:codigoEolDRE>/",
        DREDetalheView.as_view(),
        name="dre-detalhe",
    ),
    path(
        "DREs/<str:codigoEolDRE>/escola/",
        EscolasPorDREView.as_view(),
        name="escolas-por-dre",
    ),
    path(
        "DREs/<str:codigoEolDRE>/escolas/<str:tipoEscola>/",
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
        "escolas/<str:codigoEscolaEol>/",
        EscolaDetalheView.as_view(),
        name="escola-detalhe",
    ),
]
