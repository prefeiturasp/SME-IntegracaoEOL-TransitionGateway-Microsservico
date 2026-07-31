"""Valida as views do domínio de matrículas."""

from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient


def _cliente_autenticado() -> APIClient:
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


def _request_error() -> httpx.RequestError:
    request = httpx.Request("GET", "https://sidecar.local/test")
    return httpx.ConnectError("Sidecar indisponivel", request=request)


class MatriculasUrlsTest(SimpleTestCase):
    """Valida os nomes dos parâmetros nas rotas."""

    def test_rota_matriculas(self) -> None:
        match = resolve("/api/v1/matriculas/")

        self.assertEqual(match.kwargs, {})

    def test_rota_anos_anteriores_sem_barra(self) -> None:
        match = resolve("/api/v1/matriculas/anos-anteriores")

        self.assertEqual(match.url_name, "matriculas-anos-anteriores")

    def test_rota_matriculas_quantidades_ue_legado(self) -> None:
        match = resolve("/api/matriculas/escolas/100001/quantidades")

        self.assertEqual(match.kwargs, {"ue_codigo": "100001"})

    def test_rota_matriculas_quantidades_dre_legado(self) -> None:
        match = resolve("/api/matriculas/escolas/dre/108800/quantidades")

        self.assertEqual(match.kwargs, {"dre_codigo": "108800"})

    def test_rota_escolas_quantidade_alunos(self) -> None:
        match = resolve("/api/escolas/100001/alunos/quantidade/")

        self.assertEqual(match.kwargs, {"codigo_escola": "100001"})

    def test_rota_escolas_quantidade_alunos_sem_barra(self) -> None:
        match = resolve("/api/escolas/100001/alunos/quantidade")

        self.assertEqual(match.kwargs, {"codigo_escola": "100001"})

    def test_rota_escolas_matriculas_aluno(self) -> None:
        match = resolve("/api/escolas/100001/aluno/1234567/matriculas/")

        self.assertEqual(
            match.kwargs,
            {"codigo_escola": "100001", "codigo_aluno": "1234567"},
        )

    def test_rota_escolas_matriculas_aluno_sem_barra(self) -> None:
        match = resolve("/api/escolas/100001/aluno/1234567/matriculas")

        self.assertEqual(
            match.kwargs,
            {"codigo_escola": "100001", "codigo_aluno": "1234567"},
        )

    def test_rota_escolas_matriculas_aluno_plural(self) -> None:
        match = resolve("/api/escolas/100001/alunos/1234567/matriculas/")

        self.assertEqual(
            match.kwargs,
            {"codigo_escola": "100001", "codigo_aluno": "1234567"},
        )


