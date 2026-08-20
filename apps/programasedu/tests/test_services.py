"""Valida os serviços do domínio de programas educacionais."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.programasedu import services


class ListarTurmasPapTest(SimpleTestCase):
    """Valida a consulta de turmas PAP."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de turmas PAP."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"codigoTurma": "X", "turmaNome": "1A"}]
        mock_get.return_value = mock_resp

        result = services.listar_turmas_pap(
            ano_letivo=2026, codigo_escola="123"
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/turmas-pap/2026/ues/123"
        )
        self.assertEqual(result, [{"codigoTurma": "X", "turmaNome": "1A"}])


class VerificarAlunosPapTest(SimpleTestCase):
    """Valida a verificação de alunos em turmas PAP."""

    @patch.object(services._client, "get")
    def test_propaga_codigos_alunos(self, mock_get: MagicMock) -> None:
        """Verifica que os codigos dos alunos sao enviados como parametro."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.verificar_alunos_pap(
            ano_letivo=2026, codigos_alunos=["1", "2"]
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/alunos-pap/2026",
            params={"codigos_alunos": ["1", "2"]},
        )


class ListarAlunosPapAnoCorrenteTest(SimpleTestCase):
    """Valida a consulta de alunos PAP do ano corrente."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de alunos PAP do ano corrente."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_ano_corrente()

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-corrente"
        )


class ListarAlunosPapPorAnoTest(SimpleTestCase):
    """Valida a consulta de alunos PAP por ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de alunos PAP por ano letivo."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_alunos_pap_por_ano(ano_letivo=2026)

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-letivo/2026"
        )


class ListarComponentesTurmasProgramaAlunoTest(SimpleTestCase):
    """Valida a consulta de componentes das turmas de programa do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de componentes do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="123", ano_letivo=2026
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/123/turmas-programa/2026"
            "/componentes-curriculares"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="7410182", ano_letivo=2026
        )

        self.assertEqual(result, [])


class ObterDadosSrmPaeeAlunoTest(SimpleTestCase):
    """Valida a consulta de dados de SRM/PAEE colaborativo do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de SRM/PAEE do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.obter_dados_srm_paee_aluno(codigo_aluno="123")

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/srm-paee/aluno/123"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.obter_dados_srm_paee_aluno(codigo_aluno="7410182")

        self.assertEqual(result, [])


class ObterTurmaSrmERegularDoAlunoTest(SimpleTestCase):
    """Valida a orquestração de turmas SRM e regulares do aluno."""

    @patch("apps.programasedu.services.pedagogico_services.listar_turmas")
    @patch("apps.programasedu.services.obter_dados_srm_paee_aluno")
    @patch(
        "apps.programasedu.services.alunos_services."
        "get_turmas_aluno_com_programa"
    )
    def test_filtra_regular_ou_srm_e_compoe_shape(
        self,
        mock_turmas: MagicMock,
        mock_srm: MagicMock,
        mock_listar: MagicMock,
    ) -> None:
        """Verifica o filtro regular-ou-SRM e a composição dos campos."""
        mock_turmas.return_value = [
            {
                "codigo_aluno": 7000001,
                "ano_letivo": 2026,
                "nome_aluno": "ALUNO FICTICIO",
                "nome_social_aluno": None,
                "codigo_situacao_matricula": 11,
                "situacao_matricula": "Deslocamento",
                "data_situacao": "2026-01-06",
                "data_nascimento": "2025-11-05",
                "numero_aluno_chamada": None,
                "codigo_turma": 9100001,
                "nome_responsavel": "RESPONSAVEL FICTICIO",
                "tipo_responsavel": 1,
                "ddd_celular": "11",
                "numero_celular": "988887777",
                "data_atualizacao_contato": "2025-01-23",
                "codigo_tipo_turma": 1,
            },
            {
                "codigo_aluno": 7000001,
                "ano_letivo": 2026,
                "codigo_turma": 555,
                "codigo_tipo_turma": 3,
                "ddd_celular": None,
                "numero_celular": None,
            },
            {
                "codigo_aluno": 7000001,
                "ano_letivo": 2026,
                "codigo_turma": 999,
                "codigo_tipo_turma": 3,
            },
        ]
        mock_srm.return_value = [{"codigo_turma": 555}]
        mock_listar.return_value = [
            {
                "codigo": 9100001,
                "nome_turma": "2B",
                "tipo_turno": 1,
                "codigo_etapa_ensino": 5,
                "codigo_ciclo_ensino": 3,
            },
            {
                "codigo": 555,
                "nome_turma": "SRM",
                "tipo_turno": 2,
                "codigo_etapa_ensino": 1,
                "codigo_ciclo_ensino": 2,
            },
        ]

        resultado = services.obter_turma_srm_e_regular_do_aluno("7000001")

        # Programa sem SRM (999) é descartado; sobram regular e SRM.
        self.assertEqual(
            sorted(r["codigo_turma"] for r in resultado), [555, 9100001]
        )
        regular = next(r for r in resultado if r["codigo_turma"] == 9100001)
        self.assertEqual(regular["tipo_turno"], 1)
        self.assertEqual(regular["turma_nome"], "2B")
        self.assertEqual(regular["etapa_ensino"], 5)
        self.assertEqual(regular["ciclo_ensino"], 3)
        self.assertEqual(regular["desc_etapa_ensino"], "FUND9A")
        # numero_aluno_chamada ausente → default "000" (paridade legado).
        self.assertEqual(regular["numero_aluno_chamada"], "000")
        self.assertEqual(regular["celular_responsavel"], "11988887777")
        self.assertIsNone(regular["desc_ciclo_ensino"])
        self.assertEqual(
            regular["data_atualizacao_tabela"], "0001-01-01T00:00:00"
        )

    @patch(
        "apps.programasedu.services.alunos_services."
        "get_turmas_aluno_com_programa"
    )
    def test_sem_turmas_retorna_vazio(self, mock_turmas: MagicMock) -> None:
        """Verifica que aluno sem turmas resulta em lista vazia."""
        mock_turmas.return_value = []

        self.assertEqual(
            services.obter_turma_srm_e_regular_do_aluno("123"), []
        )
