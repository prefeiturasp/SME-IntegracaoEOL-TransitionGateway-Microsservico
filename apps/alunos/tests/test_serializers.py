"""Testes dos serializers do domínio de alunos."""

from django.test import SimpleTestCase

from apps.alunos.serializers import AlunoMatriculaTurmaSerializer


class AlunoMatriculaTurmaSerializerTest(SimpleTestCase):
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
            "data_atualizacao_contato": ("2021-07-29T19:53:02.270000-03:00"),
            "sequencia": 1,
            "codigo_dre": "108100",
        }

        data = AlunoMatriculaTurmaSerializer(payload).data

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

    def test_datetime_z_false_publica_datas_sem_sufixo_z(self) -> None:
        """``datetime_z=False`` publica as datas no formato ISO sem o ``Z``."""
        payload = {
            "codigo_aluno": 7730117,
            "nome_aluno": "ENZO MIGUEL FERREIRA SILVA",
            "data_nascimento": "2020-07-10",
            "data_situacao": "2025-12-08T11:42:14.660000-03:00",
            "data_matricula": "2025-11-04T08:16:14.260000-03:00",
            "data_atualizacao_contato": ("2021-07-29T19:53:02.270000-03:00"),
            "possui_deficiencia": False,
            "codigo_turma": 3012185,
            "ano_letivo": 2026,
        }

        data = AlunoMatriculaTurmaSerializer(payload, datetime_z=False).data

        self.assertEqual(data["dataNascimento"], "2020-07-10T00:00:00")
        self.assertEqual(data["dataSituacao"], "2025-12-08T11:42:14.66")
        self.assertEqual(data["dataMatricula"], "2025-11-04T08:16:14.26")
        self.assertEqual(
            data["dataAtualizacaoContato"], "2021-07-29T19:53:02.27"
        )

    def test_datetime_z_false_propaga_campos_parciais_em_many(self) -> None:
        """``datetime_z`` e ``campos_parciais`` propagam com ``many=True``."""
        payload = [
            {
                "codigo_aluno": 1,
                "data_nascimento": "2020-07-10",
                "possui_deficiencia": False,
                "codigo_turma": 99,
                "ano_letivo": 2026,
            }
        ]

        data = AlunoMatriculaTurmaSerializer(
            payload, many=True, campos_parciais=True, datetime_z=False
        ).data

        self.assertEqual(data[0]["dataNascimento"], "2020-07-10T00:00:00")
        self.assertEqual(data[0]["codigoTurma"], 0)
        self.assertEqual(data[0]["ano"], 0)

    def test_campos_parciais_zera_localizacao_turma(self) -> None:
        """``campos_parciais`` zera ano/dre/escola/turma, mantém o resto."""
        payload = {
            "codigo_aluno": 7730117,
            "nome_aluno": "ENZO MIGUEL FERREIRA SILVA",
            "numero_aluno_chamada": "12",
            "possui_deficiencia": False,
            "codigo_turma": 3012185,
            "codigo_escola": "097144",
            "ano_letivo": 2026,
            "codigo_dre": "108100",
            "sequencia": 1,
        }

        completo = AlunoMatriculaTurmaSerializer(payload).data
        parcial = AlunoMatriculaTurmaSerializer(
            payload, campos_parciais=True
        ).data

        self.assertEqual(completo["codigoTurma"], 3012185)
        self.assertEqual(completo["ano"], 2026)
        self.assertEqual(parcial["ano"], 0)
        self.assertIsNone(parcial["codigoDre"])
        self.assertIsNone(parcial["codigoEscola"])
        self.assertEqual(parcial["codigoTurma"], 0)
        self.assertEqual(parcial["codigoAluno"], 7730117)
        self.assertEqual(parcial["sequencia"], 1)

    def test_numero_chamada_null_conforme_modo(self) -> None:
        """Sem chamada: ``null`` no modo parcial e ``"000"`` no completo."""
        payload = {
            "codigo_aluno": 7730117,
            "nome_aluno": "ENZO MIGUEL FERREIRA SILVA",
            "numero_aluno_chamada": None,
            "possui_deficiencia": False,
            "codigo_turma": 3012185,
            "ano_letivo": 2026,
        }

        completo = AlunoMatriculaTurmaSerializer(payload).data
        parcial = AlunoMatriculaTurmaSerializer(
            payload, campos_parciais=True
        ).data

        self.assertEqual(completo["numeroAlunoChamada"], "000")
        self.assertIsNone(parcial["numeroAlunoChamada"])

    def test_campos_parciais_propaga_em_many(self) -> None:
        """O flag ``campos_parciais`` é propagado para ``many=True``."""
        payload = [
            {
                "codigo_aluno": 1,
                "numero_aluno_chamada": "1",
                "possui_deficiencia": False,
                "codigo_turma": 99,
                "ano_letivo": 2026,
            }
        ]

        data = AlunoMatriculaTurmaSerializer(
            payload, many=True, campos_parciais=True
        ).data

        self.assertEqual(data[0]["codigoTurma"], 0)
        self.assertEqual(data[0]["ano"], 0)
