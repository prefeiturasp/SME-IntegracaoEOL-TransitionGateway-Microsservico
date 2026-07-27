"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import (
    DisciplinaTurmaAgrupamentoSerializer,
    DisciplinaTurmaAtribuidaSerializer,
    FuncionarioCargoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoExternaSerializer,
    FuncionarioLegadoSerializer,
    FuncionarioSgpLegadoSerializer,
    ProfessorAutoCompleteSerializer,
    ProfessorTurmaAtribuidaSimplificadaSerializer,
    SupervisorLegadoSerializer,
    TextoEstritoField,
    TurmaAtribuidaProfessorSerializer,
    TurmaElegivelLegadoSerializer,
    TurmasAtribuidasLegadoSerializer,
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
                {
                    "funcionarioRF": "7730900",
                    "funcionarioNome": None,
                    "cargoId": 3239,
                },
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
            (
                SupervisorLegadoSerializer,
                {
                    "codigo_rf": "000001",
                    "nome_servidor": "NOME SERVIDOR",
                },
                {
                    "codigoRF": "000001",
                    "nomeServidor": "NOME SERVIDOR",
                },
            ),
        ]
        for serializer_cls, payload, esperado in casos:
            with self.subTest(serializer=serializer_cls.__name__):
                self.assertEqual(serializer_cls(payload).data, esperado)


class FuncionarioLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário no contrato legado."""

    def test_serializa_campos(self) -> None:
        payload = {
            "codigo_funcao_atividade": 30,
            "codigo_rf": "000001",
            "funcao_externo": 5,
            "nome": "ANA",
            "tipo_funcao_externo": 7,
        }

        self.assertEqual(
            FuncionarioLegadoSerializer(payload).data,
            {
                "cd_Cargo": 0,
                "codigoFuncaoAtividade": 30,
                "codigoRf": "000001",
                "funcaoExterno": 5,
                "login": "000001",
                "nomeServidor": "ANA",
                "tipoFuncaoExterno": 7,
            },
        )


class FuncionarioSgpLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário SGP no contrato legado."""

    def test_serializa_campos(self) -> None:
        payload = {
            "cd_cargo": "3360",
            "codigo_funcao_atividade": 30,
            "codigo_rf": "000001",
            "funcao_externo": 5,
            "login": None,
            "nome_servidor": "ANA",
            "tipo_funcao_externo": 7,
        }

        self.assertEqual(
            FuncionarioSgpLegadoSerializer(payload).data,
            {
                "cd_Cargo": 3360,
                "codigoFuncaoAtividade": 30,
                "codigoRf": "000001",
                "funcaoExterno": 5,
                "login": None,
                "nomeServidor": "ANA",
                "tipoFuncaoExterno": 7,
            },
        )


class DisciplinaTurmaSerializerTest(SimpleTestCase):
    """Valida serialização de disciplinas no contrato legado."""

    def test_disciplina_atribuida_preserva_tipo_escola(self) -> None:
        payload = {
            "codigo": 512,
            "codigo_componente_curricular_pai": None,
            "codigo_componente_territorio_saber": None,
            "descricao": "ARTE",
            "regencia": False,
            "tipo_escola": "EMEF",
            "territorio_saber": False,
        }

        self.assertEqual(
            DisciplinaTurmaAtribuidaSerializer(payload).data,
            {
                "codDisciplina": 512,
                "codDisciplinaPai": None,
                "codCompTerritorioSaber": None,
                "disciplina": "ARTE",
                "regencia": False,
                "tipoEscola": "EMEF",
                "territorioSaber": False,
                "professor": None,
            },
        )

    def test_disciplina_agrupamento_usa_zero_e_tipo_escola_nulo(self) -> None:
        payload = {
            "codigo": 138,
            "codigo_componente_curricular_pai": 512,
            "codigo_componente_territorio_saber": None,
            "codigos_territorios_agrupamento": [1, 2],
            "descricao": "LINGUA PORTUGUESA",
            "regencia": True,
            "territorio_saber": True,
        }

        self.assertEqual(
            DisciplinaTurmaAgrupamentoSerializer(payload).data[
                "codCompTerritorioSaber"
            ],
            0,
        )
        self.assertIsNone(
            DisciplinaTurmaAgrupamentoSerializer(payload).data["tipoEscola"]
        )


