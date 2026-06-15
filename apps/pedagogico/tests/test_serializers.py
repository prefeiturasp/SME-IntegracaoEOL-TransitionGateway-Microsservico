"""Valida serializers do dominio pedagogico."""

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.pedagogico.serializers import (
    CodigoTurmaField,
    CodigoTurmaListSerializer,
    TurmaDadosSerializer,
)


class CodigoTurmaListSerializerTest(SimpleTestCase):
    """Valida a lista de codigos de turma."""

    def test_valida_lista_de_strings_numericas(self) -> None:
        serializer = CodigoTurmaListSerializer(data=["3024590", "3014194"])

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, ["3024590", "3014194"])

    def test_valida_lista_vazia(self) -> None:
        serializer = CodigoTurmaListSerializer(data=[])

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, [])

    def test_rejeita_body_que_nao_e_lista(self) -> None:
        serializer = CodigoTurmaListSerializer(data={"codigo": "3024590"})

        self.assertFalse(serializer.is_valid())

    def test_rejeita_item_vazio(self) -> None:
        serializer = CodigoTurmaListSerializer(data=["3024590", ""])

        self.assertFalse(serializer.is_valid())

    def test_rejeita_item_nao_numerico(self) -> None:
        serializer = CodigoTurmaListSerializer(data=["3024590", "ABC"])

        self.assertFalse(serializer.is_valid())

    def test_rejeita_item_nulo(self) -> None:
        serializer = CodigoTurmaListSerializer(data=["3024590", None])

        self.assertFalse(serializer.is_valid())


class CodigoTurmaFieldTest(SimpleTestCase):
    """Valida o campo de codigo de turma."""

    def test_rejeita_valor_que_nao_e_texto(self) -> None:
        field = CodigoTurmaField()

        with self.assertRaisesMessage(
            serializers.ValidationError, "Não é uma string válida."
        ):
            field.to_internal_value(123)


class TurmaDadosSerializerTest(SimpleTestCase):
    """Valida os dados de turma no contrato legado."""

    def test_serializa_campos_em_camel_case(self) -> None:
        serializer = TurmaDadosSerializer(
            {
                "ano": "1",
                "anoLetivo": 2026,
                "codigo": 3034092,
                "tipoTurma": 1,
                "modalidade": "Fundamental",
                "codigoModalidade": 5,
                "nomeTurma": "1A",
                "semestre": 0,
                "duracaoTurno": 55,
                "tipoTurno": 6,
                "dataFim": None,
                "ehistorico": False,
                "ensinoEspecial": False,
                "etapaEJA": 0,
                "serieEnsino": "1o Ano",
                "dataInicioTurma": "2026-02-04T00:00:00",
                "extinta": False,
                "situacao": "O",
                "ueCodigo": "092622",
            }
        )

        self.assertEqual(serializer.data["anoLetivo"], 2026)
        self.assertEqual(serializer.data["nomeTurma"], "1A")
        self.assertEqual(serializer.data["ehistorico"], False)
