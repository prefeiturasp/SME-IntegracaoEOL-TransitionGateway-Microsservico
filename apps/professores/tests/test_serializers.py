"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import (
    FuncionarioCargoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoExternaSerializer,
    ProfessorAutoCompleteSerializer,
    ProfessorTurmaAtribuidaSimplificadaSerializer,
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


class ProfessorTurmaAtribuidaSimplificadaSerializerTest(SimpleTestCase):
    """Valida serialização simplificada de turma atribuída ao professor."""

    def test_serializa_campos(self) -> None:
        payload = {
            "codigoTurma": 3030050,
            "nomeTurma": "1A",
            "componenteCurricular": "Matemática",
            "dataInicioAtribuicao": "2026-02-03",
            "dataFimAtribuicao": None,
            "ano": "1",
            "etapaEnsino": 1,
        }

        data = ProfessorTurmaAtribuidaSimplificadaSerializer(payload).data

        self.assertEqual(data, payload)


class TurmaAtribuidaProfessorSerializerTest(SimpleTestCase):
    """Valida serialização de turma atribuída ao professor."""

    def test_serializa_campos(self) -> None:
        mapeamento = [
            # (campo_entrada,      campo_saida,       valor)
            ("cod_escola",         "codEscola",       "019465"),
            ("cod_turma",          "codTurma",        3030050),
            ("tipo_turma",         "tipoTurma",       1),
            ("ano",                "ano",             "1"),
            ("ano_letivo",         "anoLetivo",       2026),
            ("cod_modalidade",     "codModalidade",   5),
            ("cod_dre",            "codDre",          "108100"),
            ("dre",                "dre",             "DRE TESTE"),
            ("dre_abrev",          "dreAbrev",        "DRE-T"),
            ("modalidade",         "modalidade",      "Fundamental"),
            ("nome_turma",         "nomeTurma",       "1A"),
            ("semestre",           "semestre",        0),
            ("tipo_ue",            "tipoUE",          "EMEF"),
            ("cod_tipo_ue",        "codTipoUE",       1),
            ("cod_ue",             "codUe",           "019465"),
            ("ue",                 "ue",              "EMEF TESTE"),
            ("ue_abrev",           "ueAbrev",         "EMEF T."),
            ("tipo_escola",        "tipoEscola",      "EMEF"),
            ("cod_tipo_escola",    "codTipoEscola",   1),
            ("duracao_turno",      "duracaoTurno",    5),
            ("tipo_turno",         "tipoTurno",       4),
            ("ensino_especial",    "ensinoEspecial",  False),
            ("serie_ensino",       "serieEnsino",     "1 ANO"),
            ("data_inicio_turma",  "dataInicioTurma", "2024-02-01T00:00:00"),
            ("data_fim_turma",     "dataFimTurma",    None),
            ("extinta",            "extinta",         False),
        ]
        payload = {entrada: valor for entrada, _, valor in mapeamento}
        esperado = {saida: valor for _, saida, valor in mapeamento}

        self.assertEqual(TurmaAtribuidaProfessorSerializer(payload).data, esperado)
