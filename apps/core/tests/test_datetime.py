"""Valida helpers de data/hora dos contratos legados."""

from datetime import UTC, date, datetime

from django.test import SimpleTestCase

from apps.core.datetime import (
    datetime_de_tick,
    datetime_legado,
    formatar_datetime_legado,
    parse_date,
    validar_data_str,
    validar_data_tick,
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


class ValidarDataStrTest(SimpleTestCase):
    """Valida datas recebidas como texto."""

    def test_retorna_true_para_data_valida(self) -> None:
        self.assertTrue(validar_data_str("2026-07-28"))

    def test_retorna_false_para_data_inexistente(self) -> None:
        self.assertFalse(validar_data_str("2026-02-30"))

    def test_retorna_false_para_formato_invalido(self) -> None:
        self.assertFalse(validar_data_str("28/07/2026"))


class ValidarDataTickTest(SimpleTestCase):
    """Valida ticks no formato DateTime do .NET."""

    def test_aceita_tick_inteiro_e_string_numerica(self) -> None:
        self.assertTrue(validar_data_tick(639207072000000000))
        self.assertTrue(validar_data_tick("639207072000000000"))

    def test_rejeita_valores_fora_do_intervalo(self) -> None:
        self.assertFalse(validar_data_tick(-1))
        self.assertFalse(validar_data_tick(3155378976000000000))

    def test_rejeita_valor_nao_numerico(self) -> None:
        self.assertFalse(validar_data_tick("tick-invalido"))


class DatetimeDeTickTest(SimpleTestCase):
    """Valida a conversão de ticks do DateTime do .NET."""

    def test_converte_ticks_para_datetime(self) -> None:
        resultado = datetime_de_tick("639207072000000000")

        self.assertEqual(resultado, datetime(2026, 7, 27))

    def test_rejeita_ticks_invalidos(self) -> None:
        with self.assertRaisesRegex(ValueError, "Valor de ticks inválido"):
            datetime_de_tick("inválido")
