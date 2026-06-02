"""Valida as views do domínio pedagógico."""

from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/v1/componentes-curriculares"
_PREFIX_TURMAS = "/api/turmas"


# Componente curricular completo retornado pelo sidecar.
_CC: dict[str, Any] = {
    "codigo": 1,
    "codigo_componente_territorio_saber": None,
    "codigo_componente_curricular_pai": None,
    "descricao": "Matematica",
    "regencia": False,
    "planejamento_regencia": False,
    "territorio_saber": False,
    "turma_codigo": None,
    "exibir_componente_eol": True,
    "professor": None,
    "codigos_territorios_agrupamento": [],
}

# Resumo de componente (apenas código e descrição).
_BASE_CC = {"codigo": 1, "descricao": "Matematica"}

# Item de grade curricular retornado pelo sidecar.
_GRADE = {
    "codigo_componente_curricular": 1,
    "descricao_componente_curricular": "Matematica",
    "codigo_ano_turma": "1",
    "descricao_serie_ensino": "1o Ano",
    "codigo_serie_ensino": 1,
    "modalidade": 5,
}

_REGENCIA = {
    "ano_turma": "1",
    "ano_letivo": 2024,
    "codigo": 1,
    "codigo_componente_territorio_saber": 0,
    "descricao": "Regencia",
    "territorio_saber": False,
    "tipo_escola": None,
    "turno_turma": 0,
    "componente_planejamento_regencia": False,
    "turma_codigo": None,
    "professor": None,
    "inicio_atribuicao": None,
    "fim_atribuicao": None,
}

_TURMA = {
    "ano": "1",
    "anoLetivo": 2026,
    "codigo": 3034092,
    "tipoTurma": 1,
    "modalidade": "Fundamental",
    "codigoModalidade": 5,
    "nomeTurma": "1A",
    "semestre": 0,
    "duracaoTurno": 55,
    "tipoTurno": 6,
    "dataFim": None,
    "ehistorico": False,
    "ensinoEspecial": False,
    "etapaEJA": 0,
    "serieEnsino": "1o Ano",
    "dataInicioTurma": "2026-02-04T00:00:00",
    "extinta": False,
    "situacao": "O",
    "ueCodigo": "092622",
}


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()

    user = User(username="teste")
    client.force_authenticate(user=user)

    return client


class ComponentesTurmaViewSetTest(SimpleTestCase):
    """Valida a view de componentes por turmas de uma UE."""

    @patch("apps.pedagogico.views.services.get_componentes_por_turmas_ue")
    def test_200_repassa_turmas(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/turmas/?turmas=T001&turmas=T002"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_id="UE001", turmas=["T001", "T002"]
        )


