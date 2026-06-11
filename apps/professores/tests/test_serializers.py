"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import (
    FuncionarioCargoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoExternaSerializer,
    TextoEstritoField,
)


class TextoEstritoFieldTest(SimpleTestCase):
    """Valida campo de texto estrito."""

    def test_erro_quando_super_nao_retorna_texto(self) -> None:
        field = TextoEstritoField()

        with (
            patch.object(
                serializers.CharField,
                "to_internal_value",
                return_value=123,
            ),
            self.assertRaises(serializers.ValidationError),
        ):
            field.to_internal_value("abc")


class FuncionarioCargoSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário com cargo."""

    def test_serializa_campos_legados(self) -> None:
        payload = {
            "codigo_rf": "7730900",
            "nome": None,
            "cargo_id": 3239,
        }

        data = FuncionarioCargoSerializer(payload).data

        self.assertEqual(
            data,
            {
                "funcionarioRF": "7730900",
                "funcionarioNome": None,
                "cargoId": 3239,
            },
        )


class FuncionarioFuncaoAtividadeSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário com função atividade."""

    def test_serializa_campos_legados(self) -> None:
        payload = {
            "codigo_rf": "7795246",
            "nome": None,
            "codigo_funcao_atividade": 30,
        }

        data = FuncionarioFuncaoAtividadeSerializer(payload).data

        self.assertEqual(
            data,
            {
                "funcionarioRF": "7795246",
                "funcionarioNome": None,
                "funcaoAtividadeId": 30,
            },
        )


class FuncionarioFuncaoExternaSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário com função externa."""

    def test_serializa_campos_legados(self) -> None:
        payload = {
            "cpf": "11610699840",
            "funcao_externo": 5,
        }

        data = FuncionarioFuncaoExternaSerializer(payload).data

        self.assertEqual(
            data,
            {
                "funcionarioCpf": "11610699840",
                "funcaoExternaId": 5,
            },
        )
