"""Valida os serviços do domínio pedagógico."""

from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase

from apps.alunos import services as alunos_services
from apps.pedagogico import services

_BASE = "/api/v1/pedagogico/componentes-curriculares"
_BASE_TURMAS = "/api/v1/pedagogico/turmas"
_TURMA_MS = {
    "codigo": 9100001,
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
    "ue_codigo": "000001",
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
            return_value=[{"codigo": 9100001}],
        ) as mock_json_or_none:
            result = services.listar_turmas([9100001])

        mock_post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[9100001],
        )
        response.raise_for_status.assert_called_once_with()
        mock_json_or_none.assert_called_once_with(response)
        self.assertEqual(result, [{"codigo": 9100001}])

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

        result = services.get_agrupamentos_correlacionados(9100016, None)

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            f"{_BASE}/9100016/territorio-saber/agrupamentos-correlacionados/",
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

        result = services.post_agrupamentos_correlacionados([9100016], None)

        self.assertEqual(result, [])
        mock_post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
            payload=[9100016],
            params={},
        )

    @patch.object(services._client, "get")
    def test_get_correlacionados_converte_data_base_tick(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Converte os ticks recebidos em ``data_base`` ISO no filtro."""
        response = MagicMock()
        response.json.return_value = []
        mock_get.return_value = response

        services.get_agrupamentos_correlacionados(
            9100016,
            638527968000000000,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/9100016/territorio-saber/agrupamentos-correlacionados/",
            params={"data_base": "2024-06-01"},
        )

    @patch.object(services._client, "post")
    def test_post_correlacionados_converte_data_base_tick(
        self,
        mock_post: MagicMock,
    ) -> None:
        """Converte os ticks recebidos em ``data_base`` ISO no filtro."""
        response = MagicMock()
        response.json.return_value = []
        mock_post.return_value = response

        services.post_agrupamentos_correlacionados(
            [9100016],
            638527968000000000,
        )

        mock_post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
            payload=[9100016],
            params={"data_base": "2024-06-01"},
        )

    @patch.object(services._client, "post")
    def test_post_agrupamentos_usa_path_com_barra_final(
        self,
        mock_post: MagicMock,
    ) -> None:
        response = MagicMock()
        response.json.return_value = []
        mock_post.return_value = response

        result = services.post_agrupamentos_territorio([9100016])

        self.assertEqual(result, [])
        mock_post.assert_called_once_with(
            f"{_BASE}/territorio-saber/agrupamentos/",
            payload=[9100016],
        )


class PostTurmasRegularesTest(SimpleTestCase):
    """Valida a consulta de turmas regulares."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [
            {"codigo": 9100002, "nome_turma": "1D"},
            {"codigo": 9100003, "nome_turma": "1B"},
        ]

        result = services.post_turmas_regulares(["9100003", "9100002"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-regulares/",
            payload=[9100003, 9100002],
        )
        self.assertEqual(result, ["9100002", "9100003"])

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        result = services.post_turmas_regulares([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])


class PostCodigosTurmasContagemTest(SimpleTestCase):
    """Valida a consulta de códigos de turmas para contagem de alunos."""

    @patch("apps.pedagogico.services._client")
    def test_monta_path_e_query(self, mock_client: MagicMock) -> None:
        """Envia as UEs no corpo e os filtros na query string."""
        mock_client.json_or_none.return_value = [9100021, 9100022]

        result = services.post_codigos_turmas_contagem(
            ["000004", "000005"],
            ano_turma="1",
            codigo_modalidade=5,
            ano_letivo=2026,
        )

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/codigos-turmas-contagem/",
            payload=["000004", "000005"],
            params={
                "ano_turma": "1",
                "codigo_modalidade": 5,
                "ano_letivo": 2026,
            },
        )
        self.assertEqual(result, [9100021, 9100022])

    @patch("apps.pedagogico.services._client")
    def test_sem_ues_nao_chama_sidecar(self, mock_client: MagicMock) -> None:
        """Valida que a lista vazia de UEs não chama o sidecar."""
        result = services.post_codigos_turmas_contagem([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])


