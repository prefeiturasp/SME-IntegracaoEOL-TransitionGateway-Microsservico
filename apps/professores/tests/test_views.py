"""Valida as views do domínio de professores."""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient

_MSG_TURMAS_NAO_ENCONTRADAS = "Não foram encontradas turmas atribuídas."


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


def _turma_atribuida_simplificada() -> dict[str, object]:
    """Cria payload simplificado de turma atribuída para os testes."""
    return {
        "codigoTurma": 3030050,
        "nomeTurma": "1A",
        "componenteCurricular": "Matemática",
        "dataInicioAtribuicao": "2026-02-03",
        "dataFimAtribuicao": None,
        "ano": "1",
        "etapaEnsino": 1,
    }


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

    def test_preserva_codigo_ue_funcionarios_ue(self) -> None:
        match = resolve("/api/funcionarios/ue/000123/")

        self.assertEqual(match.kwargs, {"codigo_ue": "000123"})

    def test_preserva_codigo_cargo_funcionarios_cargos(self) -> None:
        match = resolve("/api/funcionarios/cargos/3360/")

        self.assertEqual(match.kwargs, {"codigo_cargo": "3360"})

    def test_preserva_codigo_dre_funcionarios_supervisores(self) -> None:
        match = resolve("/api/funcionarios/supervisores/108100/")

        self.assertEqual(match.kwargs, {"codigo_dre": "108100"})

    def test_preserva_id_perfil_funcionarios_perfis(self) -> None:
        match = resolve("/api/funcionarios/perfis/perfil-x/")

        self.assertEqual(match.kwargs, {"id_perfil": "perfil-x"})

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

    def test_preserva_funcionarios_turma_disciplinas(self) -> None:
        match = resolve("/api/funcionarios/turmas/3030050/disciplinas/")

        self.assertEqual(match.kwargs, {"codigo_turma": "3030050"})

    def test_preserva_funcionario_perfil_turma_disciplinas(self) -> None:
        match = resolve(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "login": "000001",
                "id_perfil": "perfil-x",
                "codigo_turma": "3030050",
            },
        )

    def test_preserva_funcionario_perfil_turma_planejamento(self) -> None:
        match = resolve(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/planejamento/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "login": "000001",
                "id_perfil": "perfil-x",
                "codigo_turma": "3030050",
            },
        )

    def test_preserva_codigo_rf_turmas(self) -> None:
        """Valida RF na rota de turmas."""
        match = resolve("/api/professores/000001/turmas/")

        self.assertEqual(match.kwargs, {"codigo_rf": "000001"})

    def test_preserva_codigo_rf_e_ano_buscar_por_rf_dre_ue(self) -> None:
        """Valida RF e ano letivo na rota de busca."""
        match = resolve("/api/professores/000001/BuscarPorRfDreUe/2026/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "ano_letivo": 2026},
        )

    def test_preserva_ano_buscar_por_lista_rf(self) -> None:
        """Valida ano letivo na rota de busca por lista de RF."""
        match = resolve("/api/professores/2026/BuscarPorListaRF/")

        self.assertEqual(match.kwargs, {"ano_letivo": 2026})

    def test_preserva_codigo_rf_eh_emei(self) -> None:
        """Valida RF na rota de verificação de EMEI."""
        match = resolve("/api/professores/000001/ehEmei/")

        self.assertEqual(match.kwargs, {"codigo_rf": "000001"})

    def test_preserva_ano_e_dre_autocomplete(self) -> None:
        """Valida ano letivo e DRE na rota de autocomplete."""
        match = resolve("/api/professores/2026/AutoComplete/1/")

        self.assertEqual(
            match.kwargs,
            {"ano_letivo": 2026, "dre_id": "1"},
        )

    def test_preserva_rf_escola_e_ano_turmas_atribuidas(self) -> None:
        match = resolve(
            "/api/professores/000001/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(
            match.kwargs,
            {
                "codigo_rf": "000001",
                "codigo_eol_escola": "019465",
                "ano_letivo": 2026,
            },
        )

    def test_preserva_escola_e_ano_turmas_atribuidas(self) -> None:
        match = resolve(
            "/api/professores/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(
            match.kwargs,
            {"codigo_eol_escola": "019465", "ano_letivo": 2026},
        )

    def test_preserva_rf_e_ano_turmas_atribuidas(self) -> None:
        match = resolve("/api/professores/000001/turmas/anos_letivos/2026/")

        self.assertEqual(
            match.kwargs,
            {"codigo_rf": "000001", "ano_letivo": 2026},
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


class FuncionariosUeViewTest(SimpleTestCase):
    """Valida a busca de funcionários por unidade educacional."""

    @patch("apps.professores.views.services.get_funcionarios_ue")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
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
        client = _cliente_autenticado()
        payload = {"codigosRfs": ["000001"], "filtro": ""}

        resp = client.post(
            "/api/funcionarios/ue/000123/",
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json()[0],
            {
                "cd_Cargo": 0,
                "codigoFuncaoAtividade": 0,
                "codigoRf": "000001",
                "funcaoExterno": 0,
                "login": "000001",
                "nomeServidor": "NOME SERVIDOR",
                "tipoFuncaoExterno": 0,
            },
        )
        mock_service.assert_called_once_with("000123", payload)

    @patch("apps.professores.views.services.get_funcionarios_ue")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/ue/000123/",
            data={"codigosRfs": [], "filtro": ""},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.professores.views.services.get_funcionarios_ue")
    def test_404_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/ue/000123/",
            data={"codigosRfs": [], "filtro": ""},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), "Não foram encontrados funcionários.")

    @patch("apps.professores.views.services.get_funcionarios_ue")
    def test_502_quando_sidecar_retorna_objeto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {"codigo_rf": "000001"}
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/ue/000123/",
            data={"codigosRfs": [], "filtro": ""},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            resp.json(),
            {"detail": "Resposta inválida do sidecar de professores."},
        )

    def test_400_quando_codigo_ue_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/ue/%20/",
            data={"codigosRfs": [], "filtro": ""},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )

    def test_400_quando_body_invalido(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/ue/000123/",
            data={"codigosRfs": "000001"},
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codigosRfs", resp.json())


class FuncionariosCargoViewTest(SimpleTestCase):
    """Valida a busca de funcionários por cargo."""

    @patch("apps.professores.views.services.get_funcionarios_por_cargo")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
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
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/cargos/3360/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        self.assertEqual(resp.json()[0]["cargo"], "DIRETOR")
        mock_service.assert_called_once_with("3360")

    @patch("apps.professores.views.services.get_funcionarios_por_cargo")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/cargos/3360/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.professores.views.services.get_funcionarios_por_cargo")
    def test_502_quando_sidecar_retorna_objeto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {"codigo_rf": "000001"}
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/cargos/3360/")

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)

    def test_400_quando_codigo_cargo_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/cargos/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoCargo."},
        )


