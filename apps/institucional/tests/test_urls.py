"""Valida o roteamento do domínio institucional."""

from django.test import SimpleTestCase
from django.urls import resolve


class URLsInstitucionalTest(SimpleTestCase):
    """Valida a resolução das rotas institucionais."""

    def test_dre_list_resolve(self) -> None:
        match = resolve("/api/DREs/")
        self.assertEqual(match.view_name, "dre-list")

    def test_dre_subprefeituras_resolve(self) -> None:
        match = resolve("/api/DREs/108100/subprefeituras/")
        self.assertEqual(match.view_name, "dre-subprefeituras")
        self.assertEqual(match.kwargs["dre_codigo"], "108100")

    def test_dre_ues_resolve(self) -> None:
        match = resolve("/api/DREs/108100/ues/")
        self.assertEqual(match.view_name, "dre-ues")
        self.assertEqual(match.kwargs["dre_codigo"], "108100")

    def test_dre_unidades_resolve(self) -> None:
        match = resolve("/api/DREs/108100/unidades/")
        self.assertEqual(match.view_name, "dre-unidades")
        self.assertEqual(match.kwargs["dre_codigo"], "108100")

    def test_dre_detalhe_resolve(self) -> None:
        match = resolve("/api/DREs/108100/")
        self.assertEqual(match.view_name, "dre-detalhe")
        self.assertEqual(match.kwargs["codigo_eol_dre"], "108100")

    def test_escolas_por_dre_resolve(self) -> None:
        match = resolve("/api/DREs/108100/escola/")
        self.assertEqual(match.view_name, "escolas-por-dre")
        self.assertEqual(match.kwargs["codigo_eol_dre"], "108100")

    def test_escolas_por_dre_tipo_resolve(self) -> None:
        match = resolve("/api/DREs/108100/escolas/EMEF/")
        self.assertEqual(match.view_name, "escolas-por-dre-tipo")
        self.assertEqual(match.kwargs["codigo_eol_dre"], "108100")
        self.assertEqual(match.kwargs["tipo_escola"], "EMEF")

    def test_escola_tipos_escolas_resolve(self) -> None:
        match = resolve("/api/escolas/tiposEscolas/")
        self.assertEqual(match.view_name, "escola-tipos-escolas")

    def test_equipamentos_resolve_antes_do_detalhe(self) -> None:
        # Garante que "equipamentos/" não é capturado pelo padrão
        # <str:codigoEscolaEol>/
        match = resolve("/api/escolas/equipamentos/")
        self.assertEqual(match.view_name, "escola-equipamentos")

    def test_escola_dados_resolve(self) -> None:
        match = resolve("/api/escolas/dados/019308/")
        self.assertEqual(match.view_name, "escola-dados")
        self.assertEqual(match.kwargs["codigo_escola_eol"], "019308")

    def test_escola_detalhe_resolve(self) -> None:
        match = resolve("/api/escolas/019308/")
        self.assertEqual(match.view_name, "escola-detalhe")
        self.assertEqual(match.kwargs["codigo_escola_eol"], "019308")

    def test_todas_unidades_resolve(self) -> None:
        match = resolve("/api/escolas/todas-unidades/")
        self.assertEqual(match.view_name, "escola-todas-unidades")

    def test_tipos_unidade_educacao_resolve(self) -> None:
        match = resolve("/api/escolas/tipos_unidade_educacao/")
        self.assertEqual(match.view_name, "escola-tipos-unidade-educacao")

    def test_unidade_eol_resolve(self) -> None:
        match = resolve("/api/escolas/unidade-eol/019308/")
        self.assertEqual(match.view_name, "escola-unidade-eol")
        self.assertEqual(match.kwargs["codigo_eol"], "019308")

    def test_sincronizacoes_institucionais_resolve(self) -> None:
        match = resolve(
            "/api/escolas/019308/sincronizacoes-institucionais/"
        )
        self.assertEqual(
            match.view_name, "escola-sincronizacoes-institucionais"
        )
        self.assertEqual(match.kwargs["ue_codigo"], "019308")

    def test_unidades_parceiras_resolve(self) -> None:
        match = resolve("/api/escolas/unidades-parceiras/")
        self.assertEqual(match.view_name, "escola-unidades-parceiras")