class PostTurmasProgramaTest(SimpleTestCase):
    """Valida a consulta de turmas programa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [
            {"codigo": 9100004, "nome_turma": "1A"},
            {"codigo": 9100005, "nome_turma": "1A"},
        ]

        result = services.post_turmas_programa(["9100004", "9100005"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-programa/",
            payload=[9100004, 9100005],
        )
        self.assertEqual(result, ["9100004", "9100005"])

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

        result = services.post_turmas_programa(["9100004"])

        mock_client.json_or_none.assert_called_once_with(
            mock_client.post.return_value
        )
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_aceita_payload_ms_com_lista_de_strings(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = ["9100004", "9100005"]

        result = services.post_turmas_programa(["9100004", "9100005"])

        self.assertEqual(result, ["9100004", "9100005"])

    @patch("apps.pedagogico.services._client")
    def test_aceita_payload_ms_com_lista_de_inteiros(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = [9100004, 9100005]

        result = services.post_turmas_programa(["9100004", "9100005"])

        self.assertEqual(result, ["9100004", "9100005"])


class GetTurmasRecorteFundMedioEjaTest(SimpleTestCase):
    """Valida a consulta de turmas no recorte de etapa."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path e envia os codigos como inteiros."""
        mock_client.json_or_none.return_value = [_TURMA_MS]

        result = services.get_turmas_recorte_fund_medio_eja([9100001, 9100002])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/recorte-fund-medio-eja/",
            payload=[9100001, 9100002],
        )
        self.assertEqual(result, [_TURMA_MS])

    @patch("apps.pedagogico.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Valida que a lista vazia não chama o sidecar."""
        result = services.get_turmas_recorte_fund_medio_eja([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_quando_ms_responde_sem_corpo(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Retorna lista vazia quando o sidecar responde sem corpo."""
        mock_client.json_or_none.return_value = None

        result = services.get_turmas_recorte_fund_medio_eja([9100001])

        self.assertEqual(result, [])


class PostListarTurmasTest(SimpleTestCase):
    """Valida a listagem de dados de turmas."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        mock_client.post.return_value.json.return_value = [_TURMA_MS]

        result = services.post_listar_turmas(["9100001"])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[9100001],
        )
        self.assertEqual(result[0]["codigo"], 9100001)
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

        result = services.get_dados_turma("9100001")

        mock_client.get.assert_called_once_with(
            f"{_BASE_TURMAS}/9100001/dados/"
        )
        self.assertEqual(result["codigo"], 9100001)
        self.assertEqual(result["tipoTurma"], 1)
        self.assertEqual(result["ueCodigo"], "000001")
        self.assertEqual(result["modalidade"], None)
        self.assertEqual(result["codigoModalidade"], 0)
        self.assertEqual(result["serieEnsino"], None)
        self.assertEqual(result["situacao"], None)
        self.assertEqual(result["ehistorico"], False)
        self.assertEqual(result["etapaEJA"], 0)


class GetAlunosAtivosTurmaSemRedisTest(SimpleTestCase):
    """Valida a consulta de alunos ativos sem Redis."""

    @patch.object(alunos_services._client, "get")
    def test_chama_path_canonico_com_params_fixos(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [{"codigo_aluno": 7000001}]
        response = MagicMock()
        response.content = b"[]"
        response.json.return_value = payload
        mock_get.return_value = response

        with patch.object(
            alunos_services._client,
            "json_or_none",
            return_value=payload,
        ) as mock_json_or_none:
            result = services.get_alunos_ativos_turma_sem_redis("9100009")

        mock_get.assert_called_once_with(
            "/api/v1/alunos/turmas/9100009/",
            params={
                "considerar_inativos": False,
                "sequencia": 1,
            },
        )
        response.raise_for_status.assert_called_once_with()
        mock_json_or_none.assert_called_once_with(response)
        self.assertEqual(result, payload)

    @patch.object(alunos_services._client, "get")
    def test_retorna_lista_vazia_quando_sem_corpo(
        self,
        mock_get: MagicMock,
    ) -> None:
        response = MagicMock()
        mock_get.return_value = response

        with patch.object(
            alunos_services._client,
            "json_or_none",
            return_value=None,
        ):
            result = services.get_alunos_ativos_turma_sem_redis("9100009")

        response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [])


class GetAlunosAtivosTurmaRedisMultplexTest(SimpleTestCase):
    """Valida a consulta de alunos ativos por Redis Multplex."""

    @patch.object(alunos_services._client, "get")
    def test_chama_path_canonico_sem_params(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [{"codigo_aluno": 7000001}]
        response = MagicMock()
        mock_get.return_value = response

        with patch.object(
            alunos_services._client,
            "json_or_none",
            return_value=payload,
        ) as mock_json_or_none:
            result = services.get_alunos_ativos_turma_redis_multplex(
                "9100015",
            )

        mock_get.assert_called_once_with(
            "/api/v1/alunos/turmas/9100015/",
            params={"considerar_inativos": True},
        )
        response.raise_for_status.assert_called_once_with()
        mock_json_or_none.assert_called_once_with(response)
        self.assertEqual(result, payload)

    @patch.object(alunos_services._client, "get")
    def test_retorna_lista_vazia_quando_sem_corpo(
        self,
        mock_get: MagicMock,
    ) -> None:
        response = MagicMock()
        mock_get.return_value = response

        with patch.object(
            alunos_services._client,
            "json_or_none",
            return_value=None,
        ):
            result = services.get_alunos_ativos_turma_redis_multplex(
                "9100015",
            )

        response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [])


class GetAlunosTurmaConsideraInativosTest(SimpleTestCase):
    """Valida a consulta de alunos considerando ativos ou inativos."""

    @patch.object(alunos_services, "get_alunos_por_turma")
    def test_encaminha_filtro_e_primeira_sequencia(
        self,
        mock_get_alunos: MagicMock,
    ) -> None:
        """Repassa ``considerar_inativos`` e fixa a sequência em 1."""
        payload = [{"codigo_aluno": 7000001}]
        mock_get_alunos.return_value = payload

        result = services.get_alunos_turma_considera_inativos(
            "9100015",
            considera_inativos=True,
        )

        mock_get_alunos.assert_called_once_with(
            "9100015",
            considerar_inativos=True,
            sequencia=1,
        )
        self.assertEqual(result, payload)

    @patch.object(alunos_services, "get_alunos_por_turma")
    def test_normaliza_considera_inativos_nulo_para_falso(
        self,
        mock_get_alunos: MagicMock,
    ) -> None:
        """Converte ``None`` em ``False`` antes de encaminhar ao sidecar."""
        mock_get_alunos.return_value = []

        services.get_alunos_turma_considera_inativos(
            "9100015",
            considera_inativos=None,
        )

        mock_get_alunos.assert_called_once_with(
            "9100015",
            considerar_inativos=False,
            sequencia=1,
        )


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
            9100006,
            9100007,
            9100008,
        ]
        elegivel = {
            "ano": "7",
            "ano_letivo": 2025,
            "codigo": 9100006,
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
            "codigo": 9100008,
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
            professor_rf="7900001",
        )

        obter_codigos.assert_called_once_with(2025, "7900001")
        mock_post.assert_called_once_with(
            f"{_BASE_TURMAS}/listar-turmas/",
            payload=[9100006, 9100007, 9100008],
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
        obter_codigos.return_value = [9100006]
        turma = {
            "codigo": 9100006,
            "codigo_etapa_ensino": 1,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = [turma]
        mock_post.return_value = mock_response

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="7900001",
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
        obter_codigos.return_value = [9100006]
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "codigo": 9100006,
                "codigo_etapa_ensino": 1,
                "tipo_escola": 99,
            }
        ]
        mock_post.return_value = mock_response

        result = services.get_turmas_historicas_gerais_professor(
            ano_letivo=2025,
            professor_rf="7900001",
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
            professor_rf="7900002",
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
        obter_codigos.return_value = [9100006]
        mock_response = MagicMock()
        mock_response.json.return_value = {"codigo": 9100006}
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve ser uma lista de objetos.",
        ):
            services.get_turmas_historicas_gerais_professor(
                ano_letivo=2025,
                professor_rf="7900001",
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
        obter_codigos.return_value = [9100006]
        mock_response = MagicMock()
        mock_response.json.return_value = [9100006]
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve ser uma lista de objetos.",
        ):
            services.get_turmas_historicas_gerais_professor(
                ano_letivo=2025,
                professor_rf="7900001",
            )

    @patch.object(services, "professores_services")
    @patch.object(services._client, "post")
    def test_rejeita_codigo_que_nao_seja_inteiro(
        self,
        mock_post: MagicMock,
        mock_professores: MagicMock,
    ) -> None:
        """Erra quando uma turma não traz código inteiro."""
        obter_codigos = (
            mock_professores.get_codigos_turmas_historicas_professor
        )
        obter_codigos.return_value = [9100006]
        mock_response = MagicMock()
        mock_response.json.return_value = [{"codigo": "9100006"}]
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve conter código inteiro.",
        ):
            services.get_turmas_historicas_gerais_professor(
                ano_letivo=2025,
                professor_rf="7900001",
            )


class GetSincronizacaoInstitucionalTurmaTest(SimpleTestCase):
    """Valida a consulta de sincronização institucional da turma."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = {"codigo": 9100009, "ue_codigo": "000002"}
        mock_response = MagicMock()
        mock_response.content = b'{"codigo": 9100009}'
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_sincronizacao_institucional_turma(
            codigo_ue="000002",
            codigo_turma="9100009",
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ues/000002/turmas/9100009/"
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
                codigo_ue="000002",
                codigo_turma="9100009",
            )


class GetSincronizacoesInstitucionaisAnosLetivosTest(SimpleTestCase):
    """Valida a consulta de turmas institucionais por anos letivos."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico_com_anos(
        self,
        mock_get: MagicMock,
    ) -> None:
        payload = [9100010, 9100011, 9100012]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_sincronizacoes_institucionais_anos_letivos(
            codigo_ue="000003",
            anos_letivos_vigente=[2025, 2026],
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ue/000003/"
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
            codigo_ue="000003",
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/ue/000003/"
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
        mock_response.json.return_value = {"codigo": 9100010}
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de anos letivos deve ser uma lista de inteiros.",
        ):
            services.get_sincronizacoes_institucionais_anos_letivos(
                codigo_ue="000003",
            )

    @patch.object(services._client, "get")
    def test_rejeita_item_que_nao_seja_inteiro(
        self,
        mock_get: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [9100010, "9100011"]
        mock_get.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de anos letivos deve ser uma lista de inteiros.",
        ):
            services.get_sincronizacoes_institucionais_anos_letivos(
                codigo_ue="000003",
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


class GetModalidadesEnsinoTest(SimpleTestCase):
    """Valida a consulta do catálogo de modalidades de ensino."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(self, mock_get: MagicMock) -> None:
        payload = ["Infantil", "Fundamental"]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_modalidades_ensino()

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/escolas/modalidades-ensino/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_rejeita_raiz_que_nao_seja_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"a": 1}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            services.get_modalidades_ensino()

    @patch.object(services._client, "get")
    def test_rejeita_item_que_nao_seja_texto(
        self, mock_get: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = ["Infantil", 5]
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            services.get_modalidades_ensino()


class GetTurmasPorTipoSalaTest(SimpleTestCase):
    """Valida a consulta de turmas por UE/tipo de sala/ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_turma": 9100018}]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_turmas_por_tipo_sala(
            codigo_ue="000532", tipo_sala="1", ano_letivo="2024"
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/escolas/000532/salas/1/anos-letivos/2024/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_rejeita_raiz_que_nao_seja_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"a": 1}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            services.get_turmas_por_tipo_sala(
                codigo_ue="000532", tipo_sala="1", ano_letivo="2024"
            )


