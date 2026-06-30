"""Valida as views do domínio de professores."""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


class ProfessoresUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_preserva_rf_professor(self) -> None:
        match = resolve("/api/professores/123456/")

        self.assertEqual(match.kwargs, {"rf_professor": "123456"})

    def test_preserva_codigo_rf(self) -> None:
        match = resolve("/api/professores/123456/validade/")

        self.assertEqual(match.kwargs, {"codigo_rf": "123456"})

    def test_preserva_registro_funcional_funcionario_ativo(self) -> None:
        match = resolve("/api/acessos/funcionario-ativo/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_registro_funcional_nome_servidor(self) -> None:
        match = resolve("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_registro_funcional_nome_usuario_eol(self) -> None:
        match = resolve("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(match.kwargs, {"registro_funcional": "RF001"})

    def test_preserva_codigo_rf_e_ano_letivo_buscar_por_rf(self) -> None:
        match = resolve("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "ano_letivo": 2026},
        )

    def test_resolve_funcionarios_buscar_por_lista_rf(self) -> None:
        match = resolve("/api/funcionarios/BuscarPorListaRF/")

        self.assertEqual(match.kwargs, {})

    def test_preserva_codigo_ue_funcionarios_escola(self) -> None:
        match = resolve("/api/escolas/000123/funcionarios/")

        self.assertEqual(match.kwargs, {"codigo_ue": "000123"})

    def test_preserva_codigo_ue_e_cargo_funcionarios_escola(self) -> None:
        match = resolve("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(
            match.kwargs,
            {"codigo_ue": "000123", "codigo_cargo": "14"},
        )

    def test_preserva_codigo_ue_funcionarios_cargos(self) -> None:
        match = resolve("/api/escolas/019465/funcionarios/cargos/")

        self.assertEqual(match.kwargs, {"codigo_ue": "019465"})

    def test_preserva_codigo_ue_funcionarios_funcoes_atividades(
        self,
    ) -> None:
        match = resolve("/api/escolas/019465/funcionarios/funcoes-atividades/")

        self.assertEqual(match.kwargs, {"codigo_ue": "019465"})

    def test_preserva_codigo_ue_funcionarios_funcoes_externas(self) -> None:
        match = resolve("/api/escolas/400870/funcionarios/funcoes-externas/")

        self.assertEqual(match.kwargs, {"codigo_ue": "400870"})

    def test_preserva_codigo_ue_e_funcao_externa(self) -> None:
        match = resolve("/api/escolas/400870/funcionarios/funcoes-externas/7/")

        self.assertEqual(
            match.kwargs,
            {"codigo_ue": "400870", "codigo_funcao_externa": "7"},
        )

    def test_preserva_codigo_ue_e_funcao_atividade(self) -> None:
        match = resolve(
            "/api/escolas/019465/funcionarios/funcoes-atividades/30/"
        )

        self.assertEqual(
            match.kwargs,
            {"codigo_ue": "019465", "codigo_funcao_atividade": "30"},
        )

    def test_preserva_professor_disciplina_turmas(self) -> None:
        match = resolve("/api/professores/000001/disciplina/5/turmas/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "disciplina_id": "5"},
        )

    def test_preserva_codigo_rf_turmas(self) -> None:
        """Valida que o código RF do professor é preservado na rota de turmas."""
        match = resolve("/api/professores/000001/turmas/")

        self.assertEqual(match.kwargs, {"codigo_rf": "000001"})

    def test_preserva_codigo_rf_e_ano_buscar_por_rf_dre_ue(self) -> None:
        """Valida que o código RF e o ano letivo são preservados na rota de busca."""
        match = resolve("/api/professores/000001/BuscarPorRfDreUe/2026/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "ano_letivo": 2026},
        )

    def test_preserva_ano_buscar_por_lista_rf(self) -> None:
        """Valida que o ano letivo é preservado na rota de busca por lista de RF."""
        match = resolve("/api/professores/2026/BuscarPorListaRF/")

        self.assertEqual(match.kwargs, {"ano_letivo": 2026})

    def test_preserva_codigo_rf_eh_emei(self) -> None:
        """Valida que o código RF é preservado na rota de verificação de EMEI."""
        match = resolve("/api/professores/000001/ehEmei/")

        self.assertEqual(match.kwargs, {"codigo_rf": "000001"})

    def test_preserva_ano_e_dre_autocomplete(self) -> None:
        """Valida que o ano letivo e o ID da DRE são preservados na rota de autocomplete."""
        match = resolve("/api/professores/2026/AutoComplete/1/")

        self.assertEqual(
            match.kwargs,
            {"ano_letivo": 2026, "dre_id": "1"},
        )


class ProfessorViewTest(SimpleTestCase):
    """Valida a resposta da view de professor."""

    @patch("apps.professores.views.services.get_professor")
    def test_200_retorna_nome(self, mock_service: MagicMock) -> None:
        mock_service.return_value = "Fulano de Tal"
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), "Fulano de Tal")
        mock_service.assert_called_once_with("123456")

    @patch("apps.professores.views.services.get_professor")
    def test_204_quando_professor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), {"detail": "Codigo RF e obrigatorio."})


