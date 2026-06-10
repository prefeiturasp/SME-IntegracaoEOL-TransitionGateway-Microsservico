"""Valida as views do domínio de programas educacionais."""

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


class ProgramasEduUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_preserva_kwargs_turmas_pap(self) -> None:
        """Verifica os kwargs extraidos da rota de turmas PAP."""
        match = resolve("/api/alunos/turmas-pap/2026/ues/123/")
        self.assertEqual(
            match.kwargs, {"ano_letivo": 2026, "codigo_escola": "123"}
        )

    def test_preserva_kwargs_alunos_pap(self) -> None:
        """Verifica os kwargs extraidos da rota de alunos PAP."""
        match = resolve("/api/alunos/alunos-pap/2026/")
        self.assertEqual(match.kwargs, {"ano_letivo": 2026})

    def test_preserva_kwargs_pap_ano_corrente(self) -> None:
        """Verifica que a rota de PAP do ano corrente nao expoe kwargs."""
        match = resolve("/api/alunos/pap/ano-corrente/")
        self.assertEqual(match.kwargs, {})

    def test_preserva_kwargs_pap_ano_letivo(self) -> None:
        """Verifica os kwargs extraidos da rota de PAP por ano letivo."""
        match = resolve("/api/alunos/pap/ano-letivo/2026/")
        self.assertEqual(match.kwargs, {"ano_letivo": 2026})

    def test_preserva_kwargs_componentes_turmas_programa(self) -> None:
        """Verifica os kwargs extraidos da rota de componentes do aluno."""
        match = resolve(
            "/api/alunos/123/turmas-programa/2026/componentes-curriculares/"
        )
        self.assertEqual(
            match.kwargs, {"codigo_aluno": "123", "ano_letivo": 2026}
        )

    def test_preserva_kwargs_srm_paee_aluno(self) -> None:
        """Verifica os kwargs extraidos da rota de SRM/PAEE do aluno."""
        match = resolve("/api/alunos/srm-paee/aluno/123/")
        self.assertEqual(match.kwargs, {"codigo_aluno": "123"})

    def test_preserva_kwargs_turma_srm_e_regular(self) -> None:
        """Verifica os kwargs extraidos da rota de turma SRM e regular."""
        match = resolve(
            "/api/alunos/paee/turma-srm-e-regular/aluno/123/"
        )
        self.assertEqual(match.kwargs, {"codigo_aluno": "123"})


class ObterTurmasPapViewTest(SimpleTestCase):
    """Valida a resposta da view de turmas PAP."""

    @patch("apps.programasedu.views.services.listar_turmas_pap")
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a traduçãoo da resposta de turmas PAP."""
        mock_service.return_value = [{"codigo_turma": "X", "turma_nome": "1A"}]
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/turmas-pap/2026/ues/123/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), [{"codigoTurma": "X", "turmaNome": "1A"}]
        )
        mock_service.assert_called_once_with(
            ano_letivo=2026, codigo_escola="123"
        )

    @patch("apps.programasedu.views.services.listar_turmas_pap")
    def test_400_quando_codigo_escola_em_branco(
        self, mock_service: MagicMock
    ) -> None:
        """Verifica a rejeicao quando o codigo da escola vem em branco."""
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/turmas-pap/2026/ues/%20%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "É necessário informar o codigo_escola."},
        )
        mock_service.assert_not_called()


class VerificarAlunosPapViewTest(SimpleTestCase):
    """Valida a resposta da view de verificação de alunos PAP."""

    @patch("apps.programasedu.views.services.verificar_alunos_pap")
    def test_200_com_codigos_alunos_repetidos(
        self, mock_service: MagicMock
    ) -> None:
        """Verifica a verificacao de alunos PAP com codigos repetidos."""
        mock_service.return_value = [
            {
                "codigo_aluno": 1,
                "codigo_turma": 100,
                "codigo_componente": 50,
                "descricao": "PAP",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/alunos/alunos-pap/2026/",
            {"codigos_alunos": ["1", "2"]},
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(
            ano_letivo=2026, codigos_alunos=["1", "2"]
        )

    def test_400_quando_codigos_alunos_ausente(self) -> None:
        """Verifica a rejeicao quando os codigos dos alunos nao sao informados."""
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/alunos-pap/2026/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": ("É necessário informar ao menos um codigos_alunos.")},
        )


class ObterAlunosPapAnoCorrenteViewTest(SimpleTestCase):
    """Valida a resposta da view de alunos PAP do ano corrente."""

    @patch("apps.programasedu.views.services.listar_alunos_pap_ano_corrente")
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a resposta de alunos PAP do ano corrente."""
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/pap/ano-corrente/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with()