class TurmasRegularesViewSetTest(SimpleTestCase):
    """Valida a view de turmas regulares."""

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_200_retorna_lista_de_codigos(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = ["3014194", "3024590"]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            ["3024590", "3014194"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, ["3014194", "3024590"])
        mock_svc.assert_called_once_with(["3024590", "3014194"])

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_400_quando_payload_invalido(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            ["3024590", "ABC"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    @patch("apps.pedagogico.views.services.post_turmas_regulares")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-regulares/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class TurmasProgramaViewSetTest(SimpleTestCase):
    """Valida a view de turmas programa."""

    @patch("apps.pedagogico.views.services.post_turmas_programa")
    def test_200_retorna_lista_de_codigos(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = ["3133093", "3133096"]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-programa/",
            ["3133093", "3133096"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, ["3133093", "3133096"])
        mock_svc.assert_called_once_with(["3133093", "3133096"])

    @patch("apps.pedagogico.views.services.post_turmas_programa")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/turmas-programa/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class ListarTurmasViewSetTest(SimpleTestCase):
    """Valida a view de listagem de turmas."""

    @patch("apps.pedagogico.views.services.post_listar_turmas")
    def test_200_retorna_dados_de_turmas(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = [_TURMA]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/listar-turmas/",
            ["3034092"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["codigo"], 3034092)
        self.assertEqual(resp.data[0]["nomeTurma"], "1A")
        mock_svc.assert_called_once_with(["3034092"])

    @patch("apps.pedagogico.views.services.post_listar_turmas")
    def test_200_lista_vazia_sem_chamar_service(
        self,
        mock_svc: MagicMock,
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX_TURMAS}/listar-turmas/",
            [],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        mock_svc.assert_not_called()


class DadosTurmaViewSetTest(SimpleTestCase):
    """Valida a view de dados da turma."""

    @patch("apps.pedagogico.views.services.get_dados_turma")
    def test_200_retorna_dados_da_turma(
        self,
        mock_svc: MagicMock,
    ) -> None:
        mock_svc.return_value = _TURMA
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX_TURMAS}/3034092/dados/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["codigo"], 3034092)
        self.assertEqual(resp.data["ueCodigo"], "092622")
        mock_svc.assert_called_once_with("3034092")


class TurmasSchemaTest(SimpleTestCase):
    """Valida a documentacao de turmas no schema OpenAPI."""

    def test_endpoints_usam_tag_turma(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        schema = resp.data
        self.assertEqual(
            schema["paths"]["/api/turmas/turmas-regulares/"]["post"][
                "tags"
            ],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/turmas-programa/"]["post"]["tags"],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/listar-turmas/"]["post"]["tags"],
            ["Turma"],
        )
        self.assertEqual(
            schema["paths"]["/api/turmas/{codigo_turma}/dados/"]["get"][
                "tags"
            ],
            ["Turma"],
        )

    def test_body_nao_obrigatorio_e_descreve_codigos_turmas(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/schema/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        schema = resp.data
        paths = (
            "/api/turmas/turmas-regulares/",
            "/api/turmas/turmas-programa/",
        )
        for path in paths:
            with self.subTest(path=path):
                operation = schema["paths"][path]["post"]
                self.assertFalse(
                    operation["requestBody"].get("required", False)
                )
                self.assertIn(
                    "RequestBody: `codigos_turmas`",
                    operation["description"],
                )


class ComponentesCurricularesViewSetTest(SimpleTestCase):
    """Valida a view de catálogo de componentes curriculares."""

    @patch("apps.pedagogico.views.services.get_componentes_curriculares")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()


class GradeComponentesCurricularesViewSetTest(SimpleTestCase):
    """Valida a view de grade curricular por ano letivo."""

    @patch("apps.pedagogico.views.services.get_grade_curricular")
    def test_200_retorna_grade(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_GRADE]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ano-turma/ano-letivo/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data[0]["codigoComponenteCurricular"],
            1,
        )
        self.assertEqual(resp.data[0]["codigoAnoTurma"], "1")
        mock_svc.assert_called_once_with(2024)


class ComponentesRegenciaViewSetTest(SimpleTestCase):
    """Valida a view de componentes de regencia."""

    @patch("apps.pedagogico.views.services.get_componentes_regencia")
    def test_200_retorna_regencia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_REGENCIA]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/anos/2024/regencia/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["anoTurma"], "1")
        self.assertEqual(resp.data[0]["anoLetivo"], 2024)
        self.assertEqual(
            resp.data[0]["codigoComponenteTerritorioSaber"],
            0,
        )
        self.assertEqual(
            resp.data[0]["componentePlanejamentoRegencia"],
            False,
        )
        mock_svc.assert_called_once_with(2024)

    @patch("apps.pedagogico.views.services.get_componentes_regencia")
    def test_204_quando_regencia_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/anos/9/regencia/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with(9)


class ValidarComponentePapViewSetTest(SimpleTestCase):
    """Valida a view de componente PAP."""

    @patch("apps.pedagogico.views.services.validar_componente_pap")
    def test_200_repassa_parametros_do_path(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = True
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/RF001/"
            "perfis/P1/validar/pap/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data)
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            login="RF001",
            id_perfil="P1",
        )


class ComponentesFuncionarioViewSetTest(SimpleTestCase):
    """Valida a view de componentes por funcionario."""

    @patch("apps.pedagogico.views.services.get_componentes_funcionario")
    def test_200_retorna_componentes(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/funcionarios/RF001/perfis/P1/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["planejamentoRegencia"], False)
        self.assertEqual(resp.data[0]["turmaCodigo"], None)
        mock_svc.assert_called_once_with(
            login="RF001",
            id_perfil="P1",
        )

    @patch("apps.pedagogico.views.services.get_componentes_funcionario")
    def test_204_quando_lista_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/funcionarios/RF001/perfis/P1/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with(
            login="RF001",
            id_perfil="P1",
        )


class ComponentesTurmaAnoViewSetTest(SimpleTestCase):
    """Valida a view de componentes por anos escolares."""

    @patch("apps.pedagogico.views.services.get_componentes_ue_anos")
    def test_200_repassa_anos_escolares(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024"
            "/anos-escolares/?anosEscolares=1&anosEscolares=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.data[0]["codigoComponenteTerritorioSaber"],
            None,
        )
        self.assertEqual(resp.data[0]["planejamentoRegencia"], False)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
            anos_escolares=["1", "2"],
        )


class ComponentesTurmaProgramaViewSetTest(SimpleTestCase):
    """Valida a view de componentes de turmas programa."""

    @patch("apps.pedagogico.views.services.get_componentes_turmas_programa")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["turmaCodigo"], None)
        self.assertEqual(resp.data[0]["exibirComponenteEOL"], True)

        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
        )