class GetTurmasPorEscolaTest(SimpleTestCase):
    """Valida a consulta de turmas por UE/ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_turma": 9100018}]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_turmas_por_escola(
            codigo_ue="000532", ano_letivo="2024"
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/escolas/000532/anos-letivos/2024/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_rejeita_raiz_que_nao_seja_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"a": 1}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            services.get_turmas_por_escola(
                codigo_ue="000532", ano_letivo="2024"
            )


class GetTurmasSondagemTest(SimpleTestCase):
    """Valida a consulta de turmas de Sondagem por UE/ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_turma": 9100018}]
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_get.return_value = mock_response

        result = services.get_turmas_sondagem(
            codigo_ue="000532", ano_letivo="2024"
        )

        mock_get.assert_called_once_with(
            f"{_BASE_TURMAS}/escolas/000532/turmas-sondagem/"
            "anos-letivos/2024/"
        )
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_rejeita_raiz_que_nao_seja_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"a": 1}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            services.get_turmas_sondagem(codigo_ue="000532", ano_letivo="2024")


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
                "incluirExtintas": False,
            },
        )
        self.assertEqual(result, [])

    @patch("apps.pedagogico.services._client")
    def test_incluir_extintas_repassa_flag(
        self, mock_client: MagicMock
    ) -> None:
        """Repassa incluirExtintas=True para o serviço pedagógico."""
        mock_client.get.return_value.json.return_value = []

        services.get_componentes_por_lista_turmas(
            ["T001"],
            adicionar_componentes_planejamento=False,
            incluir_extintas=True,
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas",
            params={
                "codigoTurmas": ["T001"],
                "adicionarComponentesPlanejamento": False,
                "incluirExtintas": True,
            },
        )


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
    def test_retorna_payload_bruto(
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
                    "componente_codigo": "138",
                    "componente_descricao": "LINGUA PORTUGUESA",
                    "turma_codigo": "T001",
                    "data_inicio_turma": "2024-02-05T03:00:00Z",
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


class GetTurmaComponentesTurmaTest(SimpleTestCase):
    """Valida a consulta dos componentes curriculares de uma turma."""

    @patch("apps.pedagogico.services._client")
    def test_monta_path_query_e_retorna_lista(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Repassa turma e componentes e preserva o payload recebido."""
        response = MagicMock()
        payload = [
            {
                "componente_codigo": "89",
                "desc_experiencia_pedagogica": "HORTA PEDAGOGICA",
            }
        ]
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = payload

        resultado = services.get_turma_componentes_turma(
            "9100013",
            ["89", "90"],
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/9100013/componentes-turma/",
            params={"codigos_componentes": ["89", "90"]},
        )
        mock_client.json_or_none.assert_called_once_with(response)
        self.assertEqual(resultado, payload)

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_para_payload_invalido(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Normaliza payload vazio ou incompatível para lista vazia."""
        mock_client.json_or_none.return_value = {"detail": "erro"}

        resultado = services.get_turma_componentes_turma(
            "9100013",
            ["89"],
        )

        self.assertEqual(resultado, [])


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

        mock_client.get.assert_called_once_with(f"{_BASE}/")
        mock_client.get.return_value.raise_for_status.assert_called_once_with()

        self.assertEqual(result, [])


class GetTodasTurmasAtribuidasDreUeTest(SimpleTestCase):
    """Valida a abrangência SME de turmas atribuídas."""

    @patch("apps.pedagogico.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        payload: dict[str, object] = {"abrangencia": None, "dres": []}
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = payload

        result = services.get_todas_turmas_atribuidas_dre_ue()

        mock_client.get.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-atribuidas-dre-ue/todas/"
        )
        response.raise_for_status.assert_called_once_with()
        mock_client.json_or_none.assert_called_once_with(response)
        self.assertEqual(result, payload)


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


class ListagemTurmasComponentesServiceTest(SimpleTestCase):
    """Valida a tradução do serviço de listagem turma×componente."""

    def _path(self) -> str:
        """Retorna o path canônico esperado no sidecar."""
        return f"{_BASE}/ues/9000/modalidades/5/anos/2024/componentes/"

    @patch.object(services._client, "get")
    def test_professor_monta_path_e_params(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Envia RF, ticks convertidos e demais filtros em snake_case."""
        response = MagicMock()
        response.json.return_value = {
            "items": [],
            "total_registros": 0,
            "total_paginas": 0,
        }
        mock_get.return_value = response

        services.get_listagem_turmas_componentes(
            "9000",
            5,
            2024,
            codigo_turma=77,
            qtde_registros=10,
            qtde_registros_ignorados=0,
            eh_professor=True,
            codigo_rf="RF1",
            considera_historico=True,
            periodo_escolar_inicio_tick=638527968000000000,
            anos_infantil_desconsiderar=["1"],
        )

        mock_get.assert_called_once_with(
            self._path(),
            params={
                "eh_professor": "true",
                "considera_historico": "true",
                "codigo_turma": 77,
                "qtde_registros": 10,
                "qtde_registros_ignorados": 0,
                "codigo_rf": "RF1",
                "periodo_escolar_inicio": "2024-06-01",
                "anos_infantil_desconsiderar": ["1"],
            },
        )

    @patch.object(services._client, "get")
    def test_gestor_nao_envia_rf(
        self,
        mock_get: MagicMock,
    ) -> None:
        """No modo gestor, o RF não é enviado ao sidecar."""
        response = MagicMock()
        response.json.return_value = {
            "items": [],
            "total_registros": 0,
            "total_paginas": 0,
        }
        mock_get.return_value = response

        services.get_listagem_turmas_componentes(
            "9000", 5, 2024, eh_professor=False, codigo_rf="RF1"
        )

        _, kwargs = mock_get.call_args
        self.assertNotIn("codigo_rf", kwargs["params"])
        self.assertEqual(kwargs["params"]["eh_professor"], "false")

    @patch.object(services._client, "get")
    def test_retorna_envelope(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Retorna o envelope paginado devolvido pelo sidecar."""
        envelope = {
            "items": [{"turma_codigo": "T1"}],
            "total_registros": 1,
            "total_paginas": 1,
        }
        response = MagicMock()
        response.json.return_value = envelope
        mock_get.return_value = response

        resultado = services.get_listagem_turmas_componentes("9000", 5, 2024)

        self.assertEqual(resultado, envelope)

    @patch.object(services._client, "get")
    def test_payload_nao_objeto_gera_valueerror(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Rejeita payload que não seja um objeto."""
        response = MagicMock()
        response.json.return_value = []
        mock_get.return_value = response

        with self.assertRaises(ValueError):
            services.get_listagem_turmas_componentes("9000", 5, 2024)


class VerificarAtribuicaoTerritorioSaberTest(SimpleTestCase):
    """Valida a atribuição do professor em território do saber."""

    @patch("apps.pedagogico.services._client")
    def test_chama_sidecar_e_retorna_booleano(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Monta o path com os dados da atribuição."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = True

        result = services.verificar_atriuicao_territorio_saber(
            "000001",
            "9100013",
            "89",
            "2026-07-28",
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/89/turmas/9100013/professor/000001/"
            "data/2026-07-28/atribuicao/validar/"
        )
        mock_client.json_or_none.assert_called_once_with(response)
        self.assertIs(result, True)


class GetAtribuicoesTerritorioSaberTest(SimpleTestCase):
    """Valida a consulta de atribuições de Território do Saber."""

    @patch("apps.pedagogico.services._client")
    def test_serializa_lista_retornada_pelo_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Preserva o contrato interno e aceita campos opcionais nulos."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9100013",
                "ano_letivo": None,
                "nome_turma": "7A",
                "data_inicio_atribuicao": None,
                "data_fim_atribuicao": None,
                "data_fim_turma": None,
                "ano_atribuicao": None,
                "codigo_rf": "000001",
                "disciplina_id": "800000",
                "disciplina_nome": None,
                "disciplinas_agrupadas_ids": None,
                "nome_professor": None,
            }
        ]

        result = services.get_atribuicoes_territorio_saber("000001", 2026)

        mock_client.get.assert_called_once_with(
            f"{_BASE}/professores/000001/anos-letivos/2026/"
            "atribuicoes-territorio-saber/"
        )
        mock_client.json_or_none.assert_called_once_with(response)
        self.assertEqual(result[0]["codigo_turma"], "9100013")
        self.assertIsNone(result[0]["disciplinas_agrupadas_ids"])

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_para_payload_invalido(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Ignora respostas que não sejam listas de atribuições."""
        mock_client.json_or_none.return_value = {"detail": "Não encontrado"}

        result = services.get_atribuicoes_territorio_saber("000001", 2026)

        self.assertEqual(result, [])


class GetProfessoresTurmaTerritorioSaberTest(SimpleTestCase):
    """Valida professores de Território do Saber por turma."""

    @patch("apps.pedagogico.services._client")
    def test_usa_rota_de_atribuicoes_e_serializa_retorno(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Monta a rota de atribuições no recurso de componentes."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9100013",
                "disciplina_id": "800000",
                "disciplina_nome": "TERRITORIO DO SABER",
                "disciplinas_agrupadas_ids": [89, 90],
                "nome_professor": "PROFESSOR",
                "codigo_rf": "000001",
            }
        ]

        resultado = services.get_professores_turma_territorio_saber("9100013")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/9100013/atribuicoes-territorio-saber/"
        )
        self.assertEqual(resultado[0]["disciplina_id"], "800000")

    @patch("apps.pedagogico.services._client")
    def test_normaliza_cod_agrupamento_do_payload_atual(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Usa o código do agrupamento como identificador da disciplina."""
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9100014",
                "cod_agrupamento": 900001,
                "componentes_curriculares_agrupados": [1216, 1217],
                "descricao_territorio_saber": "III - ORIENTACAO",
                "descricao_experiencia_pedagogica": "OUTRAS",
                "rf_professor": "7900003",
            }
        ]

        resultado = services.get_professores_turma_territorio_saber("9100014")

        self.assertEqual(resultado[0]["disciplina_id"], "900001")
        self.assertEqual(
            resultado[0]["disciplinas_agrupadas_ids"], [1216, 1217]
        )
        self.assertEqual(
            resultado[0]["disciplina_nome"],
            "III - ORIENTACAO - OUTRAS",
        )
        self.assertEqual(resultado[0]["codigo_rf"], "7900003")


class GetProfessoresTurmasTerritorioSaberTest(SimpleTestCase):
    """Valida professores de Território do Saber por várias turmas."""

    @patch("apps.pedagogico.services._client")
    def test_envia_codigos_como_lista_na_query_string(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Envia cada código de turma como parâmetro de mesmo nome."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = []

        resultado = services.get_professores_turmas_territorio_saber(
            ["9100013", "9100020"]
        )

        mock_client.get.assert_called_once_with(
            f"{_BASE}/turmas/atribuicoes-territorio-saber/",
            params={"codigo_turma": [9100013, 9100020]},
        )
        mock_client.json_or_none.assert_called_once_with(response)
        self.assertEqual(resultado, [])


class GetAtribuicoesTerritorioSaberSemAnoTest(SimpleTestCase):
    """Valida a consulta geral de atribuições de Território do Saber."""

    @patch("apps.pedagogico.services._client")
    def test_consulta_sem_filtro_de_ano_letivo(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Usa a rota geral quando o ano letivo não é informado."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = []

        result = services.get_atribuicoes_territorio_saber("000001")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/professores/000001/atribuicoes-territorio-saber/"
        )
        self.assertEqual(result, [])


class GetComponentesApiEolTest(SimpleTestCase):
    """Valida a consulta de componentes curriculares da API EOL."""

    @patch("apps.pedagogico.services._client")
    def test_retorna_json_do_sidecar(self, mock_client: MagicMock) -> None:
        """Consulta a rota correta e retorna o JSON recebido."""
        response = MagicMock()
        response.json.return_value = [{"id_componente_curricular": 89}]
        mock_client.get.return_value = response

        resultado = services.get_componentes_api_eol()

        mock_client.get.assert_called_once_with(f"{_BASE}/api-eol/")
        self.assertEqual(resultado, [{"id_componente_curricular": 89}])


class GetProfessoresTurmaTerritorioSaberPayloadTest(SimpleTestCase):
    """Valida respostas inválidas da atribuição territorial por turma."""

    @patch("apps.pedagogico.services._client")
    def test_retorna_lista_vazia_para_payload_invalido(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Ignora payload que não seja uma lista."""
        mock_client.json_or_none.return_value = {"detail": "Inválido"}

        resultado = services.get_professores_turma_territorio_saber("9100013")

        self.assertEqual(resultado, [])