class FuncionariosSupervisoresViewTest(SimpleTestCase):
    """Valida a busca de supervisores por DRE."""

    @patch("apps.professores.views.services.get_supervisores_por_dre")
    def test_200_retorna_supervisores(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "codigo_rf": "000001",
                "nome_servidor": "NOME SERVIDOR",
            },
        ]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/supervisores/108100/",
            data=["000001"],
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], "000001")
        self.assertEqual(resp.json()[0]["nomeServidor"], "NOME SERVIDOR")
        mock_service.assert_called_once_with("108100", ["000001"])

    @patch("apps.professores.views.services.get_supervisores_por_dre")
    def test_404_quando_sem_supervisores(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/supervisores/108100/",
            data=["000001"],
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), "Não foram encontrados supervisores.")

    def test_400_quando_lista_vazia(self) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/supervisores/108100/",
            data=[],
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            "A lista de códigos de supervisores é obrigatória.",
        )

    @patch("apps.professores.views.services.get_supervisores_por_dre")
    def test_502_quando_sidecar_retorna_objeto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = {"codigo_rf": "000001"}
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/supervisores/108100/",
            data=["000001"],
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)


class FuncionariosPerfisViewTest(SimpleTestCase):
    """Valida usuários SGP por perfil."""

    @patch("apps.professores.views.services.get_usuarios_sgp_por_perfil")
    def test_200_com_codigo_dre_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "cd_cargo": "3360",
                "codigo_funcao_atividade": 0,
                "codigo_rf": "000001",
                "funcao_externo": 0,
                "login": None,
                "nome_servidor": "ANA",
                "tipo_funcao_externo": 0,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/perfis/perfil-x/?CodigoDre=108100"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "cd_Cargo": 3360,
                    "codigoFuncaoAtividade": 0,
                    "codigoRf": "000001",
                    "funcaoExterno": 0,
                    "login": None,
                    "nomeServidor": "ANA",
                    "tipoFuncaoExterno": 0,
                }
            ],
        )
        mock_service.assert_called_once_with(
            "perfil-x",
            {"codigo_dre": "108100"},
        )

    @patch("apps.professores.views.services.get_usuarios_sgp_por_perfil")
    def test_200_com_codigo_rf_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "cd_cargo": "3379",
                "codigo_funcao_atividade": 0,
                "codigo_rf": "7654321",
                "funcao_externo": 0,
                "login": None,
                "nome_servidor": "ANA",
                "tipo_funcao_externo": 0,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/perfis/perfil-x/?CodigoRf=7654321"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRf"], "7654321")
        self.assertEqual(resp.json()[0]["login"], None)
        mock_service.assert_called_once_with(
            "perfil-x",
            {"codigo_rf": "7654321"},
        )

    @patch("apps.professores.views.services.get_usuarios_sgp_por_perfil")
    def test_400_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "erro"
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/perfis/perfil-x/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), "erro")


