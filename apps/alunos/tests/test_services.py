"""Valida os serviços do domínio de alunos."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.alunos import services

_BASE = "/api/v1/alunos"


class GetInformacoesAlunoTest(SimpleTestCase):
    """Valida a consulta de informações do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de informações do aluno."""
        payload = {"codigo_aluno": 123456, "nome_aluno": "Fulano de Tal"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = (
            b'{"codigo_aluno": 123456, "nome_aluno": "Fulano de Tal"}'
        )
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_informacoes_aluno("123456")

        mock_get.assert_called_once_with(f"{_BASE}/123456/informacoes")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        """Valida retorno None quando a consulta responde com status 204."""
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_informacoes_aluno("123456")

        mock_resp.raise_for_status.assert_called_once_with()
        self.assertIsNone(result)


class GetNecessidadesEspeciaisAlunoTest(SimpleTestCase):
    """Valida a consulta de necessidades especiais do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de necessidades especiais do aluno."""
        payload = [
            {
                "codigo_aluno": 123456,
                "tipo_necessidade_especial": 10,
                "descricao_necessidade_especial": "Deficiencia Visual",
            }
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_necessidades_especiais_aluno("123456")

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/necessidades-especiais"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class BuscarAlunosAtivosAutocompleteTest(SimpleTestCase):
    """Valida a consulta de autocomplete de alunos ativos."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_params_corretos(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"codigo_aluno": 123456, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.buscar_alunos_ativos_autocomplete(
            ue_codigo="100001",
            aluno_nome="Fulano",
            data_referencia=datetime(2026, 2, 3, 10, 0, 0),
            aluno_codigo=0,
            limite=5,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/autocomplete/ativos",
            params={
                "aluno_codigo": 0,
                "limite": 5,
                "aluno_nome": "Fulano",
                "data_referencia": "2026-02-03T10:00:00",
            },
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_omite_params_opcionais_vazios(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = services.buscar_alunos_ativos_autocomplete(
            ue_codigo="100001",
            aluno_nome=None,
            data_referencia=None,
            aluno_codigo=123456,
            limite=10,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/autocomplete/ativos",
            params={"aluno_codigo": 123456, "limite": 10},
        )
        self.assertEqual(result, [])


class GetResponsavelResumidoTest(SimpleTestCase):
    """Valida a consulta de dados resumidos do responsável."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"cpf": "12345678900", "codigo_aluno": "123456"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_responsavel_resumido("12345678900")

        mock_get.assert_called_once_with(
            f"{_BASE}/responsaveis/12345678900/resumido"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetFiliacaoAlunoTest(SimpleTestCase):
    """Valida a consulta de dados de filiação do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida o path montado para o sidecar."""
        payload = [{"nome_responsavel": "Maria da Silva"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_filiacao_aluno("123456")

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/responsaveis/filiacao"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetInformacoesAlunosTurmaTest(SimpleTestCase):
    """Valida a consulta de informações dos alunos da turma."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_aluno": 123456, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_informacoes_alunos_turma("9001")

        mock_get.assert_called_once_with(f"{_BASE}/9001/turma/informacoes")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_sem_corpo(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_informacoes_alunos_turma("9001")

        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [])


class GetAlunosPorTurmaTest(SimpleTestCase):
    """Valida a fonte única de consulta de alunos por turma."""

    @patch.object(services._client, "get")
    def test_omite_data_aula_ticks_quando_zero(
        self, mock_get: MagicMock
    ) -> None:
        """``data_aula_ticks`` igual a 0 não é enviado ao microsserviço."""
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.get_alunos_por_turma(
            "3012185",
            considerar_inativos=False,
            data_aula_ticks="0",
            sequencia=1,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3012185/",
            params={"considerar_inativos": False, "sequencia": 1},
        )

    @patch.object(services._client, "get")
    def test_envia_apenas_considerar_inativos_quando_minimo(
        self, mock_get: MagicMock
    ) -> None:
        """Sem ticks e sem sequência, envia apenas ``considerar_inativos``."""
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.get_alunos_por_turma("3012185", considerar_inativos=True)

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3012185/",
            params={"considerar_inativos": True},
        )

    @patch.object(services._client, "get")
    def test_envia_codigo_aluno_quando_informado(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.get_alunos_por_turma(
            "3123349",
            considerar_inativos=True,
            codigo_aluno="7345634",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3123349/",
            params={
                "considerar_inativos": True,
                "codigo_aluno": "7345634",
            },
        )

    @patch.object(services._client, "get")
    def test_envia_data_matricula_ticks_quando_informada(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.get_alunos_por_turma(
            "3015603",
            considerar_inativos=True,
            data_matricula_ticks="639059616000000000",
            sequencia=1,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3015603/",
            params={
                "considerar_inativos": True,
                "data_matricula_ticks": "639059616000000000",
                "sequencia": 1,
            },
        )


class GetAlunosAtivosDataAulaTicksTest(SimpleTestCase):
    """Valida a integração da consulta de alunos ativos."""

    @patch.object(services._client, "get")
    def test_chama_path_canonico(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_aluno": 123456}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_alunos_ativos_data_aula_ticks(
            codigo_turma="3012185",
            data_ticks="639031104000000000",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3012185/",
            params={
                "considerar_inativos": True,
                "data_aula_ticks": "639031104000000000",
            },
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_sem_corpo(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_alunos_ativos_data_aula_ticks(
            codigo_turma="3012185",
            data_ticks="639031104000000000",
        )

        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [])


class GetAlunosDataMatriculaTicksTest(SimpleTestCase):
    """Valida a consulta de alunos por data de matricula."""

    @patch.object(services._client, "get")
    def test_chama_endpoint_canonico_com_filtros(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"codigo_aluno": 7614272}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_alunos_data_matricula_ticks(
            codigo_turma="3015603",
            data_matricula_ticks="639059616000000000",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/3015603/",
            params={
                "considerar_inativos": True,
                "data_matricula_ticks": "639059616000000000",
                "sequencia": 1,
            },
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTurmasAlunoTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de turmas do aluno."""
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno("123456")

        mock_get.assert_called_once_with(f"{_BASE}/123456/turmas/")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetAlunosDaUeTest(SimpleTestCase):
    """Valida a consulta de alunos da UE por ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_e_filtros_corretos(self, mock_get: MagicMock) -> None:
        """Valida a chamada ao endpoint interno do sidecar."""
        payload = [{"codigo_aluno": 123456}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_alunos_da_ue(
            "019362",
            "2026",
            nome_aluno="Fulano",
            codigo_eol="123456",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/019362/anos_letivos/2026",
            params={"nome_aluno": "Fulano", "codigo_eol": "123456"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTurmasAlunoPorSituacaoTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno por situação/tipo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida o path montado para o sidecar (snake_case interno)."""
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_por_situacao(
            "123456", "2026", "true", "false"
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/turmas/anos_letivos/2026"
            "/matricula_turma/true/tipo_turma/false"
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTurmasAlunoComProgramaTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno incluindo programa."""

    @patch.object(services._client, "get")
    def test_chama_turmas_com_filtros_desativados(
        self, mock_get: MagicMock
    ) -> None:
        """Valida a consulta com filtros de tipo e situação desativados."""
        payload = [{"codigo_turma": 9001}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("123456")

        mock_get.assert_called_once_with(
            f"{_BASE}/123456/turmas/",
            params={"tipo_turma": "false", "filtrar_situacao": "false"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_codigo_invalido_retorna_lista_vazia(
        self, mock_get: MagicMock
    ) -> None:
        """Sidecar 400 (ex.: "00000") vira lista vazia, sem propagar erro."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("00000")

        self.assertEqual(result, [])
        mock_resp.raise_for_status.assert_not_called()

    @patch.object(services._client, "get")
    def test_aluno_sem_turmas_retorna_lista_vazia(
        self, mock_get: MagicMock
    ) -> None:
        """Sidecar 404 (aluno sem turmas) vira lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        result = services.get_turmas_aluno_com_programa("123456")

        self.assertEqual(result, [])
        mock_resp.raise_for_status.assert_not_called()


class GetAlunosAtivosTurmaTest(SimpleTestCase):
    """Valida a consulta de alunos ativos de uma turma."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida o path montado para o sidecar."""
        payload = [{"codigo_aluno": 123456}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_alunos_ativos_turma("9001")

        mock_get.assert_called_once_with(f"{_BASE}/turmas/9001/ativos")
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetAlunosAtivosTurmaPeriodoTest(SimpleTestCase):
    """Valida a consulta de alunos ativos por período da turma."""

    @patch.object(services._client, "get")
    def test_chama_path_e_parametro_corretos(
        self, mock_get: MagicMock
    ) -> None:
        """Valida o path e a data inicial enviados ao sidecar."""
        payload = [{"codigo_aluno": 123456}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_alunos_ativos_turma_periodo(
            "9001", "2026-12-31", "2026-01-01"
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/turmas/9001/ativos/2026-12-31",
            params={"data_referencia_inicio": "2026-01-01"},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetTotalAlunosAtivosPeriodoTest(SimpleTestCase):
    """Valida a consulta do total de alunos ativos por período."""

    @patch.object(services._client, "get")
    def test_chama_path_e_filtros_corretos(self, mock_get: MagicMock) -> None:
        """Valida o encaminhamento de filtros ao sidecar."""
        payload = {"quantidade": 42}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"quantidade": 42}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_total_alunos_ativos_periodo(
            ano_turma="5",
            ano_letivo="2026",
            data_inicio="2026-01-01",
            data_fim="2026-12-31",
            ue_id="100001",
            dre_id="108800",
            modalidades=["5", "6"],
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ativos/anos/5/anos-letivos/2026"
            "/inicio/2026-01-01/fim/2026-12-31",
            params={
                "ue_id": "100001",
                "dre_id": "108800",
                "modalidades": ["5", "6"],
            },
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_omite_filtros_opcionais_vazios(self, mock_get: MagicMock) -> None:
        """Valida a omissão de filtros opcionais não informados."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"quantidade": 0}'
        mock_resp.json.return_value = {"quantidade": 0}
        mock_get.return_value = mock_resp

        services.get_total_alunos_ativos_periodo(
            "5", "2026", "2026-01-01", "2026-12-31"
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ativos/anos/5/anos-letivos/2026"
            "/inicio/2026-01-01/fim/2026-12-31",
            params=None,
        )


class ListarAlunosTest(SimpleTestCase):
    """Valida a consulta de listagem de alunos."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida a consulta de listagem de alunos."""
        payload = [{"codigo_aluno": 1, "nome_aluno": "Fulano"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.listar_alunos(["1", "2"])

        mock_get.assert_called_once_with(
            f"{_BASE}/alunos",
            params={"codigos_aluno": ["1", "2"]},
        )
        mock_resp.raise_for_status.assert_called_once_with()
        self.assertEqual(result, payload)


class GetCodigosTurmasRegularesAlunoTest(SimpleTestCase):
    """Valida a chamada ao Alunos-MS de códigos de turma do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_e_repassa_data_referencia(
        self, mock_get: MagicMock
    ) -> None:
        """Valida a chamada ao endpoint de códigos de turmas regulares do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[23456, 12345]"
        mock_resp.json.return_value = [23456, 12345]
        mock_get.return_value = mock_resp

        result = services.get_codigos_turmas_regulares_aluno(
            "2026", "7345634", data_referencia="2026-06-01"
        )

        self.assertEqual(result, [23456, 12345])
        mock_get.assert_called_once_with(
            f"{_BASE}/anos-letivos/2026/alunos/7345634"
            "/codigos-turmas-regulares",
            params={"data_referencia": "2026-06-01"},
        )

    @patch.object(services._client, "get")
    def test_4xx_do_sidecar_retorna_lista_vazia(
        self, mock_get: MagicMock
    ) -> None:
        """Valida que o sidecar 4xx (ex.: aluno inexistente) vira lista vazia, sem propagar erro."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        self.assertEqual(
            services.get_codigos_turmas_regulares_aluno("2026", "00000"),
            [],
        )


class MontarCodigosTurmasRegularesAlunoTest(SimpleTestCase):
    """Valida a orquestração cross-domain dos endpoints 3/4."""

    @patch("apps.pedagogico.services.get_turmas_recorte_por_tipo")
    @patch("apps.alunos.services.get_codigos_turmas_regulares_aluno")
    def test_intersecta_preservando_ordem_do_alunos(
        self, mock_alunos: MagicMock, mock_recorte: MagicMock
    ) -> None:
        """Valida a intersecção de códigos de turmas regulares do aluno com o recorte de tipos de turma, preservando a ordem do retorno do Alunos-MS."""
        mock_alunos.return_value = [23456, 12345, 99999]
        mock_recorte.return_value = [12345, 23456]

        result = services.montar_codigos_turmas_regulares_aluno(
            ano_letivo="2026",
            codigo_aluno="7345634",
            tipos_turma=[1],
            ue_codigo="019370",
            semestre=1,
        )

        self.assertEqual(result, [23456, 12345])
        mock_alunos.assert_called_once_with("2026", "7345634", None)
        mock_recorte.assert_called_once_with(
            [23456, 12345, 99999], [1], "019370", 1
        )

    @patch("apps.pedagogico.services.get_turmas_recorte_por_tipo")
    @patch("apps.alunos.services.get_codigos_turmas_regulares_aluno")
    def test_alunos_vazio_nao_chama_recorte(
        self, mock_alunos: MagicMock, mock_recorte: MagicMock
    ) -> None:
        """Valida que quando o Alunos-MS retorna lista vazia, o recorte não é chamado."""
        mock_alunos.return_value = []

        result = services.montar_codigos_turmas_regulares_aluno(
            ano_letivo="2026", codigo_aluno="7345634"
        )

        self.assertEqual(result, [])
        mock_recorte.assert_not_called()


def _resp_lista(payload: list) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"[]"
    mock_resp.json.return_value = payload
    return mock_resp


class GetAlunosAutocompleteUeTest(SimpleTestCase):
    """Valida a consulta de autocomplete de alunos da UE."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_params_completos(
        self, mock_get: MagicMock
    ) -> None:
        payload = [{"codigo_aluno": 123456}]
        mock_get.return_value = _resp_lista(payload)

        result = services.get_alunos_autocomplete_ue(
            codigo_ue="100001",
            ano_letivo="2026",
            codigo_turmas=["9001"],
            nome_aluno="Fulano",
            codigo_eol="123456",
            somente_ativos="true",
            eh_historico="false",
            limite=5,
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/anos_letivos/2026/autocomplete",
            params={
                "limite": 5,
                "codigos_turmas": ["9001"],
                "nome_aluno": "Fulano",
                "codigo_eol": "123456",
                "somente_ativos": "true",
                "eh_historico": "false",
            },
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_params_minimos(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _resp_lista([])

        result = services.get_alunos_autocomplete_ue(
            codigo_ue="100001", ano_letivo="2026"
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ues/100001/anos_letivos/2026/autocomplete",
            params={"limite": 10},
        )
        self.assertEqual(result, [])


class GetDadosAcompanhamentoEscolarTest(SimpleTestCase):
    """Valida a consulta de dados de acompanhamento escolar."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_filtros(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_eol": 7074492}]
        mock_get.return_value = _resp_lista(payload)

        result = services.get_dados_acompanhamento_escolar(
            codigo_aluno="7074492",
            codigo_dre="108200",
            codigo_ue="019267",
            cpf_responsavel="12345678901",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/dados-acompanhamento-escolar/contrato",
            params={
                "codigo_aluno": "7074492",
                "codigo_dre": "108200",
                "codigo_ue": "019267",
                "cpf_responsavel": "12345678901",
            },
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_sem_filtros_envia_params_none(
        self, mock_get: MagicMock
    ) -> None:
        mock_get.return_value = _resp_lista([])

        result = services.get_dados_acompanhamento_escolar()

        mock_get.assert_called_once_with(
            f"{_BASE}/dados-acompanhamento-escolar/contrato",
            params=None,
        )
        self.assertEqual(result, [])


class GetTurmasAlunoComHistoricoTest(SimpleTestCase):
    """Valida a consulta de turmas do aluno com histórico."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_turma": 9001}]
        mock_get.return_value = _resp_lista(payload)

        result = services.get_turmas_aluno_com_historico(
            "7074492", "2026", "false", "true", "true"
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/7074492/turmas/anos_letivos/2026"
            "/historico/false/filtrar_situacao/true/tipo_turma/true"
        )
        self.assertEqual(result, payload)


class ListarAlunosPorAnoTest(SimpleTestCase):
    """Valida a consulta de alunos por códigos e ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_com_codigos(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_aluno": 1}]
        mock_get.return_value = _resp_lista(payload)

        result = services.listar_alunos_por_ano("2026", ["1", "2"])

        mock_get.assert_called_once_with(
            f"{_BASE}/ano_letivo/2026/alunos",
            params={"codigos_aluno": ["1", "2"]},
        )
        self.assertEqual(result, payload)


class GetQuantidadeMatriculadosCCTest(SimpleTestCase):
    """Valida a consulta de matriculados por componente curricular."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_filtros(self, mock_get: MagicMock) -> None:
        payload = [{"componente_curricular_id": 1310}]
        mock_get.return_value = _resp_lista(payload)

        result = services.get_quantidade_matriculados_cc(
            ano_letivo="2026",
            componentes_curriculares=["1310"],
            dre_id="109100",
            ue_id="093181",
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ano-letivo/2026/matriculados/contrato",
            params={
                "componentes_curriculares": ["1310"],
                "dre_id": "109100",
                "ue_id": "093181",
            },
        )
        self.assertEqual(result, payload)


class GetQuantidadeMatriculadosTest(SimpleTestCase):
    """Valida a consulta da quantidade de matriculados."""

    @patch.object(services._client, "get")
    def test_chama_sidecar_com_filtros(self, mock_get: MagicMock) -> None:
        payload = [{"quantidade": 28}]
        mock_get.return_value = _resp_lista(payload)

        result = services.get_quantidade_matriculados(
            ano_letivo="2026",
            dre_codigo="108200",
            ue_codigo="019267",
            modalidade=["5"],
            ano=["3"],
            turma=["3038818"],
        )

        mock_get.assert_called_once_with(
            f"{_BASE}/ano-letivo/2026/matriculados/quantidade/contrato",
            params={
                "dre_codigo": "108200",
                "ue_codigo": "019267",
                "modalidade": ["5"],
                "ano": ["3"],
                "turma": ["3038818"],
            },
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_sem_filtros_envia_params_none(
        self, mock_get: MagicMock
    ) -> None:
        mock_get.return_value = _resp_lista([])

        result = services.get_quantidade_matriculados(ano_letivo="2026")

        mock_get.assert_called_once_with(
            f"{_BASE}/ano-letivo/2026/matriculados/quantidade/contrato",
            params=None,
        )
        self.assertEqual(result, [])
