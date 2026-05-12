"""Testes das funções de service do domínio pedagógico."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.pedagogico import services

_BASE = "/api/v1/componentes-curriculares"


class GetComponentesFuncionarioTest(SimpleTestCase):
    """Testes de services.get_componentes_funcionario."""

    @patch("apps.pedagogico.services._client")
    def test_sem_turma_envia_apenas_id_perfil(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_funcionario("login1", "P001")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/funcionarios/login1",
            params={"idPerfil": "P001"},
        )
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_com_turma_envia_params_completos(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value.json.return_value = []

        services.get_componentes_funcionario(
            "login1",
            "P001",
            codigo_turma="T001",
            agrupa=True,
            planejamento=True,
            checa_motivo_disponibilizacao=False,
            considera_turma_infantil=False,
        )

        _, kwargs = mock_client.get.call_args
        params = kwargs["params"]
        self.assertEqual(params["codigoTurma"], "T001")
        self.assertTrue(params["agrupaComponenteCurricular"])
        self.assertTrue(params["planejamento"])
        self.assertFalse(params["checaMotivoDisponibilizacao"])
        self.assertFalse(params["consideraTurmaInfantil"])


class GetComponentesRegenciaTest(SimpleTestCase):
    """Testes de services.get_componentes_regencia."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_regencia(1)

        mock_client.get.assert_called_once_with(f"{_BASE}/anos/1/regencia")
        self.assertEqual(result, [])


class ValidarPapTest(SimpleTestCase):
    """Testes de services.validar_pap."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = True

        result = services.validar_pap("T001", "login1", "P001")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/T001/pap",
            params={"login": "login1", "idPerfil": "P001"},
        )
        self.assertTrue(result)


class GetComponentesUeAnosTest(SimpleTestCase):
    """Testes de services.get_componentes_ue_anos."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_ue_anos("UE001", 5, 2024, ["1", "2"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024",
            params={"anosEscolares": ["1", "2"]},
        )
        self.assertEqual(result, [])


class GetComponentesTurmasProgramaTest(SimpleTestCase):
    """Testes de services.get_componentes_turmas_programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_turmas_programa("UE001", 5, 2024)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024/turmas-programa"
        )
        self.assertEqual(result, [])


class GetComponentesPorTurmasUeTest(SimpleTestCase):
    """Testes de services.get_componentes_por_turmas_ue."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_turmas(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_por_turmas_ue(
            "UE001", ["T001", "T002"]
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/turmas",
            params={"turmas": ["T001", "T002"]},
        )
        self.assertEqual(result, [])


class GetComponentesPlanejamentoTest(SimpleTestCase):
    """Testes de services.get_componentes_planejamento."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_planejamento(["T001", "T002"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas",
            params={
                "codigoTurmas": ["T001", "T002"],
                "adicionarComponentesPlanejamento": True,
            },
        )
        self.assertEqual(result, [])


class GetComponentesBrutosTest(SimpleTestCase):
    """Testes de services.get_componentes_brutos."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_brutos(["T001"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/brutos",
            params={"codigoTurmas": ["T001"]},
        )
        self.assertEqual(result, [])


class GetCatalogoComponentesTest(SimpleTestCase):
    """Testes de services.get_catalogo_componentes."""

    @patch("apps.pedagogico.services._client")
    def test_chama_base_sem_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_catalogo_componentes()

        mock_client.get.assert_called_once_with(_BASE)
        self.assertEqual(result, [])


class GetVigenciaComponentesTest(SimpleTestCase):
    """Testes de services.get_vigencia_componentes."""

    @patch("apps.pedagogico.services._client")
    def test_sem_semestre_omite_param(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        services.get_vigencia_componentes(
            "UE001", "2024", ["1"], semestre=None
        )

        _, kwargs = mock_client.get.call_args
        self.assertNotIn("semestre", kwargs["params"])

    @patch("apps.pedagogico.services._client")
    def test_com_semestre_inclui_param(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        services.get_vigencia_componentes("UE001", "2024", ["1"], semestre="1")

        _, kwargs = mock_client.get.call_args
        self.assertEqual(kwargs["params"]["semestre"], "1")


class GetGradeCurricularTest(SimpleTestCase):
    """Testes de services.get_grade_curricular."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_grade_curricular(2024)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/grade-curricular/2024"
        )
        self.assertEqual(result, [])


class GetSemAtribuicaoTest(SimpleTestCase):
    """Testes de services.get_sem_atribuicao."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_data_base(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_sem_atribuicao("T001", "637500000000000000")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/T001/sem-atribuicao",
            params={"dataBase": "637500000000000000"},
        )
        self.assertEqual(result, [])


class GetAgrupamentosCorrelacionadosTest(SimpleTestCase):
    """Testes de services.get_agrupamentos_correlacionados."""

    @patch("apps.pedagogico.services._client")
    def test_sem_data_base_passa_params_none(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value.json.return_value = []

        services.get_agrupamentos_correlacionados(1)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/1/territorio-saber/agrupamentos-correlacionados",
            params=None,
        )

    @patch("apps.pedagogico.services._client")
    def test_com_data_base_inclui_param(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        services.get_agrupamentos_correlacionados(
            1, data_base="637500000000000000"
        )

        _, kwargs = mock_client.get.call_args
        self.assertEqual(kwargs["params"]["dataBase"], "637500000000000000")


class GetAgrupamentosCorrelacionadosLoteTest(SimpleTestCase):
    """Testes de services.get_agrupamentos_correlacionados_lote."""

    @patch("apps.pedagogico.services._client")
    def test_sem_data_base_passa_params_none(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.post.return_value.json.return_value = []

        services.get_agrupamentos_correlacionados_lote([1, 2])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos-correlacionados",
            payload=[1, 2],
            params=None,
        )

    @patch("apps.pedagogico.services._client")
    def test_com_data_base_inclui_param(self, mock_client: MagicMock) -> None:
        mock_client.post.return_value.json.return_value = []

        services.get_agrupamentos_correlacionados_lote(
            [1], data_base="637500000000000000"
        )

        _, kwargs = mock_client.post.call_args
        self.assertEqual(kwargs["params"]["dataBase"], "637500000000000000")


class GetAgrupamentosTest(SimpleTestCase):
    """Testes de services.get_agrupamentos."""

    @patch("apps.pedagogico.services._client")
    def test_chama_post_com_payload(self, mock_client: MagicMock) -> None:
        mock_client.post.return_value.json.return_value = []

        result = services.get_agrupamentos([1, 2, 3])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos",
            payload=[1, 2, 3],
        )
        self.assertEqual(result, [])