class FuncionariosPerfisDreViewTest(SimpleTestCase):
    """Valida funcionários SGP por perfil e DRE."""

    @patch(
        "apps.professores.views.services.get_funcionarios_sgp_por_perfil_dre"
    )
    def test_200_com_filtros_legado(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [
            {
                "cd_cargo": "3352",
                "codigo_funcao_atividade": 0,
                "codigo_rf": "6657109",
                "funcao_externo": 0,
                "login": None,
                "nome_servidor": "CRISTINA",
                "tipo_funcao_externo": 0,
            }
        ]
        client = _cliente_autenticado()
        path = "/api/funcionarios/perfis/perfil-x/dres/108200/"
        query = "?CodigoUe=000532&CodigoRf=6657109&NomeServidor=CRISTINA"

        resp = client.get(f"{path}{query}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "cd_Cargo": 3352,
                    "codigoFuncaoAtividade": 0,
                    "codigoRf": "6657109",
                    "funcaoExterno": 0,
                    "login": None,
                    "nomeServidor": "CRISTINA",
                    "tipoFuncaoExterno": 0,
                }
            ],
        )
        mock_service.assert_called_once_with(
            "perfil-x",
            "108200",
            {
                "codigo_ue": "000532",
                "codigo_rf": "6657109",
                "nome_servidor": "CRISTINA",
            },
        )

    @patch(
        "apps.professores.views.services.get_funcionarios_sgp_por_perfil_dre"
    )
    def test_204_quando_sidecar_retorna_none(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/perfis/perfil-x/dres/108200/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services.get_funcionarios_sgp_por_perfil_dre"
    )
    def test_400_quando_sidecar_retorna_texto(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = "erro"
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/perfis/perfil-x/dres/108200/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), "erro")


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
        """Retorna 204 quando não há turmas do professor."""
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


class FuncionarioTurmaDisciplinasViewTest(SimpleTestCase):
    """Valida disciplinas por turma."""

    @patch("apps.professores.views.services.get_disciplinas_turma")
    def test_200_retorna_disciplinas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [{"codDisciplina": 512}]
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/turmas/3030050/disciplinas/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [{"codDisciplina": 512}])
        mock_service.assert_called_once_with("3030050")

    @patch("apps.professores.views.services.get_disciplinas_turma")
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/turmas/3030050/disciplinas/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_400_quando_codigo_turma_e_somente_espacos(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/turmas/%20/disciplinas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoTurma."},
        )


