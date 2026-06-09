"""Valida helpers de data/hora dos contratos legados."""

from django.test import SimpleTestCase

from apps.core.datetime import formatar_datetime_legado


class FormatarDatetimeLegadoTest(SimpleTestCase):
    """Valida a formatacao de data/hora para o legado."""

    def test_converte_utc_para_horario_legado(self) -> None:
        result = formatar_datetime_legado("2026-02-04T03:00:00Z")

        self.assertEqual(result, "2026-02-04T00:00:00")

    def test_remove_zeros_excedentes_da_fracao(self) -> None:
        result = formatar_datetime_legado("2025-09-11T15:13:34.040000Z")

        self.assertEqual(result, "2025-09-11T12:13:34.04")

    def test_preserva_valor_que_nao_e_datetime_utc(self) -> None:
        result = formatar_datetime_legado("2026-02-04T00:00:00")

        self.assertEqual(result, "2026-02-04T00:00:00")
