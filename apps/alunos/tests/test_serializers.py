"""Testes dos serializers do domínio de alunos."""

from django.test import SimpleTestCase

from apps.alunos.serializers import AlunoAtivoDataAulaSerializer


class AlunoAtivoDataAulaSerializerTest(SimpleTestCase):
    """Valida a serialização de alunos ativos na data da aula."""

    def test_serializa_item_no_contrato_legado(self) -> None:
        payload = {
            "codigo_aluno": 7730117,
            "nome_aluno": "ENZO MIGUEL FERREIRA SILVA",
            "nome_social_aluno": None,
            "data_nascimento": "2020-07-10",
            "codigo_situacao_matricula": 1,
            "situacao_matricula": "Ativo",
            "data_situacao": "2025-12-08T11:42:14.660000-03:00",
            "numero_aluno_chamada": None,
            "possui_deficiencia": False,
            "codigo_matricula": 43790514,
            "codigo_turma": 3012185,
            "codigo_escola": "097144",
            "ano_letivo": 2026,
            "data_matricula": "2025-11-04T08:16:14.260000-03:00",
            "nome_responsavel": "MARIAZINHA FERREIRA SILVA",
            "tipo_responsavel": 1,
            "celular_responsavel": None,
            "data_atualizacao_contato": (
                "2021-07-29T19:53:02.270000-03:00"
            ),
            "sequencia": 1,
            "codigo_dre": "108100",
        }

        data = AlunoAtivoDataAulaSerializer(payload).data

        self.assertEqual(
            data,
            {
                "codigoComponenteCurricular": 0,
                "codigoAluno": 7730117,
                "nomeAluno": "ENZO MIGUEL FERREIRA SILVA",
                "dataNascimento": "2020-07-10T00:00:00Z",
                "nomeSocialAluno": None,
                "codigoSituacaoMatricula": 1,
                "situacaoMatricula": "Ativo",
                "dataSituacao": "2025-12-08T11:42:14.66Z",
                "dataMatricula": "2025-11-04T08:16:14.26Z",
                "numeroAlunoChamada": "000",
                "possuiDeficiencia": 0,
                "transferencia_Interna": False,
                "remanejado": False,
                "escolaTransferencia": None,
                "turmaTransferencia": None,
                "turmaRemanejamento": None,
                "parecerConclusivo": None,
                "nomeResponsavel": "MARIAZINHA FERREIRA SILVA",
                "tipoResponsavel": 1,
                "celularResponsavel": "",
                "dataAtualizacaoContato": "2021-07-29T19:53:02.27Z",
                "codigoMatricula": 43790514,
                "sequencia": 1,
                "tipoTurma": 0,
                "codigoTurma": 3012185,
                "codigoEscola": "097144",
                "ano": 2026,
                "codigoDre": "108100",
                "id": None,
            },
        )
