"""Testes das views do domínio pedagógico."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/v1/componentes-curriculares"

_CC = {
    "codigo": 1,
    "codigoComponenteTerritorioSaber": None,
    "codigoComponenteCurricularPai": None,
    "descricao": "Matematica",
    "regencia": False,
    "planejamentoRegencia": False,
    "territorioSaber": False,
    "turmaCodigo": None,
    "exibirComponenteEOL": True,
    "professor": None,
    "codigosTerritoriosAgrupamento": [],
}

_BASE_CC = {"codigo": 1, "descricao": "Matematica"}

_REGENCIA = {
    "anoTurma": 1,
    "anoLetivo": 2024,
    "codigo": 1,
    "codigoComponenteTerritorioSaber": None,
    "descricao": "Matematica",
    "territorioSaber": False,
    "tipoEscola": None,
    "turnoTurma": 1,
    "componentePlanejamentoRegencia": False,
    "turmaCodigo": None,
    "professor": None,
    "inicioAtribuicao": None,
    "fimAtribuicao": None,
}

_VIGENCIA = {
    "componenteCurricularCodigo": "1",
    "componenteCurricularDescricao": "Matematica",
    "turmaCodigo": "T001",
    "dataInicioTurma": None,
}

_GRADE = {
    "codigoComponenteCurricular": 1,
    "descricaoComponenteCurricular": "Matematica",
    "codigoAnoTurma": "1",
    "descricaoSerieEnsino": "1o Ano",
    "codigoSerieEnsino": 1,
    "modalidade": 5,
}

_AGRUPAMENTO = {
    "codigo": 1,
    "codigoComponenteTerritorioSaber": 2,
    "codigoComponenteCurricularPai": None,
    "descricao": "Agrupamento A",
    "regencia": False,
    "planejamentoRegencia": False,
    "territorioSaber": True,
    "turmaCodigo": "T001",
    "professor": None,
    "codigosTerritoriosAgrupamento": [],
}


class _UsuarioAutenticado:
    is_authenticated = True


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=_UsuarioAutenticado())
    return client


class ComponentesFuncionarioComTurmaViewTest(SimpleTestCase):
    """Testes de GET L1 — componentes por turma com agrupamento."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_funcionario"
    )
    def test_200_repassa_flag_como_bool(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/login1"
            "/perfis/P001/agrupaComponenteCurricular/true/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            login="login1",
            id_perfil="P001",
            codigo_turma="T001",
            agrupa=True,
        )


class ComponentesFuncionarioViewTest(SimpleTestCase):
    """Testes de GET L2 — componentes sem filtro de turma."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_funcionario"
    )
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/funcionarios/login1/perfis/P001/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            login="login1", id_perfil="P001"
        )


class ComponentesPlanejamentoFuncionarioViewTest(SimpleTestCase):
    """Testes de GET L3 — componentes com planejamento de regência."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_funcionario"
    )
    def test_200_passa_planejamento_true(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/login1"
            "/perfis/P001/planejamento/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            login="login1",
            id_perfil="P001",
            codigo_turma="T001",
            planejamento=True,
        )


class ComponentesRegenciaViewTest(SimpleTestCase):
    """Testes de GET L4 — componentes de regência por ano de turma."""

    @patch(
        "apps.pedagogico.views.services.get_componentes_regencia"
    )
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_REGENCIA]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/anos/1/regencia/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(1)


class ValidarPapViewTest(SimpleTestCase):
    """Testes de GET L5 — verificar componente PAP em turma."""

    @patch("apps.pedagogico.views.services.validar_pap")
    def test_200_retorna_booleano(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = True
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/funcionarios/login1"
            "/perfis/P001/validar/pap/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_turma="T001", login="login1", id_perfil="P001"
        )


class ComponentesUeAnosEscolaresViewTest(SimpleTestCase):
    """Testes de GET L6 — componentes por UE, modalidade, ano e anos escolares."""

    @patch(
        "apps.pedagogico.views.services.get_componentes_ue_anos"
    )
    def test_200_repassa_anos_escolares(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024"
            "/anos-escolares/?anosEscolares=1&anosEscolares=2"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_id="UE001",
            modalidade=5,
            ano_letivo=2024,
            anos_escolares=["1", "2"],
        )


