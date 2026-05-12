from django.test import SimpleTestCase
from django.urls import resolve, reverse


class URLsInstitucionalTest(SimpleTestCase):
    def test_dre_list_resolve(self) -> None:
        match = resolve("/api/DREs/")
        self.assertEqual(match.view_name, "dre-list")

    def test_dre_detalhe_resolve(self) -> None:
        match = resolve("/api/DREs/108100/")
        self.assertEqual(match.view_name, "dre-detalhe")
        self.assertEqual(match.kwargs["codigoEolDRE"], "108100")

    def test_escolas_por_dre_resolve(self) -> None:
        match = resolve("/api/DREs/108100/escola/")
        self.assertEqual(match.view_name, "escolas-por-dre")
        self.assertEqual(match.kwargs["codigoEolDRE"], "108100")

    def test_equipamentos_resolve_antes_do_detalhe(self) -> None:
        # Garante que "equipamentos/" não é capturado pelo padrão <str:codigoEscolaEol>/
        match = resolve("/api/escolas/equipamentos/")
        self.assertEqual(match.view_name, "escola-equipamentos")

    def test_escola_detalhe_resolve(self) -> None:
        match = resolve("/api/escolas/019308/")
        self.assertEqual(match.view_name, "escola-detalhe")
        self.assertEqual(match.kwargs["codigoEscolaEol"], "019308")