class FuncionarioPerfilTurmaDisciplinasViewTest(SimpleTestCase):
    """Valida disciplinas do funcionário por turma."""

    @patch("apps.professores.views.services.get_disciplinas_funcionario_turma")
    def test_200_repassa_parametros_temporarios(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [{"codDisciplina": 512}]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/?abrangencia=3&cargos=3239"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            "000001",
            "perfil-x",
            "3030050",
            abrangencia=3,
            cargos=[3239],
        )

    @patch("apps.professores.views.services.get_disciplinas_funcionario_turma")
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.professores.views.services.get_disciplinas_funcionario_turma")
    def test_400_quando_login_vazio(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/%20/perfis/perfil-x/"
            "turmas/3030050/disciplinas/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(), {"detail": "É necessário informar o login."}
        )
        mock_service.assert_not_called()


class FuncionarioPerfilTurmaDisciplinasPlanejamentoViewTest(SimpleTestCase):
    """Valida disciplinas de planejamento."""

    @patch("apps.professores.views.services.get_disciplinas_funcionario_turma")
    def test_200_repassa_planejamento_e_abrangencia(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [{"codDisciplina": 512}]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/planejamento/?abrangencia=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            "000001",
            "perfil-x",
            "3030050",
            planejamento=True,
            abrangencia=2,
        )

    @patch("apps.professores.views.services.get_disciplinas_funcionario_turma")
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/000001/perfis/perfil-x/"
            "turmas/3030050/disciplinas/planejamento/"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class FuncionarioPerfilTurmasViewTest(SimpleTestCase):
    """Valida abrangência de turmas por perfil."""

    @patch(
        "apps.professores.views.services.get_abrangencia_funcionario_perfil"
    )
    def test_200_repassa_parametros_temporarios(
        self, mock_service: MagicMock
    ) -> None:
        payload: dict[str, object] = {"abrangencia": None, "dres": []}
        mock_service.return_value = payload
        client = _cliente_autenticado()

        resp = client.get(
            "/api/funcionarios/000001/perfis/perfil-x/turmas/"
            "?abrangencia=4&cargos=3239&funcoesId=1&grupo=2"
            "&dreCodigo=108100&ehPerfilManual=true"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), payload)
        mock_service.assert_called_once_with(
            "000001",
            "perfil-x",
            abrangencia=4,
            cargos=[3239],
            funcoes=[1],
            grupo=2,
            dre_codigo="108100",
            eh_perfil_manual=True,
        )

    @patch(
        "apps.professores.views.services.get_abrangencia_funcionario_perfil"
    )
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/000001/perfis/perfil-x/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.professores.views.services.get_abrangencia_funcionario_perfil"
    )
    def test_400_quando_perfil_vazio(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/funcionarios/000001/perfis/%20/turmas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(), {"detail": "É necessário informar o perfil."}
        )
        mock_service.assert_not_called()


