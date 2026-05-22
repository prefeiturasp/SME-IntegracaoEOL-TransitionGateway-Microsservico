"""Valida as views do domínio de programas educacionais."""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
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


class ObterTurmasPapViewTest(SimpleTestCase):
    """Valida a resposta da view de turmas PAP."""

    @patch("apps.programasedu.views.services.listar_turmas_pap")
    def test_200(self, mock_service: MagicMock) -> None:
        """Verifica a traducao da resposta de turmas PAP."""
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
            {"detail": "E necessario informar o codigo_escola."},
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
            {"detail": ("E necessario informar ao menos um codigos_alunos.")},
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
