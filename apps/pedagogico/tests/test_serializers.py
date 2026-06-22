"""Valida serializers do dominio pedagogico."""

from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework import serializers

from apps.pedagogico.serializers import (
    AnosLetivosVigentesQuerySerializer,
    CodigoTurmaField,
    CodigoTurmaInteiroListSerializer,
    CodigoTurmaListSerializer,
    ItinerarioEnsinoMedioSerializer,
    SincronizacaoInstitucionalTurmaSerializer,
    TurmaDadosSerializer,
    TurmaHistoricaGeralSerializer,
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


class AnosLetivosVigentesQuerySerializerTest(SimpleTestCase):
    """Valida o filtro de anos letivos vigentes."""

    def test_valida_lista_de_anos(self) -> None:
        serializer = AnosLetivosVigentesQuerySerializer(
            data={"anos_letivos_vigente": ["2025", "2026"]}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["anos_letivos_vigente"],
            [2025, 2026],
        )

    def test_aceita_filtro_ausente(self) -> None:
        serializer = AnosLetivosVigentesQuerySerializer(data={})

        self.assertTrue(serializer.is_valid())
        self.assertNotIn(
            "anos_letivos_vigente",
            serializer.validated_data,
        )

    def test_aceita_lista_vazia(self) -> None:
        serializer = AnosLetivosVigentesQuerySerializer(
            data={"anos_letivos_vigente": []}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["anos_letivos_vigente"],
            [],
        )

    def test_rejeita_item_nao_inteiro(self) -> None:
        serializer = AnosLetivosVigentesQuerySerializer(
            data={"anos_letivos_vigente": ["2025", "invalido"]}
        )

        self.assertFalse(serializer.is_valid())

    def test_rejeita_item_booleano(self) -> None:
        serializer = AnosLetivosVigentesQuerySerializer(
            data={"anos_letivos_vigente": [True]}
        )

        self.assertFalse(serializer.is_valid())


class CodigoTurmaInteiroListSerializerTest(SimpleTestCase):
    """Valida a lista de códigos inteiros de turmas."""

    def test_serializa_lista_de_inteiros(self) -> None:
        serializer = CodigoTurmaInteiroListSerializer(
            [3036295, 3082921, 3036225]
        )

        self.assertEqual(serializer.data, [3036295, 3082921, 3036225])

    def test_valida_lista_vazia(self) -> None:
        serializer = CodigoTurmaInteiroListSerializer(data=[])

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, [])

    def test_rejeita_item_nao_inteiro(self) -> None:
        serializer = CodigoTurmaInteiroListSerializer(data=[3036295, "A"])

        self.assertFalse(serializer.is_valid())