class FuncionariosTurmasViewTest(SimpleTestCase):
    """Valida abrangência de turmas por UEs."""

    @patch("apps.professores.views.services.get_abrangencia_ues")
    def test_200_retorna_abrangencia(self, mock_service: MagicMock) -> None:
        payload: dict[str, object] = {"abrangencia": None, "dres": []}
        mock_service.return_value = payload
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/turmas/",
            ["000532"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), payload)
        mock_service.assert_called_once_with(["000532"])

    @patch("apps.professores.views.services.get_abrangencia_ues")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/turmas/",
            ["000532"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class FuncionariosBuscarTurmasElegiveisViewTest(SimpleTestCase):
    """Valida busca de turmas elegíveis."""

    @patch("apps.professores.views.services.get_turmas_elegiveis")
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        payload = {
            "CodigoRf": "000001",
            "CodigoTurma": 1,
            "ComponenteCurricular": 2,
        }
        mock_service.return_value = [{"nomeTurma": "1A", "codTurma": 3030050}]
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarTurmasElegiveis/",
            payload,
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), [{"nomeTurma": "1A", "codTurma": 3030050}]
        )
        mock_service.assert_called_once_with(payload)

    @patch("apps.professores.views.services.get_turmas_elegiveis")
    def test_204_quando_lista_vazia(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/BuscarTurmasElegiveis/",
            {
                "CodigoRf": "000001",
                "CodigoTurma": 1,
                "ComponenteCurricular": 2,
            },
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class FuncionariosViewTest(SimpleTestCase):
    """Valida busca de funcionários por filtros."""

    @patch("apps.professores.views.services.get_funcionarios")
    def test_200_retorna_funcionarios(self, mock_service: MagicMock) -> None:
        payload = {"CodigoUE": "000532"}
        mock_service.return_value = [{"codigoRf": "000001"}]
        client = _cliente_autenticado()

        resp = client.post("/api/funcionarios/", payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [{"codigoRf": "000001"}])
        mock_service.assert_called_once_with(payload)

    @patch("apps.professores.views.services.get_funcionarios")
    def test_204_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.post(
            "/api/funcionarios/",
            {"CodigoUE": "000532"},
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


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
        """Repassa filtros de DRE, UE e outros cargos."""
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
        """Retorna 204 quando professor está ausente."""
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
        """Retorna 204 quando não há professores."""
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
        """Retorna booleano de vínculo com EMEI."""
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
    def test_200_lista_vazia_quando_sem_conteudo(
        self, mock_service: MagicMock
    ) -> None:
        """Retorna lista vazia quando não há conteúdo."""
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/2026/AutoComplete/1/?ue_id=019465&nome=ana"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.professores.views.services.get_autocomplete_professores")
    def test_200_lista_vazia_quando_lista_vazia(
        self, mock_service: MagicMock
    ) -> None:
        """Retorna lista vazia."""
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


class ProfessorBuscaTurmasAtribuidasEscolaViewTest(SimpleTestCase):
    """Valida turmas atribuídas ao professor por escola."""

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professor_escola"
    )
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_atribuida_simplificada()]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [_turma_atribuida_simplificada()])
        mock_service.assert_called_once_with("000001", "019465", 2026)

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professor_escola"
    )
    def test_404_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), _MSG_TURMAS_NAO_ENCONTRADAS)

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professor_escola"
    )
    def test_400_quando_codigo_escola_e_somente_espacos(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/000001/escolas/%20/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoUE."},
        )
        mock_service.assert_not_called()


class BuscaTurmasAtribuidasProfessoresEscolaViewTest(SimpleTestCase):
    """Valida turmas atribuídas aos professores por escola."""

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professores_escola"
    )
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_atribuida_simplificada()]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [_turma_atribuida_simplificada()])
        mock_service.assert_called_once_with("019465", 2026)

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professores_escola"
    )
    def test_404_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = None
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/escolas/019465/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), _MSG_TURMAS_NAO_ENCONTRADAS)

    @patch(
        "apps.professores.views.services."
        "get_turmas_atribuidas_professores_escola"
    )
    def test_400_quando_codigo_escola_e_somente_espacos(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/professores/escolas/%20/turmas/anos_letivos/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )
        mock_service.assert_not_called()


class ProfessorBuscarTurmasAtribuidasViewTest(SimpleTestCase):
    """Valida turmas atribuídas ao professor por ano letivo."""

    @patch("apps.professores.views.services.get_turmas_atribuidas_professor")
    def test_200_retorna_turmas(self, mock_service: MagicMock) -> None:
        mock_service.return_value = [_turma_atribuida_simplificada()]
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/turmas/anos_letivos/2026/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [_turma_atribuida_simplificada()])
        mock_service.assert_called_once_with("000001", 2026)

    @patch("apps.professores.views.services.get_turmas_atribuidas_professor")
    def test_404_quando_sem_conteudo(self, mock_service: MagicMock) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/professores/000001/turmas/anos_letivos/2026/")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), _MSG_TURMAS_NAO_ENCONTRADAS)

    @patch("apps.professores.views.services.get_turmas_atribuidas_professor")
    def test_400_quando_codigo_rf_e_somente_espacos(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/professores/%20/turmas/anos_letivos/2026/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigoRF."},
        )
        mock_service.assert_not_called()


