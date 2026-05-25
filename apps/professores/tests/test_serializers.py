"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import TextoEstritoField


class TextoEstritoFieldTest(SimpleTestCase):
    """Valida campo de texto estrito."""

    def test_erro_quando_super_nao_retorna_texto(self) -> None:
        field = TextoEstritoField()

        with patch.object(
            serializers.CharField,
            "to_internal_value",
            return_value=123,
        ), self.assertRaises(serializers.ValidationError):
            field.to_internal_value("abc")
