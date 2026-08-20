"""Valida os serviços do domínio de professores."""

from datetime import date, datetime
from typing import Any
from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from apps.professores import services


class VerificarAtribuicaoProfessorTurmaTest(SimpleTestCase):
    """Valida a verificação de atribuição do professor na turma."""

    @patch("apps.professores.services._client")
    def test_chama_sidecar_e_retorna_booleano(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = True

        result = services.verificar_atribuicao_professor_turma(
            "000001",
            "9100002",
            "2026-07-28",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/9100002/"
            "atribuicao/verificar/data/?data_consulta=2026-07-28"
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertIs(result, True)


class GetStatusAtribuicaoProfessorTurmaTest(SimpleTestCase):
    """Valida a consulta do status da atribuição."""

    @patch("apps.professores.services._client")
    def test_chama_sidecar_e_retorna_payload(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = {
            "ano_atribuicao": 2026,
            "data_cancelamento": None,
            "data_disponibilizacao": "2026-07-28",
            "data_fim_turma": "2026-12-22",
            "codigo_motivo_disponibilizacao": None,
        }

        result = services.get_status_atribuicao_professor_turma(
            "000001",
            "9100002",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/9100002/atribuicao/status/"
        )
        assert result is not None
        self.assertEqual(result["ano_atribuicao"], 2026)


class VerificarAtribuicaoProfessorTurmaDisciplinaTest(SimpleTestCase):
    """Valida a verificação por disciplina e data tick."""

    @patch("apps.professores.services._client")
    def test_chama_sidecar_e_retorna_booleano(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = True

        result = services.verificar_atribuicao_professor_turma_disciplina(
            "000001",
            "9100002",
            "89",
            639207072000000000,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/9100002/disciplinas/89/"
            "atribuicao/verificar/datatick/"
            "?data_consulta_tick=639207072000000000"
        )
        self.assertIs(result, True)


class VerificarRecorrenciaDatasTest(SimpleTestCase):
    """Valida a regra legada de recorrência das atribuições."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_permite_disciplina_filha_dentro_da_atribuicao(
        self,
        mock_client: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "90",
                "data_inicio_atribuicao": "2026-02-01T00:00:00",
                "data_fim_atribuicao": "2026-12-01T00:00:00",
                "data_fim_turma": "2026-12-22T00:00:00",
            }
        ]
        mock_componentes.return_value = [
            {
                "id_componente_curricular": 90,
                "id_componente_curricular_pai": 89,
            }
        ]

        resultado = services.verificar_recorrencia_datas(
            "000001",
            "9100002",
            "89",
            ["639207072000000000"],
        )

        self.assertEqual(
            resultado,
            [
                {
                    "data": "2026-07-27T00:00:00",
                    "pode_persistir": True,
                }
            ],
        )
        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/anos_letivos/2026/"
        )

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_retorna_false_sem_atribuicao_compativel(
        self,
        mock_client: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9999999",
                "disciplina_id": "100",
                "data_inicio_atribuicao": "2026-02-01T00:00:00",
                "data_fim_atribuicao": "2026-06-01T00:00:00",
                "data_fim_turma": "2026-12-22T00:00:00",
            }
        ]
        mock_componentes.return_value = []

        resultado = services.verificar_recorrencia_datas(
            "000001",
            "9100002",
            "89",
            ["639207072000000000"],
        )

        self.assertFalse(resultado[0]["pode_persistir"])

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_preserva_ou_com_fim_da_atribuicao_apos_fim_da_turma(
        self,
        mock_client: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "outra-turma",
                "disciplina_id": "outra-disciplina",
                "data_inicio_atribuicao": "2026-02-01T00:00:00",
                "data_fim_atribuicao": "2026-12-22T00:00:00",
                "data_fim_turma": "2026-12-22T00:00:00",
            }
        ]
        mock_componentes.return_value = []

        resultado = services.verificar_recorrencia_datas(
            "000001",
            "9100002",
            "89",
            ["639207072000000000"],
        )

        self.assertTrue(resultado[0]["pode_persistir"])

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_atribuicoes_territorio_saber"
    )
    def test_consulta_territorio_saber_para_componente_agrupado(
        self,
        mock_atribuicoes: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        """Consulta o pedagógico quando o componente é um agrupamento."""
        mock_atribuicoes.return_value = []
        mock_componentes.return_value = []

        services.verificar_recorrencia_datas(
            "000001",
            "9100002",
            "800000",
            ["639207072000000000"],
        )

        mock_atribuicoes.assert_called_once_with("000001", 2026)

    def test_componente_nao_numerico_nao_e_agrupamento(self) -> None:
        """Rejeita identificador não numérico sem levantar exceção."""
        self.assertFalse(
            services._validar_componente_eh_territorio_saber_agrupado(
                "invalido"
            )
        )

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_atribuicoes_territorio_saber"
    )
    @patch("apps.professores.services._client")
    def test_retorna_atribuicoes_das_duas_origens(
        self,
        mock_client: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
    ) -> None:
        """Retorna atribuições comuns e de Território do Saber."""
        atribuicao = {
            "codigo_turma": 9100002,
            "ano_letivo": "2026",
            "nome_turma": "7A",
            "data_inicio_atribuicao": "2026-02-01T00:00:00",
            "data_fim_atribuicao": "2026-12-01T00:00:00",
            "data_fim_turma": "2026-12-22T00:00:00",
            "ano_atribuicao": "2026",
            "codigo_rf": 1,
            "disciplina_id": 89,
            "disciplina_nome": "CIENCIAS",
            "disciplinas_agrupadas_ids": [90],
            "nome_professor": "PROFESSOR",
        }
        mock_client.json_or_none.return_value = [atribuicao]
        mock_atribuicoes_territorio.return_value = [atribuicao]

        atribuicoes_comuns = (
            services._get_atribuicoes_professor_turma_disciplina(
                "000001", "89", 2026
            )
        )
        atribuicoes_territorio = (
            services._get_atribuicoes_professor_turma_disciplina(
                "000001", "800000", 2026
            )
        )

        self.assertEqual(atribuicoes_territorio, atribuicoes_comuns)
        self.assertEqual(atribuicoes_territorio[0]["codigo_turma"], 9100002)
        self.assertEqual(atribuicoes_territorio[0]["ano_letivo"], "2026")
        self.assertEqual(atribuicoes_territorio[0]["disciplina_id"], 89)


class VerificarAtribuicaoPeriodoTest(SimpleTestCase):
    """Valida atribuições que sobrepõem o período consultado."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch(
        "apps.professores.services."
        "_get_atribuicoes_professor_turma_disciplina"
    )
    def test_retorna_true_nas_tres_formas_de_sobreposicao(
        self,
        mock_atribuicoes: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        """Aceita período iniciando, terminando ou contido na consulta."""
        mock_componentes.return_value = []
        periodos_atribuicao = [
            ("2026-06-01T00:00:00", "2026-07-15T00:00:00"),
            ("2026-07-15T00:00:00", "2026-09-01T00:00:00"),
            ("2026-07-10T00:00:00", "2026-07-20T00:00:00"),
        ]

        for inicio_atribuicao, fim_atribuicao in periodos_atribuicao:
            with self.subTest(inicio_atribuicao=inicio_atribuicao):
                mock_atribuicoes.return_value = [
                    {
                        "codigo_turma": "9100002",
                        "disciplina_id": "89",
                        "data_inicio_atribuicao": inicio_atribuicao,
                        "data_fim_atribuicao": fim_atribuicao,
                    }
                ]

                resultado = services.verificar_atribuicao_periodo(
                    "000001",
                    "9100002",
                    "89",
                    "2026-07-01T00:00:00",
                    "2026-07-31T00:00:00",
                )

                self.assertTrue(resultado)

        self.assertEqual(mock_atribuicoes.call_count, 3)
        mock_atribuicoes.assert_called_with("000001", "89", 0)

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_atribuicoes_territorio_saber"
    )
    def test_territorio_saber_busca_atribuicoes_sem_ano(
        self,
        mock_atribuicoes: MagicMock,
    ) -> None:
        """Não restringe por ano a consulta usada na verificação."""
        mock_atribuicoes.return_value = []

        services._get_atribuicoes_professor_turma_disciplina(
            "000001",
            "800000",
            0,
        )

        mock_atribuicoes.assert_called_once_with("000001")

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch(
        "apps.professores.services."
        "_get_atribuicoes_professor_turma_disciplina"
    )
    def test_aceita_atribuicao_de_componente_filho(
        self,
        mock_atribuicoes: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        """Considera componente cuja disciplina pai é a consultada."""
        mock_atribuicoes.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "90",
                "data_inicio_atribuicao": "2026-07-01T00:00:00",
                "data_fim_atribuicao": "2026-07-31T00:00:00",
            }
        ]
        mock_componentes.return_value = [
            {
                "id_componente_curricular": 90,
                "id_componente_curricular_pai": 89,
            }
        ]

        resultado = services.verificar_atribuicao_periodo(
            "000001",
            "9100002",
            "89",
            "2026-07-10T00:00:00",
            "2026-07-20T00:00:00",
        )

        self.assertTrue(resultado)

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch(
        "apps.professores.services."
        "_get_atribuicoes_professor_turma_disciplina"
    )
    def test_retorna_false_sem_sobreposicao(
        self,
        mock_atribuicoes: MagicMock,
        mock_componentes: MagicMock,
    ) -> None:
        """Rejeita atribuição completamente fora do período."""
        mock_atribuicoes.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "89",
                "data_inicio_atribuicao": "2026-08-01T00:00:00",
                "data_fim_atribuicao": "2026-08-31T00:00:00",
            }
        ]
        mock_componentes.return_value = []

        resultado = services.verificar_atribuicao_periodo(
            "000001",
            "9100002",
            "89",
            "2026-07-01T00:00:00",
            "2026-07-31T00:00:00",
        )

        self.assertFalse(resultado)

    @patch(
        "apps.professores.services."
        "_get_atribuicoes_professor_turma_disciplina"
    )
    def test_retorna_false_para_periodo_invalido(
        self,
        mock_atribuicoes: MagicMock,
    ) -> None:
        """Não consulta atribuições quando o período é inválido."""
        resultado = services.verificar_atribuicao_periodo(
            "000001",
            "9100002",
            "89",
            "2026-08-01T00:00:00",
            "2026-07-01T00:00:00",
        )

        self.assertFalse(resultado)
        mock_atribuicoes.assert_not_called()


