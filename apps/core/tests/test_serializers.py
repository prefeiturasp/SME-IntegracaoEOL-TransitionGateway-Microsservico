"""Testes dos fields de serialização compartilhados."""

from django.test import SimpleTestCase

from apps.core.serializers import (
    DataHoraLegadoComZField,
    InteiroBooleanoField,
)


class InteiroBooleanoFieldTest(SimpleTestCase):
    """Valida a conversão de booleano para indicador numérico."""

    def test_converte_verdadeiro_para_um(self) -> None:
        field = InteiroBooleanoField()

        self.assertEqual(field.to_representation(True), 1)

    def test_converte_falso_para_zero(self) -> None:
        field = InteiroBooleanoField()

        self.assertEqual(field.to_representation(False), 0)


class DataHoraLegadoComZFieldTest(SimpleTestCase):
    """Valida a serialização de data/hora com sufixo publicado."""

    def test_acrescenta_sufixo_z(self) -> None:
        field = DataHoraLegadoComZField()

        self.assertEqual(
            field.to_representation("2025-12-08T11:42:14.660000-03:00"),
            "2025-12-08T11:42:14.66Z",
        )

    def test_preserva_none(self) -> None:
        field = DataHoraLegadoComZField()

        self.assertIsNone(field.to_representation(None))