class ObterAlunosPapPorAnoLetivoViewTest(SimpleTestCase):
    """Valida a resposta da view de alunos PAP por ano letivo."""

    @patch("apps.programasedu.views.services.listar_alunos_pap_por_ano")
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a resposta de alunos PAP por ano letivo."""
        mock_service.return_value = [
            {
                "ano_letivo": 2026,
                "codigo_turma": 100,
                "codigo_ue": "U1",
                "codigo_dre": "D1",
                "codigo_aluno": 1,
                "componente_curricular_id": 50,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/pap/ano-letivo/2026/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(ano_letivo=2026)


class ObterComponentesCurricularesTurmasProgramaAlunoViewTest(SimpleTestCase):
    """Valida a resposta da view de componentes do aluno."""

    @patch(
        "apps.programasedu.views.services."
        "listar_componentes_turmas_programa_aluno"
    )
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a traducao da resposta de componentes do aluno."""
        mock_service.return_value = [
            {
                "codigo_aluno": "1",
                "codigo_turma": 100,
                "codigo_componente_curricular": 50,
                "nome_componente_curricular": "MATEMATICA",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/alunos/123/turmas-programa/2026/componentes-curriculares/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigoAluno": "1",
                    "codigoTurma": 100,
                    "codigoComponenteCurricular": 50,
                    "nomeComponenteCurricular": "MATEMATICA",
                }
            ],
        )
        mock_service.assert_called_once_with(
            codigo_aluno="123", ano_letivo=2026
        )


class ObterDadosSrmPaeeAlunoViewTest(SimpleTestCase):
    """Valida a resposta da view de SRM/PAEE colaborativo do aluno."""

    @patch("apps.programasedu.views.services.obter_dados_srm_paee_aluno")
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a traducao da resposta de SRM/PAEE do aluno."""
        mock_service.return_value = [
            {
                "codigo_turma": 100,
                "codigo_escola": "U1",
                "turno": "MANHA",
                "componente": "SRM",
                "codigo_componente": 999,
                "codigo_aluno": 1,
                "situacao_matricula": "ATIVA",
                "data_matricula": "2026-02-01T11:51:46.820000",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get("/api/alunos/srm-paee/aluno/123/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigoTurma": 100,
                    "codigoEscola": "U1",
                    "turno": "MANHA",
                    "componente": "SRM",
                    "codigoComponente": 999,
                    "codigoAluno": 1,
                    "situacaoMatricula": "ATIVA",
                    "dataMatricula": "2026-02-01T11:51:46.82",
                }
            ],
        )
        mock_service.assert_called_once_with(codigo_aluno="123")


class ObterTurmaSrmERegularDoAlunoViewTest(SimpleTestCase):
    """Valida a view de turmas SRM e regulares do aluno."""

    @patch(
        "apps.programasedu.views.services."
        "obter_turma_srm_e_regular_do_aluno"
    )
    def test_200_traduz_camelcase(self, mock_service: MagicMock) -> None:
        """Verifica a tradução camelCase da resposta composta."""
        mock_service.return_value = [
            {
                "codigo_aluno": 7360328,
                "tipo_turno": 1,
                "ano_letivo": 2026,
                "nome_aluno": "AGATHA",
                "nome_social_aluno": None,
                "codigo_situacao_matricula": 11,
                "situacao_matricula": "Deslocamento",
                "data_situacao": "2026-01-06T15:41:55.393000+00:00",
                "data_nascimento": "2025-11-05",
                "numero_aluno_chamada": "000",
                "codigo_turma": 3031432,
                "nome_responsavel": "DARA",
                "tipo_responsavel": 1,
                "celular_responsavel": "11989400396",
                "data_atualizacao_contato": "2025-01-23",
                "codigo_tipo_turma": 1,
                "turma_nome": "2B",
                "etapa_ensino": 5,
                "ciclo_ensino": 3,
                "desc_etapa_ensino": "FUND9A",
                "desc_ciclo_ensino": None,
                "data_atualizacao_tabela": "0001-01-01T00:00:00",
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/alunos/paee/turma-srm-e-regular/aluno/7360328/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(item["codigoAluno"], 7360328)
        self.assertEqual(item["tipoTurno"], 1)
        self.assertEqual(item["etapaEnsino"], 5)
        self.assertEqual(item["cicloEnsino"], 3)
        self.assertEqual(item["descEtapaEnsino"], "FUND9A")
        self.assertIsNone(item["descCicloEnsino"])
        self.assertEqual(item["celularResponsavel"], "11989400396")
        self.assertEqual(item["numeroAlunoChamada"], "000")
        self.assertEqual(item["tipoResponsavel"], "1")
        # UTC 15:41 → wall-clock de SP (UTC-3) 12:41 + Z, trim de zeros.
        self.assertEqual(item["dataSituacao"], "2026-01-06T12:41:55.393Z")
        # Data pura (naive) não sofre conversão de fuso.
        self.assertEqual(item["dataNascimento"], "2025-11-05T00:00:00Z")
        self.assertEqual(
            item["dataAtualizacaoContato"], "2025-01-23T00:00:00Z"
        )
        # Sentinela de data ausente (DateTime.MinValue), sem Z.
        self.assertEqual(
            item["dataAtualizacaoTabela"], "0001-01-01T00:00:00"
        )
        mock_service.assert_called_once_with(codigo_aluno="7360328")
