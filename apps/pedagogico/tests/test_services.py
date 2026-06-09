"""Valida os serviços do domínio pedagógico."""

from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase

from apps.pedagogico import services

_BASE = "/api/v1/pedagogico/componentes-curriculares"
_BASE_TURMAS = "/api/v1/pedagogico/turmas"
_TURMA_MS = {
    "codigo": 3034092,
    "ano_letivo": 2026,
    "ano": "1",
    "tipo_turma": 1,
    "nome_turma": "1A",
    "duracao_turno": 55,
    "tipo_turno": 6,
    "data_inicio_turma": "2026-02-04T03:00:00Z",
    "data_fim": None,
    "extinta": False,
    "situacao": "O",
    "ue_codigo": "092622",
    "serie_ensino": "1o Ano",
    "codigo_serie_ensino": 84,
    "modalidade": "Fundamental",
    "codigo_modalidade": 5,
    "semestre": 0,
    "ensino_especial": False,
}


class PostTurmasRegularesTest(SimpleTestCase):
    """Valida a consulta de turmas regulares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [
            {"codigo": 3014194, "nome_turma": "1D"},
            {"codigo": 3024590, "nome_turma": "1B"},
        ]

        result = services.post_turmas_regulares(["3024590", "3014194"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-regulares/",
            payload=[3024590, 3014194],
        )
        self.assertEqual(result, ["3014194", "3024590"])

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        result = services.post_turmas_regulares([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])


class PostTurmasProgramaTest(SimpleTestCase):
    """Valida a consulta de turmas programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [
            {"codigo": 3133093, "nome_turma": "1A"},
            {"codigo": 3133096, "nome_turma": "1A"},
        ]

        result = services.post_turmas_programa(["3133093", "3133096"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-programa/",
            payload=[3133093, 3133096],
        )
        self.assertEqual(result, ["3133093", "3133096"])

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        result = services.post_turmas_programa([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_quando_ms_responde_sem_corpo(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.post.return_value = httpx.Response(200, content=b"")
        mock_client.json_or_none.return_value = None

        result = services.post_turmas_programa(["3133093"])

        mock_client.json_or_none.assert_called_once_with(
            mock_client.post.return_value
        )
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_aceita_payload_ms_com_lista_de_strings(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = ["3133093", "3133096"]

        result = services.post_turmas_programa(["3133093", "3133096"])

        self.assertEqual(result, ["3133093", "3133096"])

    @patch("apps.pedagogico.services._client")
    def test_aceita_payload_ms_com_lista_de_inteiros(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = [3133093, 3133096]

        result = services.post_turmas_programa(["3133093", "3133096"])

        self.assertEqual(result, ["3133093", "3133096"])


class PostListarTurmasTest(SimpleTestCase):
    """Valida a listagem de dados de turmas."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.post.return_value.json.return_value = [_TURMA_MS]

        result = services.post_listar_turmas(["3034092"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[3034092],
        )
        self.assertEqual(result[0]["codigo"], 3034092)
        self.assertEqual(result[0]["anoLetivo"], 2026)
        self.assertEqual(result[0]["nomeTurma"], "1A")
        self.assertEqual(result[0]["dataInicioTurma"], "2026-02-04T00:00:00")
        self.assertEqual(result[0]["modalidade"], None)
        self.assertEqual(result[0]["codigoModalidade"], 0)
        self.assertEqual(result[0]["serieEnsino"], None)
        self.assertEqual(result[0]["situacao"], None)
        self.assertEqual(result[0]["ehistorico"], False)
        self.assertEqual(result[0]["etapaEJA"], 0)

    @patch("apps.pedagogico.services._client")
    def test_preserva_fracao_minima_de_data_fim(
        self,
        mock_client: MagicMock,
    ) -> None:
        turma = {
            **_TURMA_MS,
            "data_fim": "2025-09-11T15:13:34.040000Z",
        }
        mock_client.post.return_value.json.return_value = [turma]

        result = services.post_listar_turmas(["3029408"])

        self.assertEqual(result[0]["dataFim"], "2025-09-11T12:13:34.04")

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        result = services.post_listar_turmas([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])


class GetDadosTurmaTest(SimpleTestCase):
    """Valida a consulta de dados de uma turma."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = _TURMA_MS

        result = services.get_dados_turma("3034092")

        mock_client.get.assert_called_once_with(
            f"{_BASE_TURMAS}/3034092/dados/"
        )
        self.assertEqual(result["codigo"], 3034092)
        self.assertEqual(result["tipoTurma"], 1)
        self.assertEqual(result["ueCodigo"], "092622")
        self.assertEqual(result["modalidade"], None)
        self.assertEqual(result["codigoModalidade"], 0)
        self.assertEqual(result["serieEnsino"], None)
        self.assertEqual(result["situacao"], None)
        self.assertEqual(result["ehistorico"], False)
        self.assertEqual(result["etapaEJA"], 0)


class GetComponentesUeAnosTest(SimpleTestCase):
    """Valida a consulta de componentes por anos escolares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os anos escolares como query params."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_ue_anos(
            "UE001",
            5,
            2024,
            ["1", "2"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024",
            params={"anos_escolares": ["1", "2"]},
        )

        self.assertEqual(result, [])


class GetComponentesTurmasProgramaTest(SimpleTestCase):
    """Valida a consulta de componentes de turmas programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de turmas programa por UE e modalidade."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_turmas_programa(
            "UE001",
            5,
            2024,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/modalidades/5/anos/2024/turmas-programa"
        )

        self.assertEqual(result, [])


class GetComponentesRegenciaTest(SimpleTestCase):
    """Valida a consulta de componentes de regência."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_regencia(2024)

        mock_client.get.assert_called_once_with(f"{_BASE}/anos/2024/regencia")

        self.assertEqual(result, [])


class ValidarComponentePapTest(SimpleTestCase):
    """Valida a consulta de componente PAP por turma e funcionário."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = True

        result = services.validar_componente_pap("T001", "RF001", "P1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/T001/pap",
            params={"login": "RF001", "idPerfil": "P1"},
        )

        self.assertTrue(result)


class GetComponentesFuncionarioTest(SimpleTestCase):
    """Valida a consulta de componentes por funcionário."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_funcionario("RF001", "P1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/funcionarios/RF001",
            params={"idPerfil": "P1"},
        )

        self.assertEqual(result, [])


class GetComponentesTurmaFuncionarioTest(SimpleTestCase):
    """Valida a consulta de componentes por turma e funcionário."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_filtros(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_turma_funcionario(
            "T001",
            "RF001",
            "P1",
            True,
            checa_motivo_disponibilizacao=False,
            considera_turma_infantil=True,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/funcionarios/RF001",
            params={
                "idPerfil": "P1",
                "codigoTurma": "T001",
                "agrupaComponenteCurricular": True,
                "checaMotivoDisponibilizacao": False,
                "consideraTurmaInfantil": True,
            },
        )
        self.assertEqual(result, [])


class GetComponentesPlanejamentoTest(SimpleTestCase):
    """Valida a consulta de componentes de planejamento."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_planejamento(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_planejamento("T001", "RF001", "P1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/funcionarios/RF001",
            params={
                "idPerfil": "P1",
                "codigoTurma": "T001",
                "planejamento": True,
            },
        )
        self.assertEqual(result, [])


class GetComponentesPorListaTurmasTest(SimpleTestCase):
    """Valida a consulta de componentes por lista de turmas."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_filtros(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_por_lista_turmas(
            ["T001", "T002"],
            adicionar_componentes_planejamento=False,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas",
            params={
                "codigoTurmas": ["T001", "T002"],
                "adicionarComponentesPlanejamento": False,
            },
        )
        self.assertEqual(result, [])


class GetComponentesTurmasRegularesTest(SimpleTestCase):
    """Valida a consulta de componentes de turmas regulares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_turmas(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_turmas_regulares(["T001", "T002"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/brutos",
            params={"codigoTurmas": ["T001", "T002"]},
        )
        self.assertEqual(result, [])


class GetDadosAulaTurmaTest(SimpleTestCase):
    """Valida a consulta de dados de aula por turma."""

    @patch("apps.pedagogico.services._client")
    def test_mapeia_resposta_para_legado(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.get.return_value.json.return_value = [
            {
                "componente_codigo": "138",
                "componente_descricao": "LINGUA PORTUGUESA",
                "turma_codigo": "T001",
                "data_inicio_turma": "2024-02-05T03:00:00Z",
            }
        ]

        result = services.get_dados_aula_turma(
            "UE001",
            2024,
            ["138"],
            1,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/vigencia",
            params={
                "ueCodigo": "UE001",
                "anoLetivo": 2024,
                "componentesCurriculares": ["138"],
                "semestre": 1,
            },
        )
        self.assertEqual(
            result,
            [
                {
                    "componenteCurricularCodigo": "138",
                    "componenteCurricularDescricao": "LINGUA PORTUGUESA",
                    "turmaCodigo": "T001",
                    "dataInicioTurma": "2024-02-05T00:00:00",
                }
            ],
        )


class GetComponentesSemAtribuicaoTest(SimpleTestCase):
    """Valida a consulta de componentes sem atribuição."""

    @patch("apps.pedagogico.services._client")
    def test_converte_ticks_para_data_iso(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.get.return_value.json.return_value = ["ARTE"]

        result = services.get_componentes_sem_atribuicao(
            "T001",
            638396640000000000,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/T001/sem-atribuicao",
            params={"data_base": "2024-01-01"},
        )
        self.assertEqual(result, ["ARTE"])


class GetComponentesPorTurmasUeTest(SimpleTestCase):
    """Valida a consulta de componentes por turmas de uma UE."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_com_query_params(self, mock_client: MagicMock) -> None:
        """Monta o path e repassa as turmas como query param."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_por_turmas_ue(
            "UE001",
            ["T001", "T002"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/ues/UE001/turmas",
            params={"turmas": ["T001", "T002"]},
        )

        self.assertEqual(result, [])


class GetCatalogoComponentesTest(SimpleTestCase):
    """Valida a consulta do catálogo de componentes curriculares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_base_sem_params(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Consulta o catálogo na rota base, sem query params."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_componentes_curriculares()

        mock_client.get.assert_called_once_with(_BASE)

        self.assertEqual(result, [])


class GetGradeCurricularTest(SimpleTestCase):
    """Valida a consulta da grade curricular."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Monta o path da grade curricular pelo ano letivo."""
        mock_client.get.return_value.json.return_value = []

        result = services.get_grade_curricular(2024)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/grade-curricular/2024"
        )

        self.assertEqual(result, [])