class MatriculasAnoAtualViewTest(SimpleTestCase):
    """Valida a view de matrículas do ano letivo."""

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_vazio_quando_params_camel_case(
        self, mock_service: MagicMock
    ) -> None:
        """Verifica que aliases camelCase não são aceitos na entrada."""
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_aceita_query_params_snake_case(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/?ano_letivo=2026&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with(
            ano_letivo=2026,
            ue_codigo="100001",
        )

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_vazio_quando_ano_letivo_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_200_vazio_quando_ue_codigo_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_400_quando_ano_letivo_invalido(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/?ano_letivo=abc&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "ano_letivo deve ser um inteiro válido."},
        )
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/?ano_letivo=2026&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(),
            {"detail": "Servico de matriculas indisponivel."},
        )

    def test_403_sem_autenticacao(self) -> None:
        client = APIClient()

        resp = client.get("/api/v1/matriculas/?anoLetivo=2026&ueCodigo=100001")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class MatriculasAnosAnterioresViewTest(SimpleTestCase):
    """Valida a consolidação de matrículas históricas."""

    @patch("apps.matriculas.views.services.get_matriculas_anos_anteriores")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {"turma_codigo": "54321", "quantidade": 27}
        ]
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/anos-anteriores"
            "?ano_letivo=2025&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), [{"turmaCodigo": "54321", "quantidade": 27}]
        )
        mock_service.assert_called_once_with(
            ano_letivo=2025,
            ue_codigo="100001",
        )

    @patch("apps.matriculas.views.services.get_matriculas_anos_anteriores")
    def test_200_vazio_quando_parametro_ausente(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/anos-anteriores?ano_letivo=2025"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_not_called()

    @patch("apps.matriculas.views.services.get_matriculas_anos_anteriores")
    def test_400_quando_ano_invalido(self, mock_service: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/anos-anteriores"
            "?ano_letivo=abc&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_service.assert_not_called()


class TotalMatriculasPorTurnoUeViewTest(SimpleTestCase):
    """Valida o endpoint legado M03."""

    _URL = "/api/matriculas/escolas/100001/quantidades"

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_ue")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_ue")
    def test_200_retorna_objeto_contrato(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = {
            "totalMatricula": 72,
            "turnos": [
                {
                    "turno": "Integral",
                    "tipoTurno": 6,
                    "quantidade": 72,
                }
            ],
        }
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {
                "totalMatricula": 72,
                "turnos": [
                    {
                        "turno": "Integral",
                        "tipoTurno": 6,
                        "quantidade": 72,
                    }
                ],
            },
        )
        mock_service.assert_called_once_with("100001")
        mock_fallback.assert_not_called()

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_ue")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_ue")
    def test_204_quando_sem_dados(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = []
        mock_fallback.return_value = None
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_fallback.assert_called_once_with("100001")

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_ue")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_ue")
    def test_200_quando_fallback_monta_contrato(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = []
        mock_fallback.return_value = {
            "totalMatricula": 72,
            "turnos": [
                {
                    "turno": "Integral",
                    "tipoTurno": 6,
                    "quantidade": 72,
                }
            ],
        }
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["totalMatricula"], 72)
        mock_fallback.assert_called_once_with("100001")

    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_ue")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class TotalMatriculasPorTurnoDreViewTest(SimpleTestCase):
    """Valida o endpoint legado M04."""

    _URL = "/api/matriculas/escolas/dre/108800/quantidades"

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_dre")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_dre")
    def test_200_retorna_lista_contrato(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = [
            {
                "totalMatriculas": 922,
                "codigoEolEscola": "000191",
                "turnos": [
                    {
                        "turno": "Manhã",
                        "tipoTurno": 1,
                        "quantidade": 256,
                    }
                ],
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "totalMatriculas": 922,
                    "codigoEolEscola": "000191",
                    "turnos": [
                        {
                            "turno": "Manhã",
                            "tipoTurno": 1,
                            "quantidade": 256,
                        }
                    ],
                }
            ],
        )
        mock_service.assert_called_once_with("108800")
        mock_fallback.assert_not_called()

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_dre")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_dre")
    def test_204_quando_sem_dados(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = []
        mock_fallback.return_value = []
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_fallback.assert_called_once_with("108800")

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_dre")
    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_dre")
    def test_200_quando_fallback_monta_contrato(
        self,
        mock_service: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_service.return_value = []
        mock_fallback.return_value = [
            {
                "codigoEolEscola": "100001",
                "totalMatriculas": 72,
                "turnos": [
                    {
                        "turno": "Integral",
                        "tipoTurno": 6,
                        "quantidade": 72,
                    }
                ],
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["totalMatriculas"], 72)
        mock_fallback.assert_called_once_with("108800")

    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_dre")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class QuantidadeAlunosPorTurmaEscolaViewTest(SimpleTestCase):
    """Valida o endpoint legado E05."""

    _URL = "/api/escolas/100001/alunos/quantidade/"

    @patch("apps.matriculas.views.services.get_quantidade_alunos_por_turma_escola")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [{"turma_codigo": "54321", "quantidade": 27}]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), [{"turmaCodigo": "54321", "quantidade": 27}]
        )
        mock_service.assert_called_once_with("100001")


class MatriculasAlunoEscolaViewTest(SimpleTestCase):
    """Valida o endpoint legado E24."""

    _URL = "/api/escolas/100001/aluno/1234567/matriculas/"

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {
                "codigo_aluno": 1234567,
                "nome_aluno": "Fulano",
                "nome_social_aluno": None,
                "codigo_situacao_matricula": 1,
                "situacao_matricula": "Ativo",
                "data_situacao": "2026-01-31",
                "codigo_turma": 9001,
                "codigo_matricula": 998877,
                "ano_letivo": 2026,
            }
        ]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoAluno"], 1234567)
        self.assertEqual(resp.json()[0]["codigoMatricula"], 998877)
        mock_service.assert_called_once_with("100001", "1234567")

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_200_rota_plural_reutiliza_mesma_view(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/100001/alunos/1234567/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with("100001", "1234567")

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_200_sem_barra_retorna_lista_vazia(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = []
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/400496/aluno/8577981/matriculas")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with("400496", "8577981")

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_400_quando_codigo_aluno_nao_numerico(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/100001/aluno/abc/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "O código da escola e do aluno são obrigatórios"},
        )
        mock_service.assert_not_called()
