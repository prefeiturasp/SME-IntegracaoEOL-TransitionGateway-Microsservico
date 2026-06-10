"""Valida helpers de data/hora dos contratos legados."""

from datetime import UTC, date, datetime

from django.test import SimpleTestCase

from apps.core.datetime import (
    datetime_legado,
    formatar_datetime_legado,
    parse_date,
)


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


class ParseDateTest(SimpleTestCase):
    """Valida a normalizacao de valores para data."""

    def test_converte_datetime_iso_para_data(self) -> None:
        result = parse_date("2026-02-04T03:00:00Z")

        self.assertEqual(result, date(2026, 2, 4))

    def test_retorna_none_para_data_invalida(self) -> None:
        result = parse_date("data-invalida")

        self.assertIsNone(result)


class DatetimeLegadoTest(SimpleTestCase):
    """Valida a formatacao geral de data/hora legada."""

    def test_formata_date_com_hora_zerada(self) -> None:
        result = datetime_legado(date(2026, 2, 4))

        self.assertEqual(result, "2026-02-04T00:00:00")

    def test_converte_datetime_com_timezone(self) -> None:
        result = datetime_legado(datetime(2026, 2, 4, 3, 0, tzinfo=UTC))

        self.assertEqual(result, "2026-02-04T00:00:00")