class TurmasAtribuidasLegadoSerializerTest(SimpleTestCase):
    """Valida agrupamento de turmas atribuídas."""

    def test_agrupa_por_dre_ue_e_remove_turma_repetida(self) -> None:
        payload = [
            {
                "codigo_dre": "108100",
                "dre": "DRE TESTE",
                "dre_abreviacao": "DRE-T",
                "codigo_escola": "000532",
                "ue": "EMEF TESTE",
                "codigo_tipo_escola": 1,
                "codigo_turma": 3030050,
                "ano": "1",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "codigo_modalidade": None,
                "nome_turma": "1A",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 4,
            },
            {
                "codigo_dre": "108100",
                "codigo_escola": "000532",
                "codigo_turma": 3030050,
            },
        ]

        data = TurmasAtribuidasLegadoSerializer(payload).data

        self.assertEqual(len(data["dres"]), 1)
        self.assertEqual(len(data["dres"][0]["ues"]), 1)
        self.assertEqual(len(data["dres"][0]["ues"][0]["turmas"]), 1)
        self.assertEqual(
            data["dres"][0]["ues"][0]["turmas"][0]["codigoModalidade"],
            0,
        )

    def test_aceita_campos_da_composicao_de_professor(self) -> None:
        payload = [
            {
                "cod_dre": "109200",
                "dre": "DIRETORIA REGIONAL DE EDUCACAO SAO MATEUS",
                "dre_abrev": "DRE - SM",
                "cod_escola": "013803",
                "ue": "JULIO DE GRAMMONT",
                "cod_tipo_escola": 1,
                "cod_turma": 3018605,
                "ano": "7",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "cod_modalidade": 5,
                "nome_turma": "7B",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 1,
            },
            {
                "cod_dre": "109200",
                "dre": "DIRETORIA REGIONAL DE EDUCACAO SAO MATEUS",
                "dre_abrev": "DRE - SM",
                "cod_escola": "013803",
                "ue": "JULIO DE GRAMMONT",
                "cod_tipo_escola": 1,
                "cod_turma": 3018602,
                "ano": "7",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "cod_modalidade": 5,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 1,
            },
        ]

        data = TurmasAtribuidasLegadoSerializer(payload).data
        dre = data["dres"][0]
        ue = dre["ues"][0]

        self.assertEqual(dre["codigo"], "109200")
        self.assertEqual(dre["abreviacao"], "DRE - SM")
        self.assertEqual(ue["codigo"], "013803")
        self.assertEqual(ue["codTipoEscola"], 1)
        self.assertEqual(
            [turma["codigo"] for turma in ue["turmas"]],
            [3018602, 3018605],
        )
        self.assertEqual(ue["turmas"][0]["modalidade"], "Fundamental")
        self.assertEqual(ue["turmas"][0]["codigoModalidade"], 5)
        self.assertEqual(ue["turmas"][0]["duracaoTurno"], 5)

    def test_retorna_payload_nao_lista_sem_transformar(self) -> None:
        payload = {"abrangencia": None}

        self.assertEqual(
            TurmasAtribuidasLegadoSerializer(payload).data, payload
        )


class TurmaElegivelLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de turma elegível."""

    def test_serializa_campos(self) -> None:
        payload = {"nome_turma": "1A", "cod_turma": 3030050}

        self.assertEqual(
            TurmaElegivelLegadoSerializer(payload).data,
            {"nomeTurma": "1A", "codTurma": 3030050},
        )


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
            ("cod_escola", "codEscola", "019465"),
            ("cod_turma", "codTurma", 3030050),
            ("tipo_turma", "tipoTurma", 1),
            ("ano", "ano", "1"),
            ("ano_letivo", "anoLetivo", 2026),
            ("cod_modalidade", "codModalidade", 5),
            ("cod_dre", "codDre", "108100"),
            ("dre", "dre", "DRE TESTE"),
            ("dre_abrev", "dreAbrev", "DRE-T"),
            ("modalidade", "modalidade", "Fundamental"),
            ("nome_turma", "nomeTurma", "1A"),
            ("semestre", "semestre", 0),
            ("tipo_ue", "tipoUE", "EMEF"),
            ("cod_tipo_ue", "codTipoUE", 1),
            ("cod_ue", "codUe", "019465"),
            ("ue", "ue", "EMEF TESTE"),
            ("ue_abrev", "ueAbrev", "EMEF T."),
            ("tipo_escola", "tipoEscola", "EMEF"),
            ("cod_tipo_escola", "codTipoEscola", 1),
            ("duracao_turno", "duracaoTurno", 5),
            ("tipo_turno", "tipoTurno", 4),
            ("ensino_especial", "ensinoEspecial", False),
            ("serie_ensino", "serieEnsino", "1 ANO"),
            ("data_inicio_turma", "dataInicioTurma", "2024-02-01T00:00:00"),
            ("data_fim_turma", "dataFimTurma", None),
            ("extinta", "extinta", False),
        ]
        payload = {entrada: valor for entrada, _, valor in mapeamento}
        esperado = {saida: valor for _, saida, valor in mapeamento}

        self.assertEqual(
            TurmaAtribuidaProfessorSerializer(payload).data, esperado
        )
