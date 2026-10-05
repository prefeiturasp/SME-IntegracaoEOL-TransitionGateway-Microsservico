"""Preserva o contrato e a representação em lote dos alunos da UE."""

from copy import deepcopy
from datetime import UTC, date, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import fields

from apps.alunos.serializers import AlunoDaUeSerializer

_LINHA = {
    "codigo_aluno": "123",
    "ano_letivo": "2026",
    "nome_aluno": "ALUNO FICTICIO",
    "nome_social_aluno": None,
    "codigo_situacao_matricula": "1",
    "situacao_matricula": "Ativo",
    "data_situacao": "2026-02-03T13:00:00.120000Z",
    "data_nascimento": "2015-01-02",
    "numero_aluno_chamada": None,
    "codigo_turma": "456",
    "nome_responsavel": None,
    "tipo_responsavel": 1,
    "ddd_celular": "",
    "numero_celular": "",
    "data_atualizacao_contato": None,
    "codigo_tipo_turma": "1",
    "data_atualizacao_tabela": None,
    "tipo_turno": "2",
    "turma_nome": "5A",
    "etapa_ensino": "5",
    "ciclo_ensino": "2",
    "desc_etapa_ensino": "Ensino Fundamental",
    "desc_ciclo_ensino": "Ciclo de teste",
}
_ESPERADO = {
    "codigoAluno": 123,
    "anoLetivo": 2026,
    "nomeAluno": "ALUNO FICTICIO",
    "nomeSocialAluno": None,
    "codigoSituacaoMatricula": 1,
    "situacaoMatricula": "Ativo",
    "dataSituacao": "2026-02-03T10:00:00.12",
    "dataNascimento": "2015-01-02T00:00:00",
    "numeroAlunoChamada": "0",
    "codigoTurma": 456,
    "nomeResponsavel": None,
    "tipoResponsavel": "1",
    "celularResponsavel": "",
    "dataAtualizacaoContato": None,
    "codigoTipoTurma": 1,
    "dataAtualizacaoTabela": "2026-02-03T10:00:00.12",
    "tipoTurno": 2,
    "turmaNome": "5A",
    "etapaEnsino": 5,
    "cicloEnsino": 2,
    "descEtapaEnsino": "Ensino Fundamental",
    "descCicloEnsino": "Ciclo de teste",
}


class AlunoDaUePerformanceTest(SimpleTestCase):
    """Mantém coerções, valores padrão e ordem sem resolver campos planos."""

    def test_lote_completo_evitar_resolucao_generica_repetida(self) -> None:
        """Lê diretamente as colunas simples e preserva campos especiais."""
        resolver_original = fields.get_attribute

        def resolver(instance: Any, attrs: list[str]) -> Any:
            if attrs and attrs != ["numero_aluno_chamada"]:
                raise AssertionError("Resolução genérica em campo plano")
            return resolver_original(instance, attrs)

        entrada = deepcopy(_LINHA)
        entrada["campo_extra"] = "não publicado"
        original = deepcopy(entrada)
        with patch.object(fields, "get_attribute", side_effect=resolver):
            resultado = AlunoDaUeSerializer([entrada, entrada], many=True).data
        self.assertEqual(resultado, [_ESPERADO, _ESPERADO])
        self.assertEqual(list(resultado[0]), list(_ESPERADO))
        self.assertEqual(entrada, original)

    def test_preserva_nulos_ausencias_e_objetos(self) -> None:
        """Não confunde valor nulo com campo ausente nem perde defaults."""
        esperado = {
            **dict.fromkeys(_ESPERADO),
            "numeroAlunoChamada": "0",
            "celularResponsavel": "",
            "dataAtualizacaoTabela": "0001-01-01T00:00:00",
        }
        self.assertEqual(
            AlunoDaUeSerializer(dict.fromkeys(_LINHA)).data, esperado
        )
        self.assertEqual(
            AlunoDaUeSerializer({}).data, {**esperado, "tipoTurno": 0}
        )
        self.assertEqual(
            AlunoDaUeSerializer(SimpleNamespace(**_LINHA)).data, _ESPERADO
        )

    def test_preserva_chamada_e_prioridade_do_contato(self) -> None:
        """Mantém zeros da chamada e a preferência por celular informado."""
        for chamada, esperada in (
            (None, "0"),
            ("", "0"),
            (0, "0"),
            ("001", "001"),
            (12, "12"),
        ):
            with self.subTest(chamada=chamada):
                entrada = {**_LINHA, "numero_aluno_chamada": chamada}
                self.assertEqual(
                    AlunoDaUeSerializer(entrada).data["numeroAlunoChamada"],
                    esperada,
                )
        entrada = {**_LINHA, "ddd_celular": "11", "numero_celular": "0000"}
        self.assertEqual(
            AlunoDaUeSerializer(entrada).data["celularResponsavel"], "110000"
        )
        entrada["celular_responsavel"] = ""
        self.assertEqual(
            AlunoDaUeSerializer(entrada).data["celularResponsavel"], ""
        )

    def test_preserva_datas_e_prioridade_da_atualizacao(self) -> None:
        """Preserva datas, fusos, frações e a atualização informada."""
        entrada = {
            **_LINHA,
            "data_nascimento": date(2015, 1, 2),
            "data_atualizacao_tabela": datetime(2026, 3, 1, 12, tzinfo=UTC),
            "data_atualizacao_contato": "2026-02-03T09:30:00.001000-03:00",
        }
        esperado = {
            **_ESPERADO,
            "dataAtualizacaoTabela": "2026-03-01T09:00:00",
            "dataAtualizacaoContato": "2026-02-03T09:30:00.001",
        }
        self.assertEqual(AlunoDaUeSerializer(entrada).data, esperado)

    def test_preserva_erro_de_inteiro_invalido(self) -> None:
        """Não converte dados inválidos em valor padrão silencioso."""
        with self.assertRaises(ValueError):
            _ = AlunoDaUeSerializer({**_LINHA, "codigo_aluno": "x"}).data