class ComponentesUeModalidadeViewTest(SimpleTestCase):
    """Testes de GET L7 — componentes de turmas programa."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_turmas_programa"
    )
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ues/UE001/modalidades/5/anos/2024/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_id="UE001", modalidade=5, ano_letivo=2024
        )


class ComponentesPorTurmasUeViewTest(SimpleTestCase):
    """Testes de GET L8 — componentes por lista de turmas e UE."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_por_turmas_ue"
    )
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


class ComponentesPlanejamentoViewTest(SimpleTestCase):
    """Testes de GET L9 — componentes para planejamento."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_componentes_planejamento"
    )
    def test_200_repassa_codigos_turmas(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/?codigoTurmas=T001&codigoTurmas=T002"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_turmas=["T001", "T002"]
        )


class ComponentesRegularesViewTest(SimpleTestCase):
    """Testes de GET L10 — componentes sem pós-processamento."""

    @patch(
        "apps.pedagogico.views.services.get_componentes_brutos"
    )
    def test_200_repassa_codigos_turmas(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_CC]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/regulares/?codigoTurmas=T001"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(codigo_turmas=["T001"])


class CatalogoComponentesViewTest(SimpleTestCase):
    """Testes de GET L11 — catálogo de componentes curriculares."""

    @patch(
        "apps.pedagogico.views.services.get_catalogo_componentes"
    )
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_BASE_CC]
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()


class DadosAulaTurmaViewTest(SimpleTestCase):
    """Testes de GET L12 — vigência de componentes por turma."""

    @patch(
        "apps.pedagogico.views.services.get_vigencia_componentes"
    )
    def test_200_repassa_query_params(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_VIGENCIA]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/dados-aula-turma/"
            "?ueCodigo=UE001&anoLetivo=2024"
            "&componentesCurriculares=1&semestre=1"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ue_codigo="UE001",
            ano_letivo="2024",
            componentes=["1"],
            semestre="1",
        )


class AnoTurmaAnoLetivoViewTest(SimpleTestCase):
    """Testes de GET L16 — grade curricular por ano letivo."""

    @patch(
        "apps.pedagogico.views.services.get_grade_curricular"
    )
    def test_200_retorna_grade(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_GRADE]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/ano-turma/ano-letivo/2024/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(2024)


class ComponentesSemAtribuicaoViewTest(SimpleTestCase):
    """Testes de GET L17 — componentes sem atribuição em turma."""

    @patch("apps.pedagogico.views.services.get_sem_atribuicao")
    def test_200_retorna_dados(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = ["Matematica", "Portugues"]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/turmas/T001/sem-atribuicao/637500000000000000/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo_turma="T001",
            data_base_tick="637500000000000000",
        )


class AgrupamentosCorrelacionadosViewTest(SimpleTestCase):
    """Testes de GET L13 — agrupamentos correlacionados."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_agrupamentos_correlacionados"
    )
    def test_200_sem_data_base(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/1/territorio-saber/agrupamentos-correlacionados/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(codigo=1, data_base=None)

    @patch(
        "apps.pedagogico.views.services"
        ".get_agrupamentos_correlacionados"
    )
    def test_200_com_data_base(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.get(
            f"{_PREFIX}/1/territorio-saber/agrupamentos-correlacionados/"
            "?dataBase=637500000000000000"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigo=1, data_base="637500000000000000"
        )


class AgrupamentosCorrelacionadosLoteViewTest(SimpleTestCase):
    """Testes de POST L14 — agrupamentos correlacionados em lote."""

    @patch(
        "apps.pedagogico.views.services"
        ".get_agrupamentos_correlacionados_lote"
    )
    def test_200_repassa_ids_e_data_base(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos-correlacionados/"
            "?dataBase=637500000000000000",
            data=[1, 2],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            ids=[1, 2], data_base="637500000000000000"
        )


class AgrupamentosTerritorioViewTest(SimpleTestCase):
    """Testes de POST L15 — agrupamentos de Território do Saber."""

    @patch("apps.pedagogico.views.services.get_agrupamentos")
    def test_200_repassa_ids(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_AGRUPAMENTO]
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/territorio-saber/agrupamentos/",
            data=[1, 2, 3],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with([1, 2, 3])