class ItinerarioEnsinoMedioSerializerTest(SimpleTestCase):
    """Valida itinerários do ensino médio no contrato legado."""

    def test_converte_serie_textual_para_inteiro(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={
                "id": 9,
                "nome": "Investigação cientifica",
                "serie": "2",
                "campo_adicional": "não deve vazar",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {
                "id": 9,
                "nome": "Investigação cientifica",
                "serie": 2,
            },
        )

    def test_rejeita_serie_nao_numerica(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={"id": 9, "nome": "Itinerário", "serie": "segundo"}
        )

        self.assertFalse(serializer.is_valid())

    def test_rejeita_serie_que_nao_seja_texto(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={"id": 9, "nome": "Itinerário", "serie": 2}
        )

        self.assertFalse(serializer.is_valid())

    def test_rejeita_id_booleano(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={"id": True, "nome": "Itinerário", "serie": "2"}
        )

        self.assertFalse(serializer.is_valid())

    def test_rejeita_nome_que_nao_seja_texto(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={"id": 9, "nome": 10, "serie": "2"}
        )

        self.assertFalse(serializer.is_valid())

    def test_rejeita_campo_obrigatorio_ausente(self) -> None:
        serializer = ItinerarioEnsinoMedioSerializer(
            data={"id": 9, "nome": "Itinerário"}
        )

        self.assertFalse(serializer.is_valid())


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


class TurmaHistoricaGeralSerializerTest(SimpleTestCase):
    """Valida turmas históricas gerais no contrato legado."""

    def test_aplica_defaults_aos_campos_ausentes(self) -> None:
        serializer = TurmaHistoricaGeralSerializer(
            data={
                "ano": "7",
                "ano_letivo": 2025,
                "codigo": 2825477,
                "modalidade": "Infantil",
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.data,
            {
                "ano": "7",
                "anoLetivo": 2025,
                "codigo": 2825477,
                "tipoTurma": 0,
                "modalidade": "Infantil",
                "codigoModalidade": 1,
                "nomeTurma": "7A",
                "semestre": 0,
                "duracaoTurno": 0,
                "tipoTurno": 0,
                "dataFim": None,
                "ehistorico": False,
                "ensinoEspecial": False,
                "etapaEJA": 0,
                "serieEnsino": None,
                "dataInicioTurma": None,
                "extinta": False,
                "situacao": None,
                "ueCodigo": None,
            },
        )

    def test_preserva_campos_opcionais_retornados_pelo_ms(self) -> None:
        serializer = TurmaHistoricaGeralSerializer(
            data={
                "ano": "7",
                "ano_letivo": 2025,
                "codigo": 2825477,
                "tipo_turma": 2,
                "modalidade": "Infantil",
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 6,
                "tipo_turno": 1,
                "data_fim": "2025-12-20T00:00:00",
                "ehistorico": True,
                "ensino_especial": True,
                "etapa_eja": 3,
                "serie_ensino": "7o Ano",
                "data_inicio_turma": "2025-02-05T00:00:00",
                "extinta": True,
                "situacao": "E",
                "ue_codigo": "012345",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data["tipoTurma"], 2)
        self.assertEqual(serializer.data["duracaoTurno"], 6)
        self.assertEqual(serializer.data["dataFim"], "2025-12-20T00:00:00")
        self.assertIs(serializer.data["ehistorico"], True)
        self.assertEqual(serializer.data["ueCodigo"], "012345")

    def test_preserva_nulo_retornado_pelo_ms(self) -> None:
        serializer = TurmaHistoricaGeralSerializer(
            data={
                "ano": "7",
                "ano_letivo": 2025,
                "codigo": 2825477,
                "tipo_turma": None,
                "modalidade": "Infantil",
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
                "ehistorico": None,
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.data["tipoTurma"])
        self.assertIsNone(serializer.data["ehistorico"])

    def test_rejeita_campo_essencial_ausente(self) -> None:
        serializer = TurmaHistoricaGeralSerializer(
            data={
                "ano": "7",
                "ano_letivo": 2025,
                "modalidade": "Infantil",
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("codigo", serializer.errors)


class SincronizacaoInstitucionalTurmaSerializerTest(SimpleTestCase):
    """Valida os dados institucionais da turma no contrato legado."""

    def test_obtem_modalidade_de_objeto(self) -> None:
        serializer = SincronizacaoInstitucionalTurmaSerializer()

        self.assertEqual(
            serializer.get_modalidade(
                SimpleNamespace(codigo_modalidade=5)
            ),
            "5",
        )

    def test_retorna_modalidade_nula_de_objeto(self) -> None:
        serializer = SincronizacaoInstitucionalTurmaSerializer()

        self.assertIsNone(
            serializer.get_modalidade(SimpleNamespace())
        )

    def test_serializa_contrato_legado(self) -> None:
        serializer = SincronizacaoInstitucionalTurmaSerializer(
            {
                "ano": "7",
                "ano_letivo": 2026,
                "codigo": 3010807,
                "tipo_turma": 1,
                "modalidade": "Infantil",
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 6,
                "tipo_turno": 1,
                "data_fim_turma": None,
                "ensino_especial": False,
                "etapa_eja": 0,
                "serie_ensino": "INFANTIL UNIFICADO",
                "codigo_serie_ensino": 297,
                "data_inicio_turma": "2026-02-04T03:00:00Z",
                "extinta": False,
                "situacao": "O",
                "ue_codigo": "091120",
                "data_atualizacao": "2026-06-17T08:11:45.807000Z",
                "data_status_turma_escola": (
                    "2026-06-03T18:46:18.833000Z"
                ),
                "etapa_ensino": 1,
                "ciclo_ensino": 2,
                "tipo_escola": 2,
                "descricao_grade_programa": "INFANTIL UNIFICADO",
                "tipo_grade_programa": 1,
                "codigo_grade_programa": 4239,
                "nome_filtro": "7A - INFANTIL UNIFICADO",
                "componentes": [
                    {
                        "nome_componente_curricular": "ED.INF. EMEI 4 HS",
                        "componente_curricular_codigo": 512,
                        "registro_funcional": "7393423",
                        "data_disponibizacao": None,
                    }
                ],
            }
        )

        self.assertEqual(
            serializer.data,
            {
                "ano": "7",
                "anoLetivo": 2026,
                "codigo": 3010807,
                "tipoTurma": 1,
                "modalidade": "1",
                "codigoModalidade": 1,
                "nomeTurma": "7A",
                "semestre": 0,
                "duracaoTurno": 6,
                "tipoTurno": 1,
                "dataFimTurma": None,
                "ensinoEspecial": False,
                "etapaEJA": 0,
                "serieEnsino": "INFANTIL UNIFICADO",
                "dataInicioTurma": "2026-02-04T00:00:00",
                "extinta": False,
                "situacao": "O",
                "ueCodigo": "091120",
                "dataAtualizacao": "2026-06-17T05:11:45.807",
                "dataStatusTurmaEscola": "2026-06-03T15:46:18.833",
                "etapaEnsino": 1,
                "cicloEnsino": 2,
                "tipoEscola": 2,
                "descricaoGradePrograma": "INFANTIL UNIFICADO",
                "tipoGradePrograma": 1,
                "codigoGradePrograma": 4239,
                "nomeFiltro": "7A - INFANTIL UNIFICADO",
                "componentes": [
                    {
                        "nomeComponenteCurricular": "ED.INF. EMEI 4 HS",
                        "componenteCurricularCodigo": 512,
                        "registroFuncional": "7393423",
                        "dataDisponibizacao": None,
                    }
                ],
            },
        )

    def test_formata_data_disponibizacao_quando_preenchida(self) -> None:
        serializer = SincronizacaoInstitucionalTurmaSerializer(
            {
                "ano": "7",
                "ano_letivo": 2026,
                "codigo": 3010807,
                "tipo_turma": 1,
                "codigo_modalidade": 1,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 6,
                "tipo_turno": 1,
                "data_fim_turma": None,
                "ensino_especial": False,
                "etapa_eja": 0,
                "serie_ensino": "INFANTIL UNIFICADO",
                "data_inicio_turma": None,
                "extinta": False,
                "situacao": "O",
                "ue_codigo": "091120",
                "data_atualizacao": None,
                "data_status_turma_escola": None,
                "etapa_ensino": 1,
                "ciclo_ensino": 2,
                "tipo_escola": 2,
                "descricao_grade_programa": "INFANTIL UNIFICADO",
                "tipo_grade_programa": 1,
                "codigo_grade_programa": 4239,
                "nome_filtro": "7A - INFANTIL UNIFICADO",
                "componentes": [
                    {
                        "nome_componente_curricular": "ED.INF. EMEI 4 HS",
                        "componente_curricular_codigo": 512,
                        "registro_funcional": "7393423",
                        "data_disponibizacao": "2026-06-17T08:11:45Z",
                    }
                ],
            }
        )

        componente = serializer.data["componentes"][0]
        self.assertEqual(
            componente["dataDisponibizacao"],
            "2026-06-17T05:11:45",
        )
