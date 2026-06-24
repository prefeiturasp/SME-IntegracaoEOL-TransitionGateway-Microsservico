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


class ListarTurmasTest(SimpleTestCase):
    """Valida a listagem resumida de turmas."""

    @patch.object(services._client, "post")
    def test_retorna_payload_json(
        self,
        mock_post: MagicMock,
    ) -> None:
        response = MagicMock()
        mock_post.return_value = response
        with patch.object(
            services._client,
            "json_or_none",
            return_value=[{"codigo": 3034092}],
        ) as mock_json_or_none:
            result = services.listar_turmas([3034092])

        mock_post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[3034092],
        )
        response.raise_for_status.assert_called_once_with()
        mock_json_or_none.assert_called_once_with(response)
        self.assertEqual(result, [{"codigo": 3034092}])

    @patch.object(services._client, "post")
    def test_retorna_lista_vazia_sem_payload(
        self,
        mock_post: MagicMock,
    ) -> None:
        response = MagicMock()
        mock_post.return_value = response
        with patch.object(
            services._client,
            "json_or_none",
            return_value=None,
        ):
            result = services.listar_turmas([])

        self.assertEqual(result, [])


class AgrupamentosTerritorioServiceTest(SimpleTestCase):
    """Valida chamadas de agrupamentos para o sidecar pedagógico."""

    @patch.object(services._client, "get")
    def test_get_correlacionados_usa_path_com_barra_final(
        self,
        mock_get: MagicMock,
    ) -> None:
        response = MagicMock()
        response.json.return_value = []
        mock_get.return_value = response

        result = services.get_agrupamentos_correlacionados(815274, None)

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            f"{_BASE}/815274/territorio-saber/agrupamentos-correlacionados/",
            params={},
        )

    @patch.object(services._client, "post")
    def test_post_correlacionados_usa_path_com_barra_final(
        self,
        mock_post: MagicMock,
    ) -> None:
        response = MagicMock()
        response.json.return_value = []
        mock_post.return_value = response

        result = services.post_agrupamentos_correlacionados([815274], None)

        self.assertEqual(result, [])
        mock_post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
            payload=[815274],
            params={},
        )

    @patch.object(services._client, "post")
    def test_post_agrupamentos_usa_path_com_barra_final(
        self,
        mock_post: MagicMock,
    ) -> None:
        response = MagicMock()
        response.json.return_value = []
        mock_post.return_value = response

        result = services.post_agrupamentos_territorio([815274])

        self.assertEqual(result, [])
        mock_post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos/",
            payload=[815274],
        )


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


class GetTurmasRecorteFundMedioEjaTest(SimpleTestCase):
    """Valida a consulta de turmas no recorte de etapa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [_TURMA_MS]

        result = services.get_turmas_recorte_fund_medio_eja([3034092, 3014194])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/recorte-fund-medio-eja/",
            payload=[3034092, 3014194],
        )
        self.assertEqual(result, [_TURMA_MS])

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        """ Valida que a lista vazia não chama o sidecar e retorna lista vazia."""
        result = services.get_turmas_recorte_fund_medio_eja([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_quando_ms_responde_sem_corpo(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Valida que a lista vazia é retornada quando o sidecar responde sem corpo."""
        mock_client.json_or_none.return_value = None

        result = services.get_turmas_recorte_fund_medio_eja([3034092])

        self.assertEqual(result, [])


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