class ValidadeProfessorViewTest(SimpleTestCase):
    """Valida a resposta da view de validade do professor."""

    @patch("apps.professores.views.services.get_validade_professor")
    def test_200_retorna_booleano(self, mock_service: MagicMock) -> None:
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get("/api/professores/123456/validade/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.json())
        mock_service.assert_called_once_with("123456")

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/validade/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )


class FuncionarioAtivoViewTest(SimpleTestCase):
    """Valida a resposta da view de funcionário ativo."""

    @patch("apps.professores.views.services.get_funcionario_ativo")
    def test_200_retorna_booleano(self, mock_service: MagicMock) -> None:
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get("/api/acessos/funcionario-ativo/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.json())
        mock_service.assert_called_once_with("RF001")

    def test_400_quando_registro_funcional_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/acessos/funcionario-ativo/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o registro funcional."},
        )


class NomeServidorViewTest(SimpleTestCase):
    """Valida a resposta da view de nome do servidor."""

    @patch("apps.professores.views.services.get_nome_servidor")
    def test_200_retorna_nome_e_cpf(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {
            "nome": "Maria Silva",
            "cpf": "000.000.000-00",
        }
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["nome"], "Maria Silva")
        self.assertEqual(data["cpf"], "000.000.000-00")
        mock_service.assert_called_once_with("RF001")

    @patch("apps.professores.views.services.get_nome_servidor")
    def test_204_quando_servidor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-servidor/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class NomeUsuarioEolViewTest(SimpleTestCase):
    """Valida a resposta da view de nome de usuário EOL."""

    @patch("apps.professores.views.services.get_nome_usuario_eol")
    def test_200_retorna_nome_usuario_eol(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "NOME USUARIO EOL"
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), "NOME USUARIO EOL")
        mock_service.assert_called_once_with("RF001")

    @patch("apps.professores.views.services.get_nome_usuario_eol")
    def test_204_quando_usuario_ausente(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/RF001/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_registro_funcional_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/nome-usuario-eol/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o registro funcional."},
        )


class ProfessorBuscarPorRfViewTest(SimpleTestCase):
    """Valida a busca de professor por RF e ano letivo."""

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_retorna_professor(self, mock_service: MagicMock) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {"codigoRF": "000001", "nome": "NOME PROFESSOR"},
        )
        mock_service.assert_called_once_with("000001", 2026, None)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_repassa_buscar_outros_cargos(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=true"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with("000001", 2026, True)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_200_repassa_buscar_outros_cargos_false(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=false"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with("000001", 2026, False)

    @patch("apps.professores.views.services.get_professor_por_rf")
    def test_204_quando_professor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/BuscarPorRf/2026/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )

    def test_400_quando_buscar_outros_cargos_invalido(self) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRf/2026/"
            "?buscar_outros_cargos=sim"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "buscar_outros_cargos deve ser booleano."},
        )


class FuncionariosBuscarPorListaRfViewTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF."""

    @patch("apps.professores.views.services.get_professores_por_lista_rf")
    def test_200_retorna_professores(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {"codigo_rf": "000001", "nome": "NOME PROFESSOR"},
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [{"codigoRF": "000001", "nome": "NOME PROFESSOR"}],
        )
        mock_service.assert_called_once_with(["000001"])

    @patch("apps.professores.views.services.get_professores_por_lista_rf")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_lista_vazia(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_quando_item_nao_e_texto(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarPorListaRF/",
            ["000001", 123],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class EscolaFuncionariosViewTest(SimpleTestCase):
    """Valida a busca de funcionários por escola."""

    @patch("apps.professores.views.services.get_funcionarios_escola")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "codigo_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        self.assertEqual(resp.json()[0]["nomeServidor"], "NOME SERVIDOR")
        self.assertIsNone(resp.json()[0]["cargo"])
        mock_service.assert_called_once_with("000123")

    @patch("apps.professores.views.services.get_funcionarios_escola")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class EscolaFuncionariosCargoViewTest(SimpleTestCase):
    """Valida a busca de funcionários por escola e cargo."""

    @patch("apps.professores.views.services.get_funcionarios_escola_por_cargo")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "000001",
                "nome": "NOME SERVIDOR",
                "data_inicio": "03/19/2024 00:00:00",
                "data_fim": None,
                "cargo": None,
                "codigo_tipo_funcao_atividade": 14,
                "esta_afastado": False,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        mock_service.assert_called_once_with("000123", "14")

    def test_400_quando_codigo_cargo_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoCargo."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )

    @patch("apps.professores.views.services.get_funcionarios_escola_por_cargo")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/000123/funcionarios/cargos/14/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class EscolaFuncionariosCargosViewTest(SimpleTestCase):
    """Valida resposta de funcionários da escola por cargos."""

    @patch("apps.professores.views.services.get_funcionarios_escola_cargos")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "7730900",
                "nome": None,
                "cargo_id": 3239,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/cargos/"
            "?cargos=3239&cargos=3240&dre_codigo=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "funcionarioRF": "7730900",
                    "funcionarioNome": None,
                    "cargoId": 3239,
                },
            ],
        )
        mock_service.assert_called_once_with(
            "019465",
            {"cargos": ["3239", "3240"], "dre_codigo": "1"},
        )

    @patch("apps.professores.views.services.get_funcionarios_escola_cargos")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/019465/funcionarios/cargos/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.professores.views.services.get_funcionarios_escola_cargos")
    def test_200_lista_vazia_com_apenas_dre_codigo(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/cargos/?dre_codigo=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            "019465",
            {"dre_codigo": "1"},
        )

    @patch("apps.professores.views.services.get_funcionarios_escola_cargos")
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/019465/funcionarios/cargos/")

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/cargos/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class EscolaFuncionariosFuncoesAtividadesViewTest(SimpleTestCase):
    """Valida resposta de funcionários por funções atividades."""

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_atividades"
    )
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "7795246",
                "nome": None,
                "codigo_funcao_atividade": 30,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/funcoes-atividades/"
            "?funcoes_atividades=30&funcoes_atividades=31&codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "funcionarioRF": "7795246",
                    "funcionarioNome": None,
                    "funcaoAtividadeId": 30,
                },
            ],
        )
        mock_service.assert_called_once_with(
            "019465",
            {"funcoes_atividades": ["30", "31"], "codigo_dre": "1"},
        )

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_atividades"
    )
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/funcoes-atividades/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_atividades"
    )
    def test_200_lista_vazia_com_apenas_codigo_dre(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/funcoes-atividades/"
            "?codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            "019465",
            {"codigo_dre": "1"},
        )

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_atividades"
    )
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/019465/funcionarios/funcoes-atividades/"
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/funcoes-atividades/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class EscolaFuncionariosFuncoesExternasViewTest(SimpleTestCase):
    """Valida resposta de funcionários por funções externas."""

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_externas"
    )
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "cpf": "11610699840",
                "funcao_externo": 5,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/400870/funcionarios/funcoes-externas/"
            "?funcoes=5&funcoes=6&codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "funcionarioCpf": "11610699840",
                    "funcaoExternaId": 5,
                },
            ],
        )
        mock_service.assert_called_once_with(
            "400870",
            {"funcoes": ["5", "6"], "codigo_dre": "1"},
        )

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_externas"
    )
    def test_204_quando_sem_conteudo_com_codigo_dre(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/400870/funcionarios/funcoes-externas/"
            "?codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_externas"
    )
    def test_200_lista_vazia_com_apenas_codigo_dre(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/400870/funcionarios/funcoes-externas/"
            "?codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            "400870",
            {"codigo_dre": "1"},
        )

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_externas"
    )
    def test_400_quando_sem_codigo_dre(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/400870/funcionarios/funcoes-externas/"  # NOSONAR
            "?funcoes=5"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.content, b"")
        mock_service.assert_not_called()

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_funcoes_externas"
    )
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/400870/funcionarios/funcoes-externas/"
            "?codigo_dre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/funcoes-externas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class EscolaFuncionariosFuncaoExternaViewTest(SimpleTestCase):
    """Valida resposta de funcionários por uma função externa."""

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_externa"
    )
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        """Testa retorno de funcionários por função externa."""
        mock_service.return_value = [
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
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-externas/7/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(item["codigoRF"], "000001")
        self.assertEqual(item["nomeServidor"], "NOME SERVIDOR")
        self.assertEqual(item["funcaoExterno"], 7)
        self.assertEqual(item["tipoFuncaoExterno"], 2)
        mock_service.assert_called_once_with("000123", "7")

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_externa"
    )
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna None para função externa."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-externas/7/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_externa"
    )
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna lista vazia."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-externas/7/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_externa"
    )
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        """Testa 502 quando o sidecar retorna texto para função externa."""
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-externas/7/"
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        """Testa 400 para codigoUE vazio na função externa."""
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/%20/funcionarios/funcoes-externas/7/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class EscolaFuncionariosFuncaoAtividadeViewTest(SimpleTestCase):
    """Valida resposta de funcionários por uma função atividade."""

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_atividade"
    )
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        """Testa retorno de funcionários por função atividade."""
        mock_service.return_value = [
            {
                "codigo_rf": "7654321",
                "nome": "NOME SERVIDOR",
                "codigo_cargo": "3379",
                "codigo_tipo_funcao_atividade": 1,
                "funcao_externo": 0,
                "tipo_funcao_externo": 0,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-atividades/1/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigoRf": "7654321",
                    "login": None,
                    "nomeServidor": "NOME SERVIDOR",
                    "cdCargo": 3379,
                    "codigoFuncaoAtividade": 1,
                    "funcaoExterno": 0,
                    "tipoFuncaoExterno": 0,
                },
            ],
        )
        mock_service.assert_called_once_with("000123", "1")

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_atividade"
    )
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna None para função atividade."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-atividades/1/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_atividade"
    )
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna lista vazia."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-atividades/1/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services."
        "get_funcionarios_escola_por_funcao_atividade"
    )
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        """Testa 502 quando o sidecar retorna texto para função atividade."""
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/000123/funcionarios/funcoes-atividades/1/"
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        """Testa 400 para codigoUE vazio na função atividade."""
        client = _cliente_autenticado()

        resp = client.get(
            "/api/escolas/%20/funcionarios/funcoes-atividades/1/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )


class ProfessorDisciplinaTurmasViewTest(SimpleTestCase):
    """Valida a busca de turmas por professor e disciplina."""

    @patch("apps.professores.views.services.get_turmas_professor_disciplina")
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_turma": "3030050",
                "data_disponibilizacao_aulas": "2026-12-22T00:00:00",
                "data_atribuicao_aula": "2026-03-30T00:00:00",
            },
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas/",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoTurma"], "3030050")
        mock_service.assert_called_once_with("000001", "5", ["3030050"])

    @patch("apps.professores.views.services.get_turmas_professor_disciplina")
    def test_502_quando_sidecar_retorna_lista_simples(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = ["3030050"]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas/",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )
        mock_service.assert_called_once_with("000001", "5", ["3030050"])

    @patch("apps.professores.views.services.get_turmas_professor_disciplina")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas/",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_lista_vazia(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/5/turmas/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/%20/disciplina/5/turmas/",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )

    def test_400_quando_disciplina_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/000001/disciplina/%20/turmas/",
            ["3030050"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar a disciplina."},
        )


class ProfessorTurmasViewTest(SimpleTestCase):
    """Valida a busca de turmas atribuídas ao professor."""

    @patch(
        "apps.professores.views.services.montar_turmas_atribuidas_professor"
    )
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        """Testa retorno de turmas atribuídas ao professor."""
        mock_service.return_value = [
            {
                "cod_escola": "019465",
                "cod_turma": 3030050,
                "tipo_turma": 1,
                "ano": "1",
                "ano_letivo": 2026,
                "cod_modalidade": 5,
                "cod_dre": "108100",
                "dre": "DRE TESTE",
                "dre_abrev": "DRE-T",
                "modalidade": "Fundamental",
                "nome_turma": "1A",
                "semestre": 0,
                "tipo_ue": "EMEF",
                "cod_tipo_ue": 1,
                "cod_ue": "019465",
                "ue": "EMEF TESTE",
                "ue_abrev": "EMEF T.",
                "tipo_escola": "EMEF",
                "cod_tipo_escola": 1,
                "duracao_turno": 5,
                "tipo_turno": 4,
                "ensino_especial": False,
                "serie_ensino": "1 ANO",
                "data_inicio_turma": "2024-02-01T00:00:00",
                "data_fim_turma": None,
                "extinta": False,
            },
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codTurma"], 3030050)
        self.assertEqual(resp.json()[0]["nomeTurma"], "1A")
        self.assertEqual(resp.json()[0]["codTipoEscola"], 1)
        mock_service.assert_called_once_with("000001")

    @patch(
        "apps.professores.views.services.montar_turmas_atribuidas_professor"
    )
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna lista vazia para turmas do professor."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        """Testa 400 quando o código RF do professor é apenas espaços."""
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )


class ProfessorBuscarPorRfDreUeViewTest(SimpleTestCase):
    """Valida a busca de professor por RF, DRE e UE."""

    @patch("apps.professores.views.services.get_professor_por_rf_dre_ue")
    def test_200_retorna_professor(self, mock_service: MagicMock) -> None:
        """Testa retorno de professor por RF, DRE e UE."""
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRfDreUe/2026/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {"codigoRF": "000001", "nome": "NOME PROFESSOR"},
        )
        mock_service.assert_called_once_with("000001", 2026, {})

    @patch("apps.professores.views.services.get_professor_por_rf_dre_ue")
    def test_200_repassa_filtros(self, mock_service: MagicMock) -> None:
        """Testa que os filtros de DRE, UE e buscar_outros_cargos são repassados corretamente para o serviço."""
        mock_service.return_value = {
            "codigo_rf": "000001",
            "nome": "NOME PROFESSOR",
        }
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/BuscarPorRfDreUe/2026/"
            "?dre_id=1&ue_id=019465&buscar_outros_cargos=true"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            "000001",
            2026,
            {
                "dre_id": "1",
                "ue_id": "019465",
                "buscar_outros_cargos": "true",
            },
        )

    @patch("apps.professores.views.services.get_professor_por_rf_dre_ue")
    def test_204_quando_professor_ausente(
        self, mock_service: MagicMock
    ) -> None:
        """Testa 204 quando o sidecar retorna None para professor por RF, DRE e UE."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/BuscarPorRfDreUe/2026/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        """Testa 400 quando o código RF do professor é apenas espaços."""
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/BuscarPorRfDreUe/2026/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )


class ProfessoresBuscarPorListaRfAnoViewTest(SimpleTestCase):
    """Valida a busca de professores por lista de RF e ano."""

    @patch("apps.professores.views.services.get_professores_por_lista_rf_ano")
    def test_200_retorna_professores(self, mock_service: MagicMock) -> None:
        """Testa retorno de professores por lista de RF e ano."""
        mock_service.return_value = [
            {"codigo_rf": "000001", "nome": "NOME PROFESSOR"},
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/2026/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [{"codigoRF": "000001", "nome": "NOME PROFESSOR"}],
        )
        mock_service.assert_called_once_with(2026, ["000001"])

    @patch("apps.professores.views.services.get_professores_por_lista_rf_ano")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        """Testa 204 quando o sidecar retorna None para professores por lista de RF e ano."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/2026/BuscarPorListaRF/",
            ["000001"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_lista_vazia(self) -> None:
        """Testa 400 quando a lista de RF está vazia."""
        client = _cliente_autenticado()

        resp = client.post(
            "/api/professores/2026/BuscarPorListaRF/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ProfessorEhEmeiViewTest(SimpleTestCase):
    """Valida a verificação de vínculo do professor com EMEI."""

    @patch("apps.professores.views.services.get_eh_emei")
    def test_200_retorna_booleano(self, mock_service: MagicMock) -> None:
        """Testa retorno de booleano indicando se o professor é vinculado a EMEI."""
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/ehEmei/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.json())
        mock_service.assert_called_once_with("000001")

    def test_400_quando_codigo_rf_e_somente_espacos(self) -> None:
        """Testa 400 quando o código RF do professor é apenas espaços."""
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/ehEmei/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )


class ProfessorAutoCompleteViewTest(SimpleTestCase):
    """Valida o autocomplete de professores por DRE e ano."""

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_200_retorna_professores(self, mock_service: MagicMock) -> None:
        """Testa retorno de professores para autocomplete por DRE e ano."""
        mock_service.return_value = [
            {"codigo_rf": "000001", "nome_servidor": "ANA SILVA"},
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [{"codigoRF": "000001", "nome": "ANA SILVA"}],
        )
        mock_service.assert_called_once_with(
            2026,
            "1",
            {"ue_id": "019465", "nome": "ana"},
        )

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_200_lista_vazia_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        """Testa 200 [] quando o sidecar retorna None para autocomplete de professores."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_200_lista_vazia_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        """Testa 200 [] quando o sidecar retorna lista vazia para autocomplete."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_502_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        """Testa 502 quando o sidecar retorna texto para autocomplete."""
        mock_service.return_value = "erro de contrato"
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_dre_id_e_somente_espacos(self) -> None:
        """Testa 400 quando o dreId é apenas espaços."""
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/%20/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o dreId."},
        )

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_400_quando_ue_id_ausente(self, mock_service: MagicMock) -> None:
        """Testa 400 quando o ueId não é informado."""
        client = _cliente_autenticado()

        resp = client.get("/api/professores/2026/AutoComplete/1/?nome=ana")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o ueId."},
        )
        mock_service.assert_not_called()

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_400_quando_nome_ausente(self, mock_service: MagicMock) -> None:
        """Testa 400 quando o nome não é informado."""
        client = _cliente_autenticado()

        resp = client.get("/api/professores/2026/AutoComplete/1/?ue_id=019465")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o nome."},
        )
        mock_service.assert_not_called()

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_204_quando_nome_menor_que_dois_caracteres(
        self, mock_service: MagicMock
    ) -> None:
        """Testa 204 quando o nome informado tem menos de dois caracteres."""
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=a"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_service.assert_not_called()
