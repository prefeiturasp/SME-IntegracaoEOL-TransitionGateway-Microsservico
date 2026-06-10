"""Rotas do domínio institucional."""

from django.urls import path

from apps.institucional.views import (
    DadosEscolaView,
    DREDetalheView,
    DREListView,
    EquipamentosView,
    EscolaDetalheView,
    EscolasPorDREeTipoView,
    EscolasPorDREView,
    SubprefeiturasPorDREView,
    TiposEscolasView,
    UesPorDREView,
    UnidadesPorDREView,
)

urlpatterns = [
    # DREs — /api/DREs/
    path(
        "DREs/",
        DREListView.as_view(),
        name="dre-list",
    ),
    # Sub-rotas específicas antes da rota genérica de detalhe
    path(
        "DREs/<str:dre_codigo>/subprefeituras/",
        SubprefeiturasPorDREView.as_view(),
        name="dre-subprefeituras",
    ),
    path(
        "DREs/<str:dre_codigo>/ues/",
        UesPorDREView.as_view(),
        name="dre-ues",
    ),
    path(
        "DREs/<str:dre_codigo>/unidades/",
        UnidadesPorDREView.as_view(),
        name="dre-unidades",
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
    path(
        "DREs/<str:codigo_eol_dre>/",
        DREDetalheView.as_view(),
        name="dre-detalhe",
    ),
    # Escolas — rotas literais antes das com parâmetro para evitar colisão
    path(
        "escolas/tiposEscolas/",
        TiposEscolasView.as_view(),
        name="escola-tipos-escolas",
    ),
    path(
        "escolas/equipamentos/",
        EquipamentosView.as_view(),
        name="escola-equipamentos",
    ),
    path(
        "escolas/dados/<str:codigo_escola_eol>/",
        DadosEscolaView.as_view(),
        name="escola-dados",
    ),
    path(
        "escolas/<str:codigo_escola_eol>/",
        EscolaDetalheView.as_view(),
        name="escola-detalhe",
    ),
]