class GetTurmasHistoricasGeraisProfessorTest(SimpleTestCase):
    """Valida a composição de turmas históricas gerais do professor."""

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_compoe_codigos_professores_com_atributos_pedagogico(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Usa códigos de professores e enriquece com o listar-turmas."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [
            2822488,
            2822517,
            3016391,
        ]
        elegivel = {
            "ano": "7",
            "ano_letivo": 2025,
            "codigo": 2822488,
            "modalidade": "Infantil",
            "codigo_modalidade": 1,
            "nome_turma": "7E",
            "semestre": 0,
            "codigo_etapa_ensino": 1,
            "tipo_escola": 2,
        }
        inelegivel = {
            "ano": "0",
            "ano_letivo": 2025,
            "codigo": 3016391,
            "modalidade": None,
            "codigo_modalidade": 1,
            "nome_turma": "CB",
            "semestre": 0,
            "codigo_etapa_ensino": None,
            "tipo_escola": 2,
        }
        codigo_extra = {
            **elegivel,
            "codigo": 9999999,
            "nome_turma": "EXTRA",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = [
            elegivel,
            inelegivel,
            codigo_extra,
        ]
        mock_post.return_value = mock_response

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="7483147",
        )

        obter_codigos.assert_called_once_with(2025, "7483147")
        mock_post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[2822488, 2822517, 3016391],
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [elegivel])

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_aceita_turma_sem_tipo_escola(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Aceita tipo de escola ausente quando a etapa é elegível."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [2822488]
        turma = {
            "codigo": 2822488,
            "codigo_etapa_ensino": 1,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = [turma]
        mock_post.return_value = mock_response

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="7483147",
        )

        self.assertEqual(result, [turma])

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_descarta_tipo_escola_inelegivel(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Descarta turma de tipo de escola fora do contrato legado."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [2822488]
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "codigo": 2822488,
                "codigo_etapa_ensino": 1,
                "tipo_escola": 99,
            }
        ]
        mock_post.return_value = mock_response

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="7483147",
        )

        self.assertEqual(result, [])

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_sem_codigos_nao_chama_pedagogico(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Retorna lista vazia sem consultar o pedagógico."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = []

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="8381399",
        )

        self.assertEqual(result, [])
        mock_post.assert_not_called()

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_rejeita_raiz_que_nao_seja_lista(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Erra quando o listar-turmas não devolve uma lista de objetos."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [2822488]
        mock_response = MagicMock()
        mock_response.json.return_value = {"codigo": 2822488}
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve ser uma lista de objetos.",
        ):
            services.get_turmas_historicas_gerais_professor(
                ano_letivo=2025,
                professor_rf="7483147",
            )

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_rejeita_item_que_nao_seja_objeto(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Erra quando o listar-turmas devolve item não objeto."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [2822488]
        mock_response = MagicMock()
        mock_response.json.return_value = [2822488]
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve ser uma lista de objetos.",
        ):
            services.get_turmas_historicas_gerais_professor(
                ano_letivo=2025,
                professor_rf="7483147",
            )


class GetSincronizacaoInstitucionalTurmaTest(SimpleTestCase):
    """Valida a consulta de sincronização institucional da turma."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = {"codigo": 3010807, "ue_codigo": "091120"}
        mock_response = MagicMock()
        mock_response.content = b'{"codigo": 3010807}'
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_sincronizacao_institucional_turma(
            codigo_ue="091120",
            codigo_turma="3010807",
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ues/091120/turmas/3010807/"
            "sincronizacoes-institucionais/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_rejeita_resposta_que_nao_seja_objeto(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.content = b"[]"
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta institucional da turma deve ser um objeto.",
        ):
            services.get_sincronizacao_institucional_turma(
                codigo_ue="091120",
                codigo_turma="3010807",
            )


class GetSincronizacoesInstitucionaisAnosLetivosTest(SimpleTestCase):
    """Valida a consulta de turmas institucionais por anos letivos."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico_com_anos(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [3036295, 3082921, 3036225]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_sincronizacoes_institucionais_anos_letivos(
            codigo_ue="019437",
            anos_letivos_vigente=[2025, 2026],
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/",
            params={"anos_letivos_vigente": [2025, 2026]},
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_omite_filtro_quando_anos_nao_informados(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = services.get_sincronizacoes_institucionais_anos_letivos(
            codigo_ue="019437",
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ue/019437/"
            "sincronizacoes-institucionais/anos-letivos/",
            params=None,
        )
        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_rejeita_resposta_que_nao_seja_lista(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"codigo": 3036295}
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de anos letivos deve ser uma lista de inteiros.",
        ):
            services.get_sincronizacoes_institucionais_anos_letivos(
                codigo_ue="019437",
            )

    @patch.object(services._client, "get")
    def test_rejeita_item_que_nao_seja_inteiro(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [3036295, "3082921"]
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de anos letivos deve ser uma lista de inteiros.",
        ):
            services.get_sincronizacoes_institucionais_anos_letivos(
                codigo_ue="019437",
            )


class GetItinerariosEnsinoMedioTest(SimpleTestCase):
    """Valida a consulta de itinerários do ensino médio."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [
            {
                "id": 9,
                "nome": "Investigação cientifica",
                "serie": "2",
            }
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_itinerarios_ensino_medio()

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/itinerario/ensino-medio/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = services.get_itinerarios_ensino_medio()

        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_rejeita_raiz_que_nao_seja_lista(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 9}
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de itinerários deve ser uma lista de objetos.",
        ):
            services.get_itinerarios_ensino_medio()

    @patch.object(services._client, "get")
    def test_rejeita_item_que_nao_seja_objeto(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 9}, "inválido"]
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de itinerários deve ser uma lista de objetos.",
        ):
            services.get_itinerarios_ensino_medio()


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