class VerificarAtribuicaoDisciplinaTerritorioSaberTest(SimpleTestCase):
    """Valida a verificação por data e território do saber."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "verificar_atriuicao_territorio_saber"
    )
    def test_delega_consulta_de_territorio_ao_servico_pedagogico(
        self,
        mock_verificar: MagicMock,
    ) -> None:
        """Repassa os dados da consulta ao domínio pedagógico."""
        mock_verificar.return_value = True

        result = services.verificar_atribuicao_disciplina_territorio_saber(
            "000001",
            "9100002",
            "89",
            "2026-07-28",
            True,
        )

        mock_verificar.assert_called_once_with(
            "000001",
            "9100002",
            "89",
            "2026-07-28",
        )
        self.assertIs(result, True)

    @patch("apps.professores.services._client")
    def test_repassa_retorno_do_sidecar_quando_nao_e_territorio(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = True

        result = services.verificar_atribuicao_disciplina_territorio_saber(
            "000001",
            "9100002",
            "89",
            "2026-07-28",
            False,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/9100002/disciplinas/89/"
            "atribuicao/verificar/data/?data_consulta=2026-07-28"
        )
        self.assertIs(result, True)


class GetAtribuicoesTurmaDisciplinaTest(SimpleTestCase):
    """Valida a consulta de atribuições da turma e disciplina."""

    @patch("apps.professores.services._client")
    def test_retorna_lista_do_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "9100002",
                "ano_letivo": None,
                "nome_turma": "7A",
                "data_inicio_atribuicao": "2026-06-09T00:00:00",
                "data_fim_atribuicao": "2026-12-22T00:00:00",
                "data_fim_turma": "2026-12-22T00:00:00",
                "ano_atribuicao": 2026,
                "codigo_rf": "7900009",
                "disciplina_id": "89",
                "disciplina_nome": "CIENCIAS",
                "disciplinas_agrupadas_ids": None,
                "nome_professor": "LAZARO PRETEL",
            }
        ]

        result = services.get_atribuicoes_turma_disciplina(
            "9100002",
            "89",
            "639207072000000000",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/9100002/disciplinas/89/atribuicao/data/",
            params={"data_ticks": "639207072000000000"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["codigo_turma"], "9100002")
        self.assertEqual(result[0]["disciplina_nome"], "CIENCIAS")

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_payload_nao_e_lista(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = "Not Found"

        result = services.get_atribuicoes_turma_disciplina(
            "9100002",
            "89",
            "639207072000000000",
        )

        self.assertEqual(result, [])


class GetProfessorTest(SimpleTestCase):
    """Valida a extração do nome do professor."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida extração do nome retornado."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigoRf":"123456","nome":"Fulano de Tal"}'
        mock_resp.json.return_value = {
            "codigoRf": "123456",
            "nome": "Fulano de Tal",
        }
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        mock_get.assert_called_once_with("/api/v1/professores/123456")
        self.assertEqual(result, "Fulano de Tal")

    @patch.object(services._client, "get")
    def test_retorna_texto_quando_sidecar_envia_string(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'"Fulano de Tal"'
        mock_resp.json.return_value = "Fulano de Tal"
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertEqual(result, "Fulano de Tal")

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertIsNone(result)

    @patch.object(services._client, "get")
    def test_retorna_texto_quando_resposta_nao_tem_json(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html></html>"
        mock_resp.json.side_effect = ValueError("sem json")
        mock_resp.text = "<html></html>"
        mock_get.return_value = mock_resp

        result = services.get_professor("123456")

        self.assertEqual(result, "<html></html>")


class GetValidadeProfessorTest(SimpleTestCase):
    """Valida a consulta de validade do professor."""

    @patch("apps.professores.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Valida consulta de validade do professor."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = True
        mock_client.get.return_value = mock_resp

        result = services.get_validade_professor("123456")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/123456/validade"
        )
        self.assertTrue(result)


class GetFuncionarioAtivoTest(SimpleTestCase):
    """Valida a consulta de funcionário ativo."""

    @patch("apps.professores.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Valida consulta de funcionário ativo."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = True
        mock_client.get.return_value = mock_resp

        result = services.get_funcionario_ativo("RF001")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/acessos/funcionario-ativo/RF001"
        )
        self.assertTrue(result)


class GetNomeServidorTest(SimpleTestCase):
    """Valida a consulta de nome do servidor."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Valida consulta de dados do servidor."""
        payload = {"nome": "Maria", "cpf": "000.000.000-00"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"nome": "Maria", "cpf": "000.000.000-00"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_nome_servidor("RF001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/nome-servidor/RF001"
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_nome_servidor("RF001")

        self.assertIsNone(result)


class GetNomeUsuarioEolTest(SimpleTestCase):
    """Valida a consulta de nome de usuário EOL."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'"NOME USUARIO EOL"'
        mock_resp.json.return_value = "NOME USUARIO EOL"
        mock_get.return_value = mock_resp

        result = services.get_nome_usuario_eol("RF001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/nome-usuario-eol/RF001"
        )
        self.assertEqual(result, "NOME USUARIO EOL")

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_nome_usuario_eol("RF001")

        self.assertIsNone(result)


class GetProfessorPorRfTest(SimpleTestCase):
    """Valida a busca de professor por RF e ano letivo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf("000001", 2026)

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRf/2026"
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_chama_path_com_buscar_outros_cargos(
        self, mock_get: MagicMock
    ) -> None:
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf("000001", 2026, True)

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRf/2026",
            params={"buscar_outros_cargos": True},
        )
        self.assertEqual(result, payload)


class GetProfessoresPorListaRfTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [{"codigo_rf": "000001", "nome": "NOME PROFESSOR"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'[{"codigo_rf":"000001","nome":"NOME"}]'
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_professores_por_lista_rf(["000001"])

        mock_post.assert_called_once_with(
            "/api/v1/professores/funcionarios/BuscarPorListaRF/",
            payload=["000001"],
        )
        self.assertEqual(result, payload)


class GetFuncionarioExternoTest(SimpleTestCase):
    """Valida a busca de funcionario externo por CPF."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "nome_pessoa": "NOME PESSOA",
                "cpf": "11122233355",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionario_externo("11122233355")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/"
            "funcionario-externo/11122233355/"
        )
        self.assertEqual(result, payload)


class GetFuncionariosPorListaLoginTest(SimpleTestCase):
    """Valida a busca de funcionarios por lista de login."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "login": "7900010",
                "nome_servidor": "NOME SERVIDOR",
                "perfil": "00000000-0000-0000-0000-000000000000",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_funcionarios_por_lista_login(["7900010"])

        mock_post.assert_called_once_with(
            "/api/v1/professores/funcionarios/BuscarPorListaLogin/",
            payload=["7900010"],
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaTest(SimpleTestCase):
    """Valida a busca de funcionários por escola."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "codigo_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola("000123")

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios/"
        )
        self.assertEqual(result, payload)


class GetFuncionariosUeTest(SimpleTestCase):
    """Valida a busca de funcionários por unidade educacional."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": "DIRETOR",
                "codigo_tipo_funcao_atividade": 0,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp
        body = {"codigosRfs": ["000001"], "filtro": ""}

        result = services.get_funcionarios_ue("000123", body)

        mock_post.assert_called_once_with(
            "/api/v1/professores/funcionarios/ue/000123/",
            payload=body,
        )
        self.assertEqual(result, payload)


class GetFuncionariosPorCargoTest(SimpleTestCase):
    """Valida a busca de funcionários por cargo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": "DIRETOR",
                "codigo_tipo_funcao_atividade": 0,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_por_cargo("3360")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/cargos/3360/"
        )
        self.assertEqual(result, payload)


class GetSupervisoresPorDreTest(SimpleTestCase):
    """Valida a busca de supervisores por DRE."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_supervisores_por_dre("100001", ["000001"])

        mock_post.assert_called_once_with(
            "/api/v1/professores/funcionarios/supervisores/100001/",
            payload=["000001"],
        )
        self.assertEqual(result, payload)


class GetSupervisoresDreTest(SimpleTestCase):
    """Valida a busca de supervisores da DRE via endpoint canonico."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "7900002",
                "nome_servidor": "NOME SERVIDOR",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_supervisores_dre("100001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/dres/100001/supervisores/"
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaPorCargoTest(SimpleTestCase):
    """Valida a busca de funcionários por escola e cargo."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        payload = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "codigo_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_cargo("000123", "14")

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios/?cargos=14"
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaCargosTest(SimpleTestCase):
    """Valida busca de funcionários por cargos."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        mock_resp_3239 = MagicMock()
        mock_resp_3239.status_code = 200
        mock_resp_3239.content = b"[{}]"
        mock_resp_3239.json.return_value = [
            {
                "codigo_rf": "7900005",
                "nome": None,
            },
        ]
        mock_resp_3240 = MagicMock()
        mock_resp_3240.status_code = 200
        mock_resp_3240.content = b"[{}]"
        mock_resp_3240.json.return_value = [
            {
                "codigo_rf": "7900006",
                "nome": None,
            },
        ]
        mock_get.side_effect = [mock_resp_3239, mock_resp_3240]

        result = services.get_funcionarios_escola_cargos(
            "000103",
            {"cargos": ["3239", "3240"], "dre_codigo": "1"},
        )

        mock_get.assert_has_calls(
            [
                call(
                    "/api/v1/professores/escolas/000103/funcionarios/",
                    params={"cargos": ["3239"], "dre_codigo": "1"},
                ),
                call(
                    "/api/v1/professores/escolas/000103/funcionarios/",
                    params={"cargos": ["3240"], "dre_codigo": "1"},
                ),
            ]
        )
        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": "7900005",
                    "nome": None,
                    "cargo_id": 3239,
                },
                {
                    "codigo_rf": "7900006",
                    "nome": None,
                    "cargo_id": 3240,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_sem_cargos(self, mock_get: MagicMock) -> None:
        result = services.get_funcionarios_escola_cargos("000103", {})

        mock_get.assert_not_called()
        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_sidecar_nao_retorna_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = {"codigo_rf": "7900005"}
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_cargos(
            "000103",
            {"cargos": "3239", "dre_codigo": "1"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000103/funcionarios/",
            params={"cargos": ["3239"], "dre_codigo": "1"},
        )
        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_com_apenas_dre_codigo(
        self, mock_get: MagicMock
    ) -> None:
        result = services.get_funcionarios_escola_cargos(
            "000103",
            {"dre_codigo": "1"},
        )

        mock_get.assert_not_called()
        self.assertEqual(result, [])


class GetUsuariosSgpPorPerfilTest(SimpleTestCase):
    """Valida busca de usuários SGP por perfil."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_rf": "000001"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_usuarios_sgp_por_perfil(
            "perfil-x",
            {"codigo_dre": "100001"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/perfis/perfil-x/",
            params={"codigo_dre": "100001"},
        )
        self.assertEqual(result, payload)


class GetFuncionariosSgpPorPerfilDreTest(SimpleTestCase):
    """Valida busca de funcionários SGP por perfil e DRE."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        payload = [{"codigo_rf": "000001"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_sgp_por_perfil_dre(
            "perfil-x",
            "100001",
            {"codigo_ue": "000102"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/funcionarios/perfis/perfil-x/dres/100001/",
            params={"codigo_ue": "000102"},
        )
        self.assertEqual(result, payload)


class GetFuncionariosEscolaFuncoesAtividadesTest(SimpleTestCase):
    """Valida busca de funcionários por funções atividades."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        mock_resp_30 = MagicMock()
        mock_resp_30.status_code = 200
        mock_resp_30.content = b"[{}]"
        mock_resp_30.json.return_value = [
            {
                "codigo_rf": "7900007",
                "nome": None,
                "codigo_funcao_atividade": 30,
            },
        ]
        mock_resp_31 = MagicMock()
        mock_resp_31.status_code = 200
        mock_resp_31.content = b"[{}]"
        mock_resp_31.json.return_value = [
            {
                "codigo_rf": "7900008",
                "nome": None,
                "codigo_funcao_atividade": 31,
            },
        ]
        mock_get.side_effect = [mock_resp_30, mock_resp_31]

        result = services.get_funcionarios_escola_funcoes_atividades(
            "000103",
            {"funcoes_atividades": ["30", "31"], "codigo_dre": "1"},
        )

        mock_get.assert_has_calls(
            [
                call(
                    "/api/v1/professores/escolas/000103/funcionarios/",
                    params={
                        "funcoes_atividades": ["30"],
                        "codigo_dre": "1",
                    },
                ),
                call(
                    "/api/v1/professores/escolas/000103/funcionarios/",
                    params={
                        "funcoes_atividades": ["31"],
                        "codigo_dre": "1",
                    },
                ),
            ]
        )
        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": "7900007",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "codigo_rf": "7900008",
                    "nome": None,
                    "codigo_funcao_atividade": 31,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_adiciona_primeira_funcao_atividade_quando_payload_nao_tem_id(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp_30 = MagicMock()
        mock_resp_30.status_code = 200
        mock_resp_30.content = b"[{}]"
        mock_resp_30.json.return_value = [
            {
                "codigo_rf": "7900007",
                "nome": None,
            },
        ]
        mock_resp_31 = MagicMock()
        mock_resp_31.status_code = 200
        mock_resp_31.content = b"[{}]"
        mock_resp_31.json.return_value = [
            {
                "codigo_rf": "7900008",
                "nome": None,
            },
        ]
        mock_get.side_effect = [mock_resp_30, mock_resp_31]

        result = services.get_funcionarios_escola_funcoes_atividades(
            "000103",
            {"funcoes_atividades": ["30", "31"], "codigo_dre": "1"},
        )

        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": "7900007",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "codigo_rf": "7900008",
                    "nome": None,
                    "codigo_funcao_atividade": 31,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_com_apenas_codigo_dre(
        self, mock_get: MagicMock
    ) -> None:
        result = services.get_funcionarios_escola_funcoes_atividades(
            "000103",
            {"codigo_dre": "1"},
        )

        mock_get.assert_not_called()
        self.assertEqual(result, [])


class GetFuncionariosEscolaFuncoesExternasTest(SimpleTestCase):
    """Valida busca de funcionários por funções externas."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        mock_resp_5 = MagicMock()
        mock_resp_5.status_code = 200
        mock_resp_5.content = b"[{}]"
        mock_resp_5.json.return_value = [
            {
                "cpf": "11122233366",
                "funcao_externo": 5,
            },
        ]
        mock_resp_6 = MagicMock()
        mock_resp_6.status_code = 200
        mock_resp_6.content = b"[{}]"
        mock_resp_6.json.return_value = [
            {
                "cpf": "11122233367",
                "funcao_externo": 6,
            },
        ]
        mock_get.side_effect = [mock_resp_5, mock_resp_6]

        result = services.get_funcionarios_escola_funcoes_externas(
            "400870",
            {"funcoes": ["5", "6"], "codigo_dre": "1"},
        )

        mock_get.assert_has_calls(
            [
                call(
                    "/api/v1/professores/escolas/400870/funcionarios/",
                    params={"codigo_dre": "1", "funcoes_externas": ["5"]},
                ),
                call(
                    "/api/v1/professores/escolas/400870/funcionarios/",
                    params={"codigo_dre": "1", "funcoes_externas": ["6"]},
                ),
            ]
        )
        self.assertEqual(
            result,
            [
                {
                    "cpf": "11122233366",
                    "funcao_externo": 5,
                },
                {
                    "cpf": "11122233367",
                    "funcao_externo": 6,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_adiciona_primeira_funcao_externa_quando_payload_nao_tem_id(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp_5 = MagicMock()
        mock_resp_5.status_code = 200
        mock_resp_5.content = b"[{}]"
        mock_resp_5.json.return_value = [
            {
                "cpf": "11122233366",
            },
        ]
        mock_resp_6 = MagicMock()
        mock_resp_6.status_code = 200
        mock_resp_6.content = b"[{}]"
        mock_resp_6.json.return_value = [
            {
                "cpf": "11122233367",
            },
        ]
        mock_get.side_effect = [mock_resp_5, mock_resp_6]

        result = services.get_funcionarios_escola_funcoes_externas(
            "400870",
            {"funcoes": ["5", "6"], "codigo_dre": "1"},
        )

        self.assertEqual(
            result,
            [
                {
                    "cpf": "11122233366",
                    "funcao_externo": 5,
                },
                {
                    "cpf": "11122233367",
                    "funcao_externo": 6,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_com_apenas_codigo_dre(
        self, mock_get: MagicMock
    ) -> None:
        result = services.get_funcionarios_escola_funcoes_externas(
            "400870",
            {"codigo_dre": "1"},
        )

        mock_get.assert_not_called()
        self.assertEqual(result, [])


class GetFuncionariosEscolaPorFuncaoExternaTest(SimpleTestCase):
    """Valida a busca de funcionários por uma função externa."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica se o path é chamado corretamente."""
        payload = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": None,
                "data_fim": None,
                "cargo": "",
                "codigo_cargo": "",
                "codigo_tipo_funcao_atividade": 0,
                "esta_afastado": False,
                "funcao_externo": 7,
                "tipo_funcao_externo": 2,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_funcao_externa(
            "000123",
            "7",
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios/",
            params={"funcoes_externas": "7"},
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        """Verifica se retorna None quando o status code é 204."""
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_funcao_externa(
            "000123",
            "7",
        )

        self.assertIsNone(result)


class GetFuncionariosEscolaPorFuncaoAtividadeTest(SimpleTestCase):
    """Valida a busca de funcionários por uma função atividade."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica se o path é chamado corretamente."""
        payload = [
            {
                "codigo_rf": "7900003",
                "nome": "NOME SERVIDOR",
                "codigo_cargo": "3379",
                "codigo_tipo_funcao_atividade": 1,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_funcao_atividade(
            "000123",
            "1",
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/000123/funcionarios/",
            params={"funcoes_atividades": "1"},
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        """Verifica se retorna None quando o status code é 204."""
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_por_funcao_atividade(
            "000123",
            "1",
        )

        self.assertIsNone(result)


class GetTurmasProfessorTest(SimpleTestCase):
    """Valida a busca de turmas atribuídas ao professor."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica se o path é chamado corretamente."""
        payload = [{"codigo_turma": 9100001, "nome_turma": "1A"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_turmas_professor("000001")

        mock_get.assert_called_once_with("/api/v1/professores/000001/turmas/")
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_retorna_none_quando_204(self, mock_get: MagicMock) -> None:
        """Verifica se retorna None quando o status code é 204."""
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.get_turmas_professor("000001")

        self.assertIsNone(result)


class GetProfessorPorRfDreUeTest(SimpleTestCase):
    """Valida a busca de professor por RF, DRE e UE."""

    @patch.object(services._client, "get")
    def test_chama_path_sem_params(self, mock_get: MagicMock) -> None:
        """Valida chamada sem parâmetros adicionais."""
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf_dre_ue("000001", 2026)

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRfDreUe/2026",
            params=None,
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_chama_path_com_params(self, mock_get: MagicMock) -> None:
        """Valida chamada com parâmetros adicionais."""
        payload = {"codigo_rf": "000001", "nome": "NOME PROFESSOR"}
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"codigo_rf":"000001","nome":"NOME"}'
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_professor_por_rf_dre_ue(
            "000001",
            2026,
            {"dre_id": "1", "ue_id": "000103"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRfDreUe/2026",
            params={"dre_id": "1", "ue_id": "000103"},
        )
        self.assertEqual(result, payload)


class GetProfessoresPorListaRfAnoTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF e ano."""

    def _mock_sidecar(self, dados: list[dict]) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = dados
        return mock_resp

    @patch.object(services._client, "post")
    def test_retorna_lista_do_sidecar(self, mock_post: MagicMock) -> None:
        """Repassa diretamente o retorno do sidecar (um item por turma)."""
        payload = [
            {"codigo_rf": "000001", "nome": "NOME"},
            {"codigo_rf": "000001", "nome": "NOME"},
        ]
        mock_post.return_value = self._mock_sidecar(payload)

        result = services.get_professores_por_lista_rf_ano(2026, ["000001"])

        mock_post.assert_called_once_with(
            "/api/v1/professores/2026/BuscarPorListaRF/",
            payload=["000001"],
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "post")
    def test_sem_resultados_retorna_vazio(self, mock_post: MagicMock) -> None:
        """Retorna lista vazia quando o sidecar não encontra professores."""
        mock_post.return_value = self._mock_sidecar([])

        result = services.get_professores_por_lista_rf_ano(2026, ["000001"])

        self.assertEqual(result, [])


class GetEhEmeiTest(SimpleTestCase):
    """Valida vínculo com EMEI."""

    @patch(
        "apps.professores.services.institucional_services.get_codigos_ue_emei"
    )
    @patch("apps.professores.services.get_unidades_atribuicao_professor")
    def test_intersecao_nao_vazia_retorna_true(
        self, mock_ues: MagicMock, mock_emei: MagicMock
    ) -> None:
        """Retorna verdadeiro quando há intersecção de UEs."""
        mock_ues.return_value = ["000102", "000999"]
        mock_emei.return_value = ["000102"]

        result = services.get_eh_emei("000001")

        mock_ues.assert_called_once_with("000001")
        mock_emei.assert_called_once_with(["000102", "000999"])
        self.assertTrue(result)

    @patch(
        "apps.professores.services.institucional_services.get_codigos_ue_emei"
    )
    @patch("apps.professores.services.get_unidades_atribuicao_professor")
    def test_intersecao_vazia_retorna_false(
        self, mock_ues: MagicMock, mock_emei: MagicMock
    ) -> None:
        """Retorna falso quando não há intersecção de UEs."""
        mock_ues.return_value = ["000102"]
        mock_emei.return_value = []

        self.assertFalse(services.get_eh_emei("000001"))

    @patch(
        "apps.professores.services.institucional_services.get_codigos_ue_emei"
    )
    @patch("apps.professores.services.get_unidades_atribuicao_professor")
    def test_sem_atribuicao_nao_chama_institucional(
        self, mock_ues: MagicMock, mock_emei: MagicMock
    ) -> None:
        """Não consulta institucional sem UEs atribuídas."""
        mock_ues.return_value = []

        result = services.get_eh_emei("000001")

        self.assertFalse(result)
        mock_emei.assert_not_called()


class GetUnidadesAtribuicaoProfessorTest(SimpleTestCase):
    """Valida a coleta de UEs com atribuição válida do professor."""

    @patch.object(services._client, "get")
    def test_extrai_codigos_ue(self, mock_get: MagicMock) -> None:
        """Extrai códigos de UEs do payload."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = {
            "codigo_rf": "000001",
            "codigos_ue": ["000102"],
        }
        mock_get.return_value = mock_resp

        result = services.get_unidades_atribuicao_professor("000001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/unidades-atribuicao/"
        )
        self.assertEqual(result, ["000102"])


class GetAutoCompleteProfessoresTest(SimpleTestCase):
    """Valida o autocomplete de professores por DRE e ano."""

    @patch.object(services._client, "get")
    def test_chama_path_sem_params(self, mock_get: MagicMock) -> None:
        """Valida chamada do path correto sem parâmetros adicionais."""
        payload = [{"codigo_rf": "000001", "nome_servidor": "NOME"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_autocomplete_professores(2026, "1")

        mock_get.assert_called_once_with(
            "/api/v1/professores/2026/AutoComplete/1",
            params=None,
        )
        self.assertEqual(result, payload)

    @patch.object(services._client, "get")
    def test_chama_path_com_params(self, mock_get: MagicMock) -> None:
        """Valida chamada do path correto com parâmetros adicionais."""
        payload = [{"codigo_rf": "000001", "nome_servidor": "NOME"}]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        result = services.get_autocomplete_professores(
            2026,
            "1",
            {"ue_id": "000103", "nome": "ana"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/2026/AutoComplete/1",
            params={"ue_id": "000103", "nome": "ana"},
        )
        self.assertEqual(result, payload)


class GetTurmasProfessorDisciplinaTest(SimpleTestCase):
    """Valida a busca de turmas por professor e disciplina."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "codigo_turma": "9100001",
                "data_disponibilizacao_aulas": "2026-12-22T00:00:00",
                "data_atribuicao_aula": "2026-03-30T00:00:00",
            },
        ]
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = payload
        mock_post.return_value = mock_resp

        result = services.get_turmas_professor_disciplina(
            "000001",
            "5",
            ["9100001"],
        )

        mock_post.assert_called_once_with(
            "/api/v1/professores/000001/disciplina/5/turmas/",
            payload=["9100001"],
        )
        self.assertEqual(result, payload)


class BuscarProfessoresTitularesPorTurmaTest(SimpleTestCase):
    """Valida a integração da busca de professores titulares."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_monta_path_sem_filtros_e_retorna_lista(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Consulta o sidecar sem repassar RF ou data na query string."""
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = []
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "disciplinas_id": "89,90",
                "turma_id": 9100002,
            }
        ]

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002",
            datetime(2026, 7, 28),
            True,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/9100002/titulares/",
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        mock_componentes_turma.assert_called_once_with(
            "9100002",
            ["89"],
        )
        self.assertEqual(
            resultado,
            [
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "89",
                    "disciplinas_id": "89",
                    "nome_professor": "PROFESSOR",
                    "professor_rf": "000001",
                    "turma_id": 0,
                }
            ],
        )

    @patch("apps.professores.services._client")
    def test_normaliza_payload_invalido(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Retorna lista vazia quando o sidecar não devolve uma lista."""
        mock_client.json_or_none.return_value = None

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002",
            None,
            False,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/9100002/titulares/",
        )
        self.assertEqual(resultado, [])

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_concatena_territorio_e_experiencia_pedagogica(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Usa a experiência pedagógica do componente correspondente."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "PROJETO",
                "disciplina_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": 89,
                "desc_territorio_saber": "I - EDUCOMUNICACAO",
                "desc_experiencia_pedagogica": "HORTA PEDAGOGICA",
            }
        ]

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002",
            None,
            False,
        )

        self.assertEqual(
            resultado[0]["disciplina"],
            "I - EDUCOMUNICACAO - HORTA PEDAGOGICA",
        )

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_preserva_disciplina_sem_experiencia_pedagogica(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Preserva a disciplina quando a experiência é nula."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "PROJETO",
                "disciplina_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": "89",
                "desc_experiencia_pedagogica": None,
            }
        ]

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002",
            None,
            False,
        )

        self.assertEqual(resultado[0]["disciplina"], "PROJETO")

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_nao_envia_codigo_none_ao_servico_pedagogico(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Remove o identificador textual None antes da consulta pedagógica."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "PROJETO",
                "disciplina_id": "1522",
                "turma_id": 3022108,
            },
            {
                "professor_rf": "",
                "nome_professor": "",
                "disciplina": None,
                "disciplina_id": None,
                "turma_id": 9100002,
            },
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = []

        services.buscar_professores_titulares_por_turma(
            "3022108",
            None,
            True,
        )

        mock_componentes_turma.assert_called_once_with(
            "3022108",
            ["1522"],
        )

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_remove_componente_sem_dados_relevantes(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Não retorna o registro vazio produzido pelo agrupamento."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "",
                "nome_professor": "",
                "disciplina": None,
                "disciplina_id": None,
                "disciplinas_id": None,
                "turma_id": 0,
            }
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = []

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002",
            None,
            False,
        )

        self.assertEqual(resultado, [])


class BuscarProfessoresTitularesPorUeTest(SimpleTestCase):
    """Valida a integração da busca de titulares por UE."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_monta_path_e_preserva_componentes_sem_agrupamento(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Consulta a UE e preserva os componentes sem agrupamento."""
        response = MagicMock()
        payload = [
            {
                "professor_rf": "000001",
                "disciplina_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = payload
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = []

        resultado = services.buscar_professores_titulares_por_ue(
            "094765",
            datetime(2026, 8, 10),
            False,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/titulares/ue/094765/2026-08-10"
        )
        mock_client.json_or_none.assert_called_once_with(response)
        mock_componentes_api_eol.assert_called_once_with()
        mock_atribuicoes_territorio.assert_called_once_with(["9100002"])
        mock_componentes_turma.assert_called_once_with("9100002", ["89"])
        self.assertEqual(resultado, payload)

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_para_payload_invalido(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
    ) -> None:
        """Interrompe o processamento quando o payload é inválido."""
        mock_client.json_or_none.return_value = None

        resultado = services.buscar_professores_titulares_por_ue(
            "094765",
            datetime(2026, 8, 10),
            False,
        )

        self.assertEqual(resultado, [])
        mock_componentes_api_eol.assert_not_called()
        mock_atribuicoes_territorio.assert_not_called()

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_agrupa_componente_pelo_pai_quando_vigente(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Substitui o componente pelo pai quando a vigência está ativa."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_componentes_api_eol.return_value = [
            {
                "id_componente_curricular": 89,
                "id_componente_curricular_pai": 6,
            },
            {
                "id_componente_curricular": 6,
                "descricao": "CIENCIAS E BIOLOGIA",
            },
        ]
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": 6,
                "desc_territorio_saber": "III - ORIENTACAO",
                "desc_experiencia_pedagogica": "OUTRAS",
            }
        ]

        resultado = services.buscar_professores_titulares_por_ue(
            "094765",
            datetime(2026, 8, 10),
            False,
        )

        self.assertEqual(
            resultado[0]["disciplina"], "III - ORIENTACAO - OUTRAS"
        )
        self.assertEqual(resultado[0]["disciplina_id"], "6")
        mock_componentes_turma.assert_called_once_with("9100002", ["6"])

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_inclui_atribuicao_de_territorio_do_saber(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Substitui filhos pela atribuição de Território do Saber."""
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "800001",
                "disciplina_nome": "TERRITORIO DO SABER",
                "disciplinas_agrupadas_ids": [89],
                "nome_professor": "PROFESSOR TERRITORIO",
                "codigo_rf": "000002",
            }
        ]
        mock_componentes_turma.return_value = []

        resultado = services.buscar_professores_titulares_por_ue(
            "094765",
            datetime(2026, 8, 10),
            False,
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["disciplina"], "TERRITORIO DO SABER")
        self.assertEqual(resultado[0]["disciplina_id"], "800001")
        self.assertEqual(resultado[0]["disciplinas_id"], "800001")
        self.assertEqual(resultado[0]["turma_id"], 9100002)
        mock_componentes_turma.assert_called_once_with("9100002", ["800001"])


class BuscarProfessorTitularPorTurmaDisciplinaTest(SimpleTestCase):
    """Valida a busca singular de professor titular."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch("apps.professores.services._client")
    def test_monta_path_e_retorna_professor(
        self,
        mock_client: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Consulta o professor pela turma e componente curricular."""
        response = MagicMock()
        payload = {
            "professor_rf": "000001",
            "disciplina": "PROJETO",
            "disciplina_id": "89",
            "turma_id": 9100002,
        }
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = payload
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": 89,
                "desc_territorio_saber": "III - ORIENTACAO DE ESTUDOS",
                "desc_experiencia_pedagogica": "OUTRAS",
            }
        ]

        resultado = services.buscar_professor_titular_por_turma_disciplina(
            "9100002",
            "89",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/titular/turmas/9100002/"
            "componentes-curriculares/89"
        )
        mock_client.json_or_none.assert_called_once_with(response)
        mock_componentes_turma.assert_called_once_with("9100002", ["89"])
        assert resultado is not None
        self.assertEqual(resultado["disciplina"], "OUTRAS")

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch("apps.professores.services._client")
    def test_preserva_disciplina_quando_experiencia_pedagogica_for_nula(
        self,
        mock_client: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Preserva o nome original quando não existe experiência."""
        mock_client.json_or_none.return_value = {
            "disciplina": "PROJETO",
            "disciplina_id": "89",
        }
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": "89",
                "desc_territorio_saber": "III - ORIENTACAO DE ESTUDOS",
                "desc_experiencia_pedagogica": None,
            }
        ]

        resultado = services.buscar_professor_titular_por_turma_disciplina(
            "9100002",
            "89",
        )

        assert resultado is not None
        self.assertEqual(resultado["disciplina"], "PROJETO")

    @patch("apps.professores.services._client")
    def test_retorna_none_para_payload_incompativel(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Normaliza resposta vazia ou incompatível para ausência."""
        mock_client.json_or_none.return_value = []

        resultado = services.buscar_professor_titular_por_turma_disciplina(
            "9100002",
            "89",
        )

        self.assertIsNone(resultado)

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch("apps.professores.services._client")
    def test_retorna_professor_de_territorio_do_saber(
        self,
        mock_client: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
    ) -> None:
        """Converte a atribuição pedagógica para o contrato interno."""
        mock_atribuicoes_territorio.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "800001",
                "disciplina_nome": "TERRITORIO DO SABER",
                "disciplinas_agrupadas_ids": [89, 90],
                "nome_professor": "PROFESSOR TERRITORIO",
                "codigo_rf": "000002",
            }
        ]

        resultado = services.buscar_professor_titular_por_turma_disciplina(
            "9100002",
            "800001",
        )

        self.assertEqual(
            resultado,
            {
                "disciplina": "TERRITORIO DO SABER",
                "disciplina_id": "800001",
                "disciplinas_id": "89,90",
                "nome_professor": "PROFESSOR TERRITORIO",
                "professor_rf": "000002",
                "turma_id": 9100002,
            },
        )
        mock_atribuicoes_territorio.assert_called_once_with("9100002")
        mock_client.get.assert_not_called()

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch("apps.professores.services._client")
    def test_retorna_none_quando_territorio_nao_e_encontrado(
        self,
        mock_client: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
    ) -> None:
        """Não consulta o sidecar de professores para território ausente."""
        mock_atribuicoes_territorio.return_value = []

        resultado = services.buscar_professor_titular_por_turma_disciplina(
            "9100002",
            "800001",
        )

        self.assertIsNone(resultado)
        mock_client.get.assert_not_called()


class BuscarProfessoresTitularesPorTurmasTest(SimpleTestCase):
    """Valida a integração da busca de titulares por várias turmas."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_envia_lista_na_query_e_retorna_professores(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Consulta titulares usando parâmetros repetidos por turma."""
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = [
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "disciplinas_id": "89",
                "turma_id": 9100002,
            }
        ]
        mock_componentes_api_eol.return_value = []
        mock_atribuicoes_territorio.return_value = []
        mock_componentes_turma.return_value = [
            {
                "componente_codigo": 89,
                "desc_territorio_saber": "III - ORIENTACAO",
                "desc_experiencia_pedagogica": "OUTRAS",
            }
        ]

        resultado = services.buscar_professores_titulares_por_turmas(
            ["9100002", "9100003"]
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/titulares/",
            params={"codigos_turmas": [9100002, 9100003]},
        )
        mock_client.json_or_none.assert_called_once_with(response)
        mock_componentes_api_eol.assert_called_once_with()
        mock_atribuicoes_territorio.assert_called_once_with(
            ["9100002", "9100003"]
        )
        self.assertEqual(resultado[0]["professor_rf"], "000001")
        self.assertEqual(
            resultado[0]["disciplina"], "III - ORIENTACAO - OUTRAS"
        )
        self.assertEqual(resultado[0]["disciplina_id"], "89")
        self.assertEqual(resultado[0]["disciplinas_id"], "89")

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_retorna_vazio_sem_consultar_complementos_para_payload_invalido(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
    ) -> None:
        """Interrompe o processamento quando o sidecar não retorna lista."""
        mock_client.json_or_none.return_value = {"detail": "erro"}

        resultado = services.buscar_professores_titulares_por_turmas(
            ["9100002"]
        )

        self.assertEqual(resultado, [])
        mock_componentes_api_eol.assert_not_called()
        mock_atribuicoes_territorio.assert_not_called()

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turmas_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_nao_duplica_atribuicoes_de_territorio_entre_turmas(
        self,
        mock_client: MagicMock,
        mock_componentes_api_eol: MagicMock,
        mock_atribuicoes_territorio: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Mantém cada atribuição de território somente em sua turma."""
        mock_client.json_or_none.return_value = []
        mock_componentes_api_eol.return_value = []
        mock_componentes_turma.return_value = []
        mock_atribuicoes_territorio.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "800001",
                "disciplina_nome": "TERRITORIO 1",
                "disciplinas_agrupadas_ids": [],
                "nome_professor": "PROFESSOR 1",
                "codigo_rf": "000001",
            },
            {
                "codigo_turma": "9100003",
                "disciplina_id": "800002",
                "disciplina_nome": "TERRITORIO 2",
                "disciplinas_agrupadas_ids": [],
                "nome_professor": "PROFESSOR 2",
                "codigo_rf": "000002",
            },
        ]

        resultado = services.buscar_professores_titulares_por_turmas(
            ["9100002", "9100003"]
        )

        self.assertEqual(len(resultado), 2)
        self.assertEqual(
            {item["professor_rf"] for item in resultado},
            {"000001", "000002"},
        )


class VerificarVigenciaComponentePaiTest(SimpleTestCase):
    """Valida a vigência do componente curricular pai."""

    def test_retorna_true_quando_pai_nao_possui_vigencia(self) -> None:
        """Considera vigente o componente pai sem data de vigência."""
        componentes: list[dict[str, Any]] = [
            {
                "id_componente_curricular": 89,
                "id_componente_curricular_pai": 10,
            },
            {
                "id_componente_curricular": 10,
                "id_componente_curricular_pai": None,
                "vigencia": None,
            },
        ]

        resultado = services._verificar_vigencia_componente_pai(
            componentes,
            "89",
            datetime(2026, 7, 28),
        )

        self.assertTrue(resultado)


class TratarAgrupamentoComponentesProfessorTest(SimpleTestCase):
    """Valida o agrupamento dos componentes de professores titulares."""

    def test_remove_filhos_e_adiciona_atribuicao_territorio(self) -> None:
        """Substitui componentes filhos pela atribuição agrupadora."""
        componentes_professor = [
            {
                "professor_rf": "000001",
                "disciplina": "CIENCIAS",
                "disciplina_id": "90",
                "turma_id": 9100002,
            },
            {
                "professor_rf": "000001",
                "disciplina": "MATEMATICA",
                "disciplina_id": "100",
                "turma_id": 9100002,
            },
        ]
        atribuicoes_territorio = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "800000",
                "disciplina_nome": "TERRITORIO DO SABER",
                "disciplinas_agrupadas_ids": [89, 90],
                "nome_professor": "PROFESSOR TERRITORIO",
                "codigo_rf": "000002",
            }
        ]

        resultado = services._tratar_agrupamento_componentes_professor(
            "9100002",
            componentes_professor,
            atribuicoes_territorio,
        )

        self.assertEqual(
            resultado,
            [
                componentes_professor[1],
                {
                    "disciplina": "TERRITORIO DO SABER",
                    "disciplina_id": "800000",
                    "disciplinas_id": "800000",
                    "nome_professor": "PROFESSOR TERRITORIO",
                    "professor_rf": "000002",
                    "turma_id": 9100002,
                },
            ],
        )

    def test_preserva_componentes_quando_lista_agrupada_e_nula(self) -> None:
        """Trata a ausência de disciplinas agrupadas como lista vazia."""
        componente = {
            "disciplina_id": "90",
            "turma_id": 9100002,
        }
        atribuicao = {
            "codigo_turma": "9100002",
            "disciplina_id": "800000",
            "disciplina_nome": "TERRITORIO DO SABER",
            "disciplinas_agrupadas_ids": None,
            "nome_professor": "PROFESSOR",
            "codigo_rf": "000001",
        }

        resultado = services._tratar_agrupamento_componentes_professor(
            ["9100002"],
            [componente],
            [atribuicao],
        )

        self.assertEqual(resultado[0], componente)
        self.assertEqual(resultado[1]["disciplina_id"], "800000")


class MontarComponenteProfessorAgrupadoTest(SimpleTestCase):
    """Valida a conversão do componente do professor para o componente pai."""

    def test_usa_codigo_e_descricao_do_componente_pai(self) -> None:
        """Substitui disciplina filha pelos dados da disciplina pai."""
        resultado = services._montar_componente_professor_agrupado(
            {
                "disciplina": "CIENCIAS FILHA",
                "disciplina_id": "90",
                "nome_professor": "PROFESSOR",
                "professor_rf": "000001",
                "turma_id": 9100002,
            },
            [
                {
                    "id_componente_curricular": 90,
                    "id_componente_curricular_pai": 89,
                    "descricao": "CIENCIAS FILHA",
                },
                {
                    "id_componente_curricular": 89,
                    "id_componente_curricular_pai": None,
                    "descricao": "CIENCIAS",
                },
            ],
        )

        self.assertEqual(
            resultado,
            {
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "disciplinas_id": None,
                "nome_professor": "PROFESSOR",
                "professor_rf": "000001",
                "turma_id": 9100002,
            },
        )

    def test_preserva_disciplina_sem_componente_pai(self) -> None:
        """Mantém os dados originais quando não existe componente pai."""
        resultado = services._montar_componente_professor_agrupado(
            {
                "disciplina": "MATEMATICA",
                "disciplina_id": "100",
                "nome_professor": "PROFESSOR",
                "professor_rf": "000001",
            },
            [
                {
                    "id_componente_curricular": 100,
                    "id_componente_curricular_pai": None,
                    "descricao": "MATEMATICA",
                }
            ],
        )

        self.assertEqual(resultado["disciplina"], "MATEMATICA")
        self.assertEqual(resultado["disciplina_id"], "100")


class AgruparComponentesRetornoTest(SimpleTestCase):
    """Valida o agrupamento final dos componentes de professores."""

    def test_agrupa_ids_e_valores_distintos_no_contrato_final(self) -> None:
        """Reproduz o agrupamento por disciplina e RF do .NET."""
        resultado = services._agrupar_componentes_retorno(
            [
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "89",
                    "nome_professor": "PROFESSOR",
                    "professor_rf": "000001",
                },
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "90",
                    "nome_professor": "Não há professor titular.",
                    "professor_rf": "000001",
                },
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "91",
                    "nome_professor": "OUTRO PROFESSOR",
                    "professor_rf": "000002",
                },
            ]
        )

        self.assertEqual(
            resultado,
            [
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "89",
                    "disciplinas_id": "89,90",
                    "nome_professor": "PROFESSOR",
                    "professor_rf": "000001",
                    "turma_id": 0,
                },
                {
                    "disciplina": "CIENCIAS",
                    "disciplina_id": "91",
                    "disciplinas_id": "91",
                    "nome_professor": "OUTRO PROFESSOR",
                    "professor_rf": "000002",
                    "turma_id": 0,
                },
            ],
        )

    def test_retorna_lista_vazia_sem_componentes(self) -> None:
        """Equivale ao Select vazio do retorno .NET."""
        self.assertEqual(services._agrupar_componentes_retorno([]), [])


class VerificarVigenciaComponentePaiComplementarTest(SimpleTestCase):
    """Complementa os cenários de vigência do componente pai."""

    def test_retorna_true_quando_pai_esta_vigente_na_data(self) -> None:
        """Aceita vigência igual ou posterior à data de referência."""
        componentes: list[dict[str, Any]] = [
            {
                "id_componente_curricular": 89,
                "id_componente_curricular_pai": 10,
            },
            {
                "id_componente_curricular": 10,
                "vigencia": "2026-12-31T00:00:00",
            },
        ]

        resultado = services._verificar_vigencia_componente_pai(
            componentes,
            "89",
            datetime(2026, 7, 28),
        )

        self.assertTrue(resultado)

    def test_retorna_false_quando_vigencia_do_pai_expirou(self) -> None:
        """Rejeita pai com vigência anterior à data de referência."""
        componentes: list[dict[str, Any]] = [
            {
                "id_componente_curricular": 89,
                "id_componente_curricular_pai": 10,
            },
            {
                "id_componente_curricular": 10,
                "vigencia": "2026-07-27T23:59:59",
            },
        ]

        resultado = services._verificar_vigencia_componente_pai(
            componentes,
            "89",
            datetime(2026, 7, 28),
        )

        self.assertFalse(resultado)

    def test_retorna_false_quando_componente_ou_pai_nao_existe(self) -> None:
        """Rejeita listas que não permitem localizar o componente pai."""
        sem_componente = services._verificar_vigencia_componente_pai(
            [],
            "89",
            datetime(2026, 7, 28),
        )
        sem_pai = services._verificar_vigencia_componente_pai(
            [
                {
                    "id_componente_curricular": 89,
                    "id_componente_curricular_pai": 10,
                }
            ],
            "89",
            datetime(2026, 7, 28),
        )

        self.assertFalse(sem_componente)
        self.assertFalse(sem_pai)

    def test_usa_data_atual_quando_referencia_e_nula(self) -> None:
        """Aplica a data atual quando não há data de referência."""
        componentes: list[dict[str, Any]] = [
            {
                "id_componente_curricular": 89,
                "id_componente_curricular_pai": 10,
            },
            {
                "id_componente_curricular": 10,
                "vigencia": "9999-12-31T00:00:00",
            },
        ]

        resultado = services._verificar_vigencia_componente_pai(
            componentes,
            "89",
            None,
        )

        self.assertTrue(resultado)


class MontarTurmasAtribuidasProfessorTest(SimpleTestCase):
    """Valida turmas atribuídas por etapa e tipo de UE."""

    def _ancora(
        self,
        codigo_turma: int | None,
        codigo_ue: str | None,
    ) -> dict:
        """Cria uma âncora de teste para simular a resposta da API."""
        return {
            "codigo_turma": codigo_turma,
            "codigo_serie_grade": None,
            "codigo_unidade_educacao": codigo_ue,
            "data_atribuicao": "02/01/2024 00:00:00",
            "data_disponibilizacao": None,
        }

    def _turma(self, codigo: int) -> dict:
        """Cria uma turma de teste para simular a resposta da API."""
        return {
            "codigo": codigo,
            "nome_turma": "1A",
            "ano_letivo": 2024,
            "ano": "1",
            "tipo_turma": 1,
            "ue_codigo": "000102",
            "modalidade": "Fundamental",
            "codigo_modalidade": 5,
            "semestre": 0,
            "ensino_especial": False,
            "serie_ensino": "1 ANO",
            "codigo_serie_ensino": 10,
            "situacao": "A",
            "extinta": False,
            "data_inicio_turma": "2024-02-01",
            "data_fim": None,
            "duracao_turno": 5,
            "tipo_turno": 4,
            "codigo_etapa_ensino": 4,
            "codigo_ciclo_ensino": 2,
        }

    def _ue(self, codigo: str) -> dict:
        """Cria uma unidade de ensino de teste."""
        return {
            "codigo": codigo,
            "nome": "EMEF TESTE",
            "nomeExibicao": "EMEF T.",
            "tipoUnidade": "EMEF",
            "codigoTipoUnidadeEducacao": 1,
            "codigoTipoEscola": 1,
            "siglaTipoEscola": "EMEF",
            "codigoDRE": "100001",
            "nomeDRE": "DRE TESTE",
            "siglaDRE": "DRE-T",
        }

    @patch.object(
        services.institucional_services, "get_ues_recorte_fund_medio"
    )
    @patch.object(
        services.pedagogico_services, "get_turmas_recorte_fund_medio_eja"
    )
    @patch.object(services, "get_turmas_professor")
    def test_interseccao_monta_contrato_legado(
        self,
        mock_ancora: MagicMock,
        mock_ped: MagicMock,
        mock_inst: MagicMock,
    ) -> None:
        """Mapeia campos quando turma e UE passam nos dois recortes."""
        mock_ancora.return_value = [self._ancora(9100006, "000102")]
        mock_ped.return_value = [self._turma(9100006)]
        mock_inst.return_value = [self._ue("000102")]

        result = services.montar_turmas_atribuidas_professor("000001")

        mock_ped.assert_called_once_with([9100006])
        mock_inst.assert_called_once_with(["000102"])
        self.assertEqual(len(result), 1)
        linha = result[0]
        self.assertEqual(linha["cod_turma"], 9100006)
        self.assertEqual(linha["cod_escola"], "000102")
        self.assertEqual(linha["cod_ue"], "000102")
        self.assertEqual(linha["modalidade"], "Fundamental")
        self.assertEqual(linha["cod_modalidade"], 5)
        self.assertEqual(linha["cod_dre"], "100001")
        self.assertEqual(linha["dre_abrev"], "DRE-T")
        self.assertEqual(linha["tipo_escola"], "EMEF")
        self.assertEqual(linha["cod_tipo_escola"], 1)
        self.assertEqual(linha["data_inicio_turma"], "2024-02-01T00:00:00")

    @patch.object(
        services.institucional_services, "get_ues_recorte_fund_medio"
    )
    @patch.object(
        services.pedagogico_services, "get_turmas_recorte_fund_medio_eja"
    )
    @patch.object(services, "get_turmas_professor")
    def test_exclui_turma_fora_do_recorte_de_etapa(
        self,
        mock_ancora: MagicMock,
        mock_ped: MagicMock,
        mock_inst: MagicMock,
    ) -> None:
        """Remove a âncora cuja turma não voltou do recorte pedagógico."""
        mock_ancora.return_value = [
            self._ancora(9100006, "000102"),
            self._ancora(9999999, "000102"),
        ]
        mock_ped.return_value = [self._turma(9100006)]
        mock_inst.return_value = [self._ue("000102")]

        result = services.montar_turmas_atribuidas_professor("000001")

        self.assertEqual([linha["cod_turma"] for linha in result], [9100006])

    @patch.object(
        services.institucional_services, "get_ues_recorte_fund_medio"
    )
    @patch.object(
        services.pedagogico_services, "get_turmas_recorte_fund_medio_eja"
    )
    @patch.object(services, "get_turmas_professor")
    def test_exclui_ue_fora_do_recorte_de_tipo(
        self,
        mock_ancora: MagicMock,
        mock_ped: MagicMock,
        mock_inst: MagicMock,
    ) -> None:
        """Remove a âncora cuja UE não voltou do recorte institucional."""
        mock_ancora.return_value = [self._ancora(9100006, "000102")]
        mock_ped.return_value = [self._turma(9100006)]
        mock_inst.return_value = []

        result = services.montar_turmas_atribuidas_professor("000001")

        self.assertEqual(result, [])

    @patch.object(
        services.institucional_services, "get_ues_recorte_fund_medio"
    )
    @patch.object(
        services.pedagogico_services, "get_turmas_recorte_fund_medio_eja"
    )
    @patch.object(services, "get_turmas_professor")
    def test_ignora_ancora_de_programa_sem_codigo_turma(
        self,
        mock_ancora: MagicMock,
        mock_ped: MagicMock,
        mock_inst: MagicMock,
    ) -> None:
        """Âncora de programa (sem codigo_turma) não é consultada nem sai."""
        mock_ancora.return_value = [self._ancora(None, "000102")]

        result = services.montar_turmas_atribuidas_professor("000001")

        self.assertEqual(result, [])
        mock_ped.assert_not_called()
        mock_inst.assert_not_called()

    @patch.object(services, "get_turmas_professor")
    def test_ancora_vazia_retorna_vazio(
        self,
        mock_ancora: MagicMock,
    ) -> None:
        """Sem âncora não há orquestração."""
        mock_ancora.return_value = None

        result = services.montar_turmas_atribuidas_professor("000001")

        self.assertEqual(result, [])


class GetCodigosTurmasHistoricasProfessorTest(SimpleTestCase):
    """Valida a extração de códigos de turmas históricas do professor."""

    @patch.object(services._client, "get")
    def test_chama_path_e_retorna_lista(self, mock_get: MagicMock) -> None:
        """Extrai códigos dos objetos retornados pelo endpoint canônico."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'[{"codigo":2822488},{"codigo":2822517}]'
        mock_resp.json.return_value = [
            {"codigo": 2822488},
            {"codigo": 2822517},
        ]
        mock_get.return_value = mock_resp

        result = services.get_codigos_turmas_historicas_professor(
            2025,
            "7483147",
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/turmas/anos-letivos/2025/professor/"
            "7483147/turmas-historicas-geral/"
        )
        self.assertEqual(result, [2822488, 2822517])

    @patch.object(services._client, "get")
    def test_aceita_lista_de_codigos_inteiros(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Aceita o formato simplificado retornado pelo sidecar."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[2822498]"
        mock_resp.json.return_value = [2822498]
        mock_get.return_value = mock_resp

        result = services.get_codigos_turmas_historicas_professor(
            2025,
            "8057826",
        )

        self.assertEqual(result, [2822498])

    @patch.object(services._client, "get")
    def test_remove_codigos_duplicados_preservando_ordem(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Remove códigos repetidos sem alterar a ordem da resposta."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[{}]"
        mock_resp.json.return_value = [
            {"codigo": 2822517},
            {"codigo": 2822488},
            {"codigo": 2822517},
        ]
        mock_get.return_value = mock_resp

        result = services.get_codigos_turmas_historicas_professor(
            2025,
            "7483147",
        )

        self.assertEqual(result, [2822517, 2822488])

    @patch.object(services._client, "get")
    def test_404_retorna_lista_vazia(self, mock_get: MagicMock) -> None:
        """Trata 404 do professores como ausência de turmas."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        result = services.get_codigos_turmas_historicas_professor(
            2025,
            "8381399",
        )

        self.assertEqual(result, [])
        mock_resp.raise_for_status.assert_not_called()

    @patch.object(services._client, "get")
    def test_rejeita_item_sem_codigo_inteiro(
        self,
        mock_get: MagicMock,
    ) -> None:
        """Erra quando um item não contém código inteiro."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'[{"codigo":"2822488"}]'
        mock_resp.json.return_value = [{"codigo": "2822488"}]
        mock_get.return_value = mock_resp

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve conter códigos inteiros.",
        ):
            services.get_codigos_turmas_historicas_professor(
                2025,
                "7483147",
            )

    @patch.object(services._client, "get")
    def test_rejeita_resposta_sem_corpo(self, mock_get: MagicMock) -> None:
        """Erra quando o professores responde sem uma lista JSON."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        with self.assertRaisesMessage(
            ValueError,
            "Resposta de turmas históricas deve conter códigos inteiros.",
        ):
            services.get_codigos_turmas_historicas_professor(
                2025,
                "7483147",
            )


class GetTurmasAtribuidasProfessorEscolaTest(SimpleTestCase):
    """Valida turmas atribuídas ao professor na escola."""

    @patch("apps.professores.services._client")
    def test_chama_path_e_mapeia_retorno(self, mock_client: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": 9100001,
                "nome_turma": "1A",
                "componente_curricular": "Matemática",
                "data_inicio_turma": "2026-02-03",
                "data_fim_atribuicao": None,
                "ano": "1",
                "etapa_ensino": 1,
            },
        ]

        result = services.get_turmas_atribuidas_professor_escola(
            "000001",
            "000103",
            2026,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/escolas/000103/turmas/anos_letivos/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigoTurma": 9100001,
                    "nomeTurma": "1A",
                    "componenteCurricular": "Matemática",
                    "dataInicioAtribuicao": "2026-02-03",
                    "dataFimAtribuicao": None,
                    "ano": "1",
                    "etapaEnsino": 1,
                },
            ],
        )

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_sidecar_nao_retorna_lista(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = {"erro": "contrato"}

        result = services.get_turmas_atribuidas_professor_escola(
            "000001",
            "000103",
            2026,
        )

        self.assertEqual(result, [])


class GetTurmasAtribuidasProfessoresEscolaTest(SimpleTestCase):
    """Valida turmas atribuídas aos professores na escola."""

    @patch("apps.professores.services._client")
    def test_chama_path_e_mapeia_retorno(self, mock_client: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": 9100001,
                "nome_turma": "1A",
                "componente_curricular": "Matemática",
                "data_inicio_turma": "2026-02-03",
                "data_fim_atribuicao": None,
                "ano": "1",
                "etapa_ensino": 1,
            },
        ]

        result = services.get_turmas_atribuidas_professores_escola(
            "000103",
            2026,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/escolas/000103/turmas/anos_letivos/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigoTurma": 9100001,
                    "nomeTurma": "1A",
                    "componenteCurricular": "Matemática",
                    "dataInicioAtribuicao": "2026-02-03",
                    "dataFimAtribuicao": None,
                    "ano": "1",
                    "etapaEnsino": 1,
                },
            ],
        )

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_sidecar_nao_retorna_lista(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = None

        result = services.get_turmas_atribuidas_professores_escola(
            "000103",
            2026,
        )

        self.assertEqual(result, [])


class GetProfessoresEscolaTest(SimpleTestCase):
    """Valida professores atribuídos à escola."""

    @patch("apps.professores.services._client")
    def test_chama_path_e_mapeia_retorno(self, mock_client: MagicMock) -> None:
        """Retorna professores no contrato do domínio."""
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = [
            {
                "codigo_rf": 7900003,
                "nome": "Ana Silva",
                "cargo": "PROFESSOR",
                "cpf": "12345678900",
                "data_inicio_exercicio": "2020-01-01",
            }
        ]

        result = services.get_professores_escola("000103", 2026)

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/escolas/000103/professores/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": 7900003,
                    "nome": "Ana Silva",
                    "cargo": "PROFESSOR",
                    "cpf": "12345678900",
                    "data_inicio_exercicio": "2020-01-01",
                }
            ],
        )

    @patch("apps.professores.services._client")
    def test_sem_ano_usa_zero(self, mock_client: MagicMock) -> None:
        """Consulta o ano padrão usado pelo contrato legado."""
        mock_client.json_or_none.return_value = []

        result = services.get_professores_escola("000103")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/escolas/000103/professores/0/"
        )
        self.assertEqual(result, [])


class GetTurmasAtribuidasProfessorTest(SimpleTestCase):
    """Valida turmas atribuídas ao professor por ano letivo."""

    @patch("apps.professores.services._client")
    def test_chama_path_e_mapeia_retorno(self, mock_client: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": 9100001,
                "nome_turma": "1A",
                "componente_curricular": "Matemática",
                "data_inicio_turma": "2026-02-03",
                "data_disponibilizacao": None,
                "ano": "1",
                "etapa_ensino": 1,
            },
        ]

        result = services.get_turmas_atribuidas_professor("000001", 2026)

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/anos_letivos/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigoTurma": 9100001,
                    "nomeTurma": "1A",
                    "componenteCurricular": "Matemática",
                    "dataInicioAtribuicao": "2026-02-03",
                    "dataFimAtribuicao": None,
                    "ano": "1",
                    "etapaEnsino": 1,
                },
            ],
        )

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_sidecar_nao_retorna_lista(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = {"erro": "contrato"}

        result = services.get_turmas_atribuidas_professor("000001", 2026)

        self.assertEqual(result, [])


class GetAdministradoresSgpEscolaTest(SimpleTestCase):
    """Valida serviço de administradores SGP da escola."""

    @patch("apps.professores.services._client")
    def test_chama_endpoint_correto(self, mock_client: MagicMock) -> None:
        """Valida path do sidecar."""
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = ["7821972", "7980302"]

        result = services.get_administradores_sgp_escola("000103")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/escolas/000103/administrador-sgp"
        )
        self.assertEqual(result, ["7821972", "7980302"])

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_sidecar_retorna_none(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna [] quando sidecar retorna None."""
        mock_client.json_or_none.return_value = None

        result = services.get_administradores_sgp_escola("000103")

        self.assertEqual(result, [])

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_sidecar_retorna_dict(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna [] quando sidecar retorna objeto ao invés de array."""
        mock_client.json_or_none.return_value = {"erro": "contrato"}

        result = services.get_administradores_sgp_escola("000103")

        self.assertEqual(result, [])

    @patch("apps.professores.services._client")
    def test_filtra_valores_vazios(self, mock_client: MagicMock) -> None:
        """Remove valores None e vazios da lista."""
        mock_client.json_or_none.return_value = [
            "7821972",
            None,
            "",
            "7980302",
        ]

        result = services.get_administradores_sgp_escola("000103")

        self.assertEqual(result, ["7821972", "7980302"])

    @patch("apps.professores.services._client")
    def test_converte_para_string(self, mock_client: MagicMock) -> None:
        """Converte RFs numéricos para string."""
        mock_client.json_or_none.return_value = [7821972, 7980302]

        result = services.get_administradores_sgp_escola("000103")

        self.assertEqual(result, ["7821972", "7980302"])
        self.assertIsInstance(result[0], str)


class GetDisciplinasFuncionarioTurmaTest(SimpleTestCase):
    """Valida seleção de fonte por abrangência."""

    @patch("apps.professores.services.pedagogico_services")
    def test_abrangencia_sme_consulta_componentes_da_turma(
        self,
        mock_pedagogico: MagicMock,
    ) -> None:
        mock_pedagogico.get_componentes_por_lista_turmas.return_value = [
            {
                "codigo": 512,
                "codigo_componente_curricular_pai": None,
                "descricao": "Arte",
                "tipo_escola": "1",
                "territorio_saber": False,
            }
        ]

        result = services.get_disciplinas_funcionario_turma(
            "000001",
            "perfil-sme",
            "3020465",
            abrangencia=6,
        )

        mock_pedagogico.get_componentes_por_lista_turmas.assert_called_once_with(
            ["3020465"],
            adicionar_componentes_planejamento=False,
        )
        mock_pedagogico.get_componentes_turma_funcionario.assert_not_called()
        self.assertEqual(result[0]["codigo"], 512)
        self.assertEqual(result[0]["descricao"], "Arte")

    @patch("apps.professores.services.pedagogico_services")
    def test_abrangencia_professor_consulta_componentes_do_funcionario(
        self,
        mock_pedagogico: MagicMock,
    ) -> None:
        mock_pedagogico.get_componentes_turma_funcionario.return_value = []

        services.get_disciplinas_funcionario_turma(
            "000001",
            "perfil-professor",
            "3020465",
            abrangencia=2,
        )

        mock_pedagogico.get_componentes_turma_funcionario.assert_called_once_with(
            codigo_turma="3020465",
            login="000001",
            id_perfil="perfil-professor",
            agrupa_componente_curricular=False,
        )
        mock_pedagogico.get_componentes_por_lista_turmas.assert_not_called()

    @patch("apps.professores.services._client")
    def test_abrangencia_ue_consulta_disciplinas_por_vinculo(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_resp = MagicMock()
        mock_client.get.return_value = mock_resp
        mock_client.json_or_none.return_value = []

        result = services.get_disciplinas_funcionario_turma(
            "000001",
            "perfil-ue",
            "3020465",
            abrangencia=1,
            cargos=[1, 2],
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/funcionarios/000001/turmas/3020465/"
            "disciplinas-atribuidas-ue/",
            params={"cargos": ["1", "2"]},
        )
        self.assertEqual(result, [])


class GetAbrangenciaFuncionarioPerfilTest(SimpleTestCase):
    """Valida o switch de turmas por abrangência."""

    @patch("apps.professores.services._client")
    def test_abrangencia_dre_usa_turmas_atribuidas_ue(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = []

        data = services.get_abrangencia_funcionario_perfil(
            "000001",
            "perfil-dre",
            abrangencia=4,
            cargos=[3239],
            funcoes=[10],
            grupo=5,
            dre_codigo="100001",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/funcionarios/000001/turmas-atribuidas-ue/",
            params={"codigo_dre": "100001"},
        )
        self.assertEqual(data, [])


class CoberturaRegrasAtribuicaoStagedTest(SimpleTestCase):
    """Cobre branches das novas regras de atribuição."""

    def test_recorrencia_sem_ticks_retorna_lista_vazia(self) -> None:
        """Não consulta dependências quando não há recorrências."""
        resultado = services.verificar_recorrencia_datas(
            "000001", "9100002", "89", []
        )

        self.assertEqual(resultado, [])

    def test_atribuicao_sem_datas_nao_sobrepoe_periodo(self) -> None:
        """Rejeita atribuição sem limites de vigência."""
        resultado = services._atribuicao_sobrepoe_periodo(
            {"codigo_turma": "9100002", "disciplina_id": "89"},
            "9100002",
            "89",
            set(),
            datetime(2026, 7, 1),
            datetime(2026, 7, 31),
        )

        self.assertFalse(resultado)

    def test_parse_converte_date_e_rejeita_string_invalida(self) -> None:
        """Cobre valores de data e texto inválido no parser interno."""
        self.assertEqual(
            services._parse_datetime_atribuicao(date(2026, 7, 28)),
            datetime(2026, 7, 28),
        )
        self.assertIsNone(services._parse_datetime_atribuicao("invalida"))

    def test_vigencia_rejeita_componente_sem_pai(self) -> None:
        """Retorna falso quando a disciplina não possui componente pai."""
        resultado = services._verificar_vigencia_componente_pai(
            [
                {
                    "id_componente_curricular": 89,
                    "id_componente_curricular_pai": None,
                }
            ],
            "89",
            datetime(2026, 7, 28),
        )

        self.assertFalse(resultado)

    @patch("apps.professores.services._client")
    def test_busca_regular_sem_ano_e_payload_invalido(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Usa a rota geral e normaliza resposta que não seja lista."""
        mock_client.json_or_none.return_value = None

        resultado = services._get_atribuicoes_professor_turma_disciplina(
            "000001", "89", 0
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/anos_letivos/"
        )
        self.assertEqual(resultado, [])


class CoberturaBuscaProfessoresTitularesStagedTest(SimpleTestCase):
    """Cobre os branches de agrupamento dos professores titulares."""

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_trata_atribuicao_de_territorio_do_saber(
        self,
        mock_client: MagicMock,
        mock_componentes: MagicMock,
        mock_atribuicoes: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Substitui componente filho pela atribuição territorial."""
        mock_client.json_or_none.return_value = [
            {
                "disciplina": "CIENCIAS FILHA",
                "disciplina_id": "90",
                "nome_professor": "PROFESSOR",
                "professor_rf": "000001",
                "turma_id": 9100002,
            }
        ]
        mock_componentes.return_value = []
        mock_componentes_turma.return_value = []
        mock_atribuicoes.return_value = [
            {
                "codigo_turma": "9100002",
                "disciplina_id": "800000",
                "disciplina_nome": "TERRITORIO DO SABER",
                "disciplinas_agrupadas_ids": [90],
                "nome_professor": "PROFESSOR TERRITORIO",
                "codigo_rf": "000002",
            }
        ]

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002", None, False
        )

        self.assertEqual(resultado[0]["disciplina"], "TERRITORIO DO SABER")
        self.assertEqual(resultado[0]["disciplina_id"], "800000")
        self.assertEqual(resultado[0]["disciplinas_id"], "800000")

    @patch(
        "apps.professores.services.pedagogico_services."
        "get_turma_componentes_turma"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_professores_turma_territorio_saber"
    )
    @patch(
        "apps.professores.services.pedagogico_services."
        "get_componentes_api_eol"
    )
    @patch("apps.professores.services._client")
    def test_preserva_componentes_quando_nao_agrupa(
        self,
        mock_client: MagicMock,
        mock_componentes: MagicMock,
        mock_atribuicoes: MagicMock,
        mock_componentes_turma: MagicMock,
    ) -> None:
        """Usa os componentes originais quando nenhuma regra agrupa."""
        mock_client.json_or_none.return_value = [
            {
                "disciplina": "MATEMATICA",
                "disciplina_id": "100",
                "nome_professor": "PROFESSOR",
                "professor_rf": "000001",
                "turma_id": 9100002,
            }
        ]
        mock_componentes.return_value = []
        mock_atribuicoes.return_value = []
        mock_componentes_turma.return_value = []

        resultado = services.buscar_professores_titulares_por_turma(
            "9100002", None, False
        )

        self.assertEqual(resultado[0]["disciplina"], "MATEMATICA")
        self.assertEqual(resultado[0]["disciplinas_id"], "100")


class GetAbrangenciaFuncionarioPerfilComplementarTest(SimpleTestCase):
    """Complementa os cenários de abrangência por perfil."""

    @patch("apps.professores.services._client")
    def test_abrangencia_ue_nao_envia_dre(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = []

        services.get_abrangencia_funcionario_perfil(
            "000001",
            "perfil-ue",
            abrangencia=1,
            cargos=[3239],
            dre_codigo="100001",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/funcionarios/000001/turmas-atribuidas-ue/",
            params={"cargos": ["3239"]},
        )

    @patch("apps.professores.services._client")
    def test_sem_abrangencia_faz_proxy_do_perfil(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.json_or_none.return_value = {
            "abrangencia": None,
            "dres": [],
        }

        data = services.get_abrangencia_funcionario_perfil(
            "000001",
            "perfil-x",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/funcionarios/000001/perfis/perfil-x/turmas/"
        )
        self.assertIsNone(data["abrangencia"])

    @patch("apps.professores.services._client")
    @patch("apps.professores.services.montar_turmas_atribuidas_professor")
    def test_abrangencia_professor_usa_composicao_enriquecida(
        self,
        mock_montar_turmas: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        mock_montar_turmas.return_value = [
            {
                "cod_dre": "100005",
                "dre": "DIRETORIA REGIONAL FICTICIA",
                "dre_abrev": "DRE - X",
                "cod_escola": "000105",
                "ue": "EMEF FICTICIA DOIS DE TESTE",
                "cod_tipo_escola": 1,
                "cod_turma": 9100004,
                "ano": "7",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "cod_modalidade": 5,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 1,
            }
        ]

        data = services.get_abrangencia_funcionario_perfil(
            "9364137",
            "perfil-professor",
            abrangencia=2,
            cargos=[3280],
            grupo=6,
        )

        mock_montar_turmas.assert_called_once_with("9364137")
        mock_client.get.assert_not_called()
        turma = data[0]
        self.assertEqual(turma["cod_dre"], "100005")
        self.assertEqual(turma["modalidade"], "Fundamental")
        self.assertEqual(turma["duracao_turno"], 5)

    @patch("apps.professores.services.pedagogico_services")
    def test_abrangencia_sme_faz_proxy_e_monta_bloco(
        self, mock_pedagogico_services: MagicMock
    ) -> None:
        mock_turmas = (
            mock_pedagogico_services.get_todas_turmas_atribuidas_dre_ue
        )
        mock_turmas.return_value = {"abrangencia": None, "dres": []}

        data = services.get_abrangencia_funcionario_perfil(
            "000001",
            "perfil-sme",
            abrangencia=6,
            grupo=31,
            eh_perfil_manual=True,
        )

        mock_pedagogico_services.get_todas_turmas_atribuidas_dre_ue.assert_called_once_with()
        self.assertEqual(data, {"abrangencia": None, "dres": []})


class GetFuncionariosNovosContratosTest(SimpleTestCase):
    """Valida services dos novos contratos de funcionarios."""

    @patch("apps.professores.services._client")
    def test_funcionarios_unidade_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.json_or_none.return_value = [
            {"login": "11122233388", "nome_servidor": "LUCAS", "perfil": "p1"}
        ]

        result = services.get_funcionarios_unidade("100004", ["p1"])

        mock_client.post.assert_called_once_with(
            "/api/v1/professores/funcionarios/unidade/100004/",
            payload=["p1"],
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, mock_client.json_or_none.return_value)

    @patch("apps.professores.services._client")
    def test_admins_sme_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.json_or_none.return_value = ["9521992"]

        result = services.get_funcionarios_admins_sme(["perfil"])

        mock_client.post.assert_called_once_with(
            "/api/v1/professores/funcionarios/admins/sme/",
            payload=["perfil"],
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, ["9521992"])

    @patch("apps.professores.services._client")
    def test_dados_sigpae_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = {"rf": "7900001"}

        result = services.get_funcionario_dados_sigpae("7900001")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/funcionarios/DadosSigpae/7900001/"
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, {"rf": "7900001"})

    @patch("apps.professores.services._client")
    def test_cargos_funcionario_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [{"rf": 7900001}]

        result = services.get_cargos_funcionario("7900001")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/funcionarios/cargo/7900001/"
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, [{"rf": 7900001}])

    @patch("apps.professores.services._client")
    def test_funcionarios_conecta_formacao_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [{"rf": "7900001"}]

        result = services.get_funcionarios_conecta_formacao(
            {"codigos_cargos": ["3360"]}
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/funcionarios/registros-funcionais/"
            "conecta-formacao/",
            params={"codigos_cargos": ["3360"]},
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, [{"rf": "7900001"}])

    @patch("apps.professores.services._client")
    def test_dre_ue_atribuicao_cargo_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [{"codigo_rf": "7900001"}]

        result = services.get_dre_ue_atribuicao_cargo("7900001", "3360")

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/funcionarios/atribuicao/7900001/"
            "cargo/3360/"
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, [{"codigo_rf": "7900001"}])

    @patch("apps.professores.services._client")
    def test_usuarios_conecta_formacao_chama_path_correto(
        self, mock_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.json_or_none.return_value = [{"login": "7900001"}]

        result = services.get_usuarios_conecta_formacao(["perfil"])

        mock_client.post.assert_called_once_with(
            "/api/v1/professores/funcionarios/usuarios/conecta-formacao/",
            payload=["perfil"],
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertEqual(result, [{"login": "7900001"}])
