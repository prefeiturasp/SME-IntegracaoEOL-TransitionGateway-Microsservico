"""Valida os serviços do domínio de professores."""

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
            "3032577",
            "2026-07-28",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/3032577/"
            "verificar-atribuicao/?data_consulta=2026-07-28"
        )
        mock_client.json_or_none.assert_called_once_with(mock_response)
        self.assertIs(result, True)


class GetStatusAtribuicaoProfessorTurmaTest(SimpleTestCase):
    """Valida a consulta do status da atribuição."""

    @patch("apps.professores.services._client")
    def test_chama_sidecar_e_serializa_status(
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
            "3032577",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/3032577/atribuicao/status/"
        )
        self.assertEqual(result["anoAtribuicao"], 2026)


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
            "3032577",
            "89",
            639207072000000000,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/3032577/disciplinas/89/"
            "atribuicao/verificar/datatick/"
            "?data_consulta_tick=639207072000000000"
        )
        self.assertIs(result, True)


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
            "3032577",
            "89",
            "2026-07-28",
            True,
        )

        mock_verificar.assert_called_once_with(
            "000001",
            "3032577",
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
            "3032577",
            "89",
            "2026-07-28",
            False,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/turmas/3032577/disciplinas/89/"
            "atribuicao/verificar/data/?data_consulta=2026-07-28"
        )
        self.assertIs(result, True)