class ProfessorVerificarAtribuicaoDisciplinaViewTest(SimpleTestCase):
    """Valida os parâmetros da verificação de atribuição por disciplina."""

    _URL = (
        "/api/professores/000001/turmas/123/disciplinas/456/"
        "atribuicao/verificar/data"
    )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_disciplina_territorio_saber"
    )
    def test_repassa_false_booleano_e_retorno_true(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = True
        client = _cliente_autenticado()

        resp = client.get(
            self._URL,
            {
                "dataConsulta": "2026-07-28",
                "territorioSaber": "false",
            },
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIs(resp.json(), True)
        mock_service.assert_called_once_with(
            "000001",
            "123",
            "456",
            "2026-07-28",
            False,
        )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_disciplina_territorio_saber"
    )
    def test_400_para_data_invalida(
        self,
        mock_service: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(self._URL, {"dataConsulta": "28/07/2026"})

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()


class ProfessorVerificarAtribuicaoDataViewTest(SimpleTestCase):
    """Valida a verificação da atribuição por data."""

    _URL = (
        "/api/professores/000001/turmas/3032577/"
        "atribuicao/verificar/data/"
    )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_professor_turma"
    )
    def test_200_repassa_parametros_e_retorno(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = True

        resp = _cliente_autenticado().get(
            self._URL,
            {"dataConsulta": "2026-07-28"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIs(resp.json(), True)
        mock_service.assert_called_once_with(
            "000001",
            "3032577",
            "2026-07-28",
        )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_professor_turma"
    )
    def test_400_quando_data_ausente(
        self,
        mock_service: MagicMock,
    ) -> None:
        resp = _cliente_autenticado().get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()


class ProfessorStatusAtribuicaoViewTest(SimpleTestCase):
    """Valida a consulta do status da atribuição."""

    @patch(
        "apps.professores.views.services."
        "get_status_atribuicao_professor_turma"
    )
    def test_200_repassa_parametros_e_retorno(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = {"anoAtribuicao": 2026}

        resp = _cliente_autenticado().get(
            "/api/professores/000001/turmas/3032577/atribuicao/status/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), {"anoAtribuicao": 2026})
        mock_service.assert_called_once_with("000001", "3032577")


class ProfessorVerificarAtribuicaoDataTickViewTest(SimpleTestCase):
    """Valida a verificação da atribuição por data tick."""

    _URL = (
        "/api/professores/000001/turmas/3032577/disciplinas/89/"
        "atribuicao/verificar/datatick/"
    )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_professor_turma_disciplina"
    )
    def test_200_repassa_tick_e_retorno(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = True

        resp = _cliente_autenticado().get(
            self._URL,
            {"dataConsultaTick": "639207072000000000"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIs(resp.json(), True)
        mock_service.assert_called_once_with(
            "000001",
            "3032577",
            "89",
            "639207072000000000",
        )

    @patch(
        "apps.professores.views.services."
        "verificar_atribuicao_professor_turma_disciplina"
    )
    def test_400_quando_tick_invalido(
        self,
        mock_service: MagicMock,
    ) -> None:
        resp = _cliente_autenticado().get(
            self._URL,
            {"dataConsultaTick": "invalido"},
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()


class ProfessorAtribuicaoTurmaDisciplinaViewTest(SimpleTestCase):
    """Valida a consulta das atribuições por disciplina."""

    _URL = (
        "/api/professores/3032577/disciplinas/89/atribuicao/data/"
    )

    @patch(
        "apps.professores.views.services.get_atribuicoes_turma_disciplina"
    )
    def test_200_repassa_tick_e_retorna_lista(
        self,
        mock_service: MagicMock,
    ) -> None:
        mock_service.return_value = [{"codigoTurma": 3032577}]

        resp = _cliente_autenticado().get(
            self._URL,
            {"dataTicks": "639207072000000000"},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [{"codigoTurma": 3032577}])
        mock_service.assert_called_once_with(
            "3032577",
            "89",
            "639207072000000000",
        )

    @patch(
        "apps.professores.views.services.get_atribuicoes_turma_disciplina"
    )
    def test_400_quando_tick_ausente(
        self,
        mock_service: MagicMock,
    ) -> None:
        resp = _cliente_autenticado().get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()
