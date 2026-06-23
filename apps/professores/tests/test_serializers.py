"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import (
    FuncionarioCargoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoExternaSerializer,
    ProfessorAutoCompleteSerializer,
    TextoEstritoField,
    TurmaAtribuidaProfessorSerializer,
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


class FuncionarioSerializerTest(SimpleTestCase):
    """Valida serialização dos contratos de funcionário."""

    def test_serializa_campos(self) -> None:
        casos = [
            (
                FuncionarioCargoSerializer,
                {"codigo_rf": "7730900", "nome": None, "cargo_id": 3239},
                {"funcionarioRF": "7730900", "funcionarioNome": None, "cargoId": 3239},
            ),
            (
                FuncionarioFuncaoAtividadeSerializer,
                {
                    "codigo_rf": "7795246",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "funcionarioRF": "7795246",
                    "funcionarioNome": None,
                    "funcaoAtividadeId": 30,
                },
            ),
            (
                FuncionarioFuncaoExternaSerializer,
                {"cpf": "11610699840", "funcao_externo": 5},
                {"funcionarioCpf": "11610699840", "funcaoExternaId": 5},
            ),
        ]
        for serializer_cls, payload, esperado in casos:
            with self.subTest(serializer=serializer_cls.__name__):
                self.assertEqual(serializer_cls(payload).data, esperado)


class ProfessorAutoCompleteSerializerTest(SimpleTestCase):
    """Valida serialização de professor para autocomplete."""

    def test_serializa_nome_servidor_como_nome(self) -> None:
        payload = {"codigo_rf": "000001", "nome_servidor": "ANA SILVA"}

        data = ProfessorAutoCompleteSerializer(payload).data

        self.assertEqual(
            data,
            {"codigoRF": "000001", "nome": "ANA SILVA"},
        )


class TurmaAtribuidaProfessorSerializerTest(SimpleTestCase):
    """Valida serialização de turma atribuída ao professor."""

    def test_serializa_campos(self) -> None:
        payload = {
            "cod_escola": "019465",
            "cod_turma": 3030050,
            "tipo_turma": 1,
            "ano": "1",
            "ano_letivo": 2026,
            "cod_modalidade": 5,
            "cod_dre": "108100",
            "dre": "DRE TESTE",
            "dre_abrev": "DRE-T",
            "modalidade": "Fundamental",
            "nome_turma": "1A",
            "semestre": 0,
            "tipo_ue": "EMEF",
            "cod_tipo_ue": 1,
            "cod_ue": "019465",
            "ue": "EMEF TESTE",
            "ue_abrev": "EMEF T.",
            "tipo_escola": "EMEF",
            "cod_tipo_escola": 1,
            "duracao_turno": 5,
            "tipo_turno": 4,
            "ensino_especial": False,
            "serie_ensino": "1 ANO",
            "data_inicio_turma": "2024-02-01T00:00:00",
            "data_fim_turma": None,
            "extinta": False,
        }

        data = TurmaAtribuidaProfessorSerializer(payload).data

        self.assertEqual(
            data,
            {
                "codEscola": "019465",
                "codTurma": 3030050,
                "tipoTurma": 1,
                "ano": "1",
                "anoLetivo": 2026,
                "codModalidade": 5,
                "codDre": "108100",
                "dre": "DRE TESTE",
                "dreAbrev": "DRE-T",
                "modalidade": "Fundamental",
                "nomeTurma": "1A",
                "semestre": 0,
                "tipoUE": "EMEF",
                "codTipoUE": 1,
                "codUe": "019465",
                "ue": "EMEF TESTE",
                "ueAbrev": "EMEF T.",
                "tipoEscola": "EMEF",
                "codTipoEscola": 1,
                "duracaoTurno": 5,
                "tipoTurno": 4,
                "ensinoEspecial": False,
                "serieEnsino": "1 ANO",
                "dataInicioTurma": "2024-02-01T00:00:00",
                "dataFimTurma": None,
                "extinta": False,
            },
        )