class GetAtribuicoesTurmaDisciplinaTest(SimpleTestCase):
    """Valida a consulta de atribuições da turma e disciplina."""

    @patch("apps.professores.services._client")
    def test_serializa_lista_retornada_pelo_sidecar(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.json_or_none.return_value = [
            {
                "codigo_turma": "3032577",
                "ano_letivo": None,
                "nome_turma": "7A",
                "data_inicio_atribuicao": "2026-06-09T00:00:00",
                "data_fim_atribuicao": "2026-12-22T00:00:00",
                "data_fim_turma": "2026-12-22T00:00:00",
                "ano_atribuicao": 2026,
                "codigo_rf": "6230504",
                "disciplina_id": "89",
                "disciplina_nome": "CIENCIAS",
                "disciplinas_agrupadas_ids": None,
                "nome_professor": "LAZARO PRETEL",
            }
        ]

        result = services.get_atribuicoes_turma_disciplina(
            "3032577",
            "89",
            "639207072000000000",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/3032577/disciplinas/89/atribuicao/data/",
            params={"data_ticks": "639207072000000000"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["codigoTurma"], 3032577)
        self.assertEqual(result[0]["disciplinaNome"], "CIENCIAS")

    @patch("apps.professores.services._client")
    def test_retorna_lista_vazia_quando_payload_nao_e_lista(
        self,
        mock_client: MagicMock,
    ) -> None:
        mock_client.json_or_none.return_value = "Not Found"

        result = services.get_atribuicoes_turma_disciplina(
            "3032577",
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
                "codigo_rf": "7730900",
                "nome": None,
            },
        ]
        mock_resp_3240 = MagicMock()
        mock_resp_3240.status_code = 200
        mock_resp_3240.content = b"[{}]"
        mock_resp_3240.json.return_value = [
            {
                "codigo_rf": "7730901",
                "nome": None,
            },
        ]
        mock_get.side_effect = [mock_resp_3239, mock_resp_3240]

        result = services.get_funcionarios_escola_cargos(
            "019465",
            {"cargos": ["3239", "3240"], "dre_codigo": "1"},
        )

        mock_get.assert_has_calls(
            [
                call(
                    "/api/v1/professores/escolas/019465/funcionarios/",
                    params={"cargos": ["3239"], "dre_codigo": "1"},
                ),
                call(
                    "/api/v1/professores/escolas/019465/funcionarios/",
                    params={"cargos": ["3240"], "dre_codigo": "1"},
                ),
            ]
        )
        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": "7730900",
                    "nome": None,
                    "cargo_id": 3239,
                },
                {
                    "codigo_rf": "7730901",
                    "nome": None,
                    "cargo_id": 3240,
                },
            ],
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_sem_cargos(self, mock_get: MagicMock) -> None:
        result = services.get_funcionarios_escola_cargos("019465", {})

        mock_get.assert_not_called()
        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_sidecar_nao_retorna_lista(
        self, mock_get: MagicMock
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = {"codigo_rf": "7730900"}
        mock_get.return_value = mock_resp

        result = services.get_funcionarios_escola_cargos(
            "019465",
            {"cargos": "3239", "dre_codigo": "1"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/escolas/019465/funcionarios/",
            params={"cargos": ["3239"], "dre_codigo": "1"},
        )
        self.assertEqual(result, [])

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_com_apenas_dre_codigo(
        self, mock_get: MagicMock
    ) -> None:
        result = services.get_funcionarios_escola_cargos(
            "019465",
            {"dre_codigo": "1"},
        )

        mock_get.assert_not_called()
        self.assertEqual(result, [])


class GetFuncionariosEscolaFuncoesAtividadesTest(SimpleTestCase):
    """Valida busca de funcionários por funções atividades."""

    @patch.object(services._client, "get")
    def test_chama_path_correto_com_params(self, mock_get: MagicMock) -> None:
        mock_resp_30 = MagicMock()
        mock_resp_30.status_code = 200
        mock_resp_30.content = b"[{}]"
        mock_resp_30.json.return_value = [
            {
                "codigo_rf": "7795246",
                "nome": None,
                "codigo_funcao_atividade": 30,
            },
        ]
        mock_resp_31 = MagicMock()
        mock_resp_31.status_code = 200
        mock_resp_31.content = b"[{}]"
        mock_resp_31.json.return_value = [
            {
                "codigo_rf": "7795247",
                "nome": None,
                "codigo_funcao_atividade": 31,
            },
        ]
        mock_get.side_effect = [mock_resp_30, mock_resp_31]

        result = services.get_funcionarios_escola_funcoes_atividades(
            "019465",
            {"funcoes_atividades": ["30", "31"], "codigo_dre": "1"},
        )

        mock_get.assert_has_calls(
            [
                call(
                    "/api/v1/professores/escolas/019465/funcionarios/",
                    params={
                        "funcoes_atividades": ["30"],
                        "codigo_dre": "1",
                    },
                ),
                call(
                    "/api/v1/professores/escolas/019465/funcionarios/",
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
                    "codigo_rf": "7795246",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "codigo_rf": "7795247",
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
                "codigo_rf": "7795246",
                "nome": None,
            },
        ]
        mock_resp_31 = MagicMock()
        mock_resp_31.status_code = 200
        mock_resp_31.content = b"[{}]"
        mock_resp_31.json.return_value = [
            {
                "codigo_rf": "7795247",
                "nome": None,
            },
        ]
        mock_get.side_effect = [mock_resp_30, mock_resp_31]

        result = services.get_funcionarios_escola_funcoes_atividades(
            "019465",
            {"funcoes_atividades": ["30", "31"], "codigo_dre": "1"},
        )

        self.assertEqual(
            result,
            [
                {
                    "codigo_rf": "7795246",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "codigo_rf": "7795247",
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
            "019465",
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
                "cpf": "11610699840",
                "funcao_externo": 5,
            },
        ]
        mock_resp_6 = MagicMock()
        mock_resp_6.status_code = 200
        mock_resp_6.content = b"[{}]"
        mock_resp_6.json.return_value = [
            {
                "cpf": "11610699841",
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
                    "cpf": "11610699840",
                    "funcao_externo": 5,
                },
                {
                    "cpf": "11610699841",
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
                "cpf": "11610699840",
            },
        ]
        mock_resp_6 = MagicMock()
        mock_resp_6.status_code = 200
        mock_resp_6.content = b"[{}]"
        mock_resp_6.json.return_value = [
            {
                "cpf": "11610699841",
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
                    "cpf": "11610699840",
                    "funcao_externo": 5,
                },
                {
                    "cpf": "11610699841",
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
                "codigo_rf": "7654321",
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
        payload = [{"codigo_turma": 3030050, "nome_turma": "1A"}]
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
            {"dre_id": "1", "ue_id": "019465"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/BuscarPorRfDreUe/2026",
            params={"dre_id": "1", "ue_id": "019465"},
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
        mock_ues.return_value = ["000532", "000999"]
        mock_emei.return_value = ["000532"]

        result = services.get_eh_emei("000001")

        mock_ues.assert_called_once_with("000001")
        mock_emei.assert_called_once_with(["000532", "000999"])
        self.assertTrue(result)

    @patch(
        "apps.professores.services.institucional_services.get_codigos_ue_emei"
    )
    @patch("apps.professores.services.get_unidades_atribuicao_professor")
    def test_intersecao_vazia_retorna_false(
        self, mock_ues: MagicMock, mock_emei: MagicMock
    ) -> None:
        """Retorna falso quando não há intersecção de UEs."""
        mock_ues.return_value = ["000532"]
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
            "codigos_ue": ["000532"],
        }
        mock_get.return_value = mock_resp

        result = services.get_unidades_atribuicao_professor("000001")

        mock_get.assert_called_once_with(
            "/api/v1/professores/000001/unidades-atribuicao/"
        )
        self.assertEqual(result, ["000532"])


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
            {"ue_id": "019465", "nome": "ana"},
        )

        mock_get.assert_called_once_with(
            "/api/v1/professores/2026/AutoComplete/1",
            params={"ue_id": "019465", "nome": "ana"},
        )
        self.assertEqual(result, payload)


class GetTurmasProfessorDisciplinaTest(SimpleTestCase):
    """Valida a busca de turmas por professor e disciplina."""

    @patch.object(services._client, "post")
    def test_chama_path_correto(self, mock_post: MagicMock) -> None:
        payload = [
            {
                "codigo_turma": "3030050",
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
            ["3030050"],
        )

        mock_post.assert_called_once_with(
            "/api/v1/professores/000001/disciplina/5/turmas/",
            payload=["3030050"],
        )
        self.assertEqual(result, payload)


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
            "ue_codigo": "000532",
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
            "codigoDRE": "108100",
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
        mock_ancora.return_value = [self._ancora(2112345, "000532")]
        mock_ped.return_value = [self._turma(2112345)]
        mock_inst.return_value = [self._ue("000532")]

        result = services.montar_turmas_atribuidas_professor("000001")

        mock_ped.assert_called_once_with([2112345])
        mock_inst.assert_called_once_with(["000532"])
        self.assertEqual(len(result), 1)
        linha = result[0]
        self.assertEqual(linha["cod_turma"], 2112345)
        self.assertEqual(linha["cod_escola"], "000532")
        self.assertEqual(linha["cod_ue"], "000532")
        self.assertEqual(linha["modalidade"], "Fundamental")
        self.assertEqual(linha["cod_modalidade"], 5)
        self.assertEqual(linha["cod_dre"], "108100")
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
            self._ancora(2112345, "000532"),
            self._ancora(9999999, "000532"),
        ]
        mock_ped.return_value = [self._turma(2112345)]
        mock_inst.return_value = [self._ue("000532")]

        result = services.montar_turmas_atribuidas_professor("000001")

        self.assertEqual([linha["cod_turma"] for linha in result], [2112345])

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
        mock_ancora.return_value = [self._ancora(2112345, "000532")]
        mock_ped.return_value = [self._turma(2112345)]
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
        mock_ancora.return_value = [self._ancora(None, "000532")]

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
                "codigo_turma": 3030050,
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
            "019465",
            2026,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/000001/escolas/019465/turmas/anos_letivos/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigoTurma": 3030050,
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
            "019465",
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
                "codigo_turma": 3030050,
                "nome_turma": "1A",
                "componente_curricular": "Matemática",
                "data_inicio_turma": "2026-02-03",
                "data_fim_atribuicao": None,
                "ano": "1",
                "etapa_ensino": 1,
            },
        ]

        result = services.get_turmas_atribuidas_professores_escola(
            "019465",
            2026,
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/professores/escolas/019465/turmas/anos_letivos/2026/"
        )
        self.assertEqual(
            result,
            [
                {
                    "codigoTurma": 3030050,
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
            "019465",
            2026,
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
                "codigo_turma": 3030050,
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
                    "codigoTurma": 3030050,
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
        self.assertEqual(result[0]["codDisciplina"], 512)
        self.assertEqual(result[0]["disciplina"], "Arte")

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
            dre_codigo="108100",
        )

        mock_client.get.assert_called_once_with(
            "/api/v1/funcionarios/000001/turmas-atribuidas-ue/",
            params={"codigo_dre": "108100"},
        )
        self.assertEqual(
            data["abrangencia"],
            {
                "grupoID": "perfil-dre",
                "cargosId": [3239],
                "funcoesId": [10],
                "grupo": 5,
                "abrangencia": 4,
                "ehPerfilManual": False,
            },
        )

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
            dre_codigo="108100",
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
        self.assertEqual(
            data["abrangencia"],
            {
                "grupoID": "perfil-sme",
                "cargosId": [],
                "funcoesId": [],
                "grupo": 31,
                "abrangencia": 6,
                "ehPerfilManual": True,
            },
        )
