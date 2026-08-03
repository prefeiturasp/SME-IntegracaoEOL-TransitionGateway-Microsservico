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
            {"detail": "Serviço de matriculas indisponível."},
        )

    @patch("apps.matriculas.views.services.get_matriculas_ano_atual")
    def test_400_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            400, json={"detail": "Ano invalido"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/?ano_letivo=2026&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), {"detail": "Ano invalido"})

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

        resp = client.get("/api/v1/matriculas/anos-anteriores?ano_letivo=2025")

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

    @patch("apps.matriculas.views.services.get_matriculas_anos_anteriores")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/anos-anteriores?ano_letivo=2025&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.matriculas.views.services.get_matriculas_anos_anteriores")
    def test_500_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            500, json={"detail": "Erro interno"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(
            "/api/v1/matriculas/anos-anteriores?ano_letivo=2025&ue_codigo=100001"
        )

        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(resp.json(), {"detail": "Erro interno"})


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

    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_ue")
    def test_500_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            500, json={"detail": "Erro interno"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(resp.json(), {"detail": "Erro interno"})


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

    @patch("apps.matriculas.views.services.get_total_matriculas_por_turno_dre")
    def test_404_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            404, json={"detail": "DRE não encontrada"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), {"detail": "DRE não encontrada"})


class QuantidadeAlunosPorTurmaEscolaViewTest(SimpleTestCase):
    """Valida o endpoint legado E05."""

    _URL = "/api/escolas/100001/alunos/quantidade/"

    @patch(
        "apps.matriculas.views.services.get_quantidade_alunos_por_turma_escola"
    )
    def test_200_retorna_contrato_legado(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.return_value = [
            {"turma_codigo": "54321", "quantidade": 27}
        ]
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(), [{"turmaCodigo": "54321", "quantidade": 27}]
        )
        mock_service.assert_called_once_with("100001")

    @patch("apps.matriculas.views.services.get_quantidade_alunos_por_turma_escola")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.matriculas.views.services.get_quantidade_alunos_por_turma_escola")
    def test_400_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            400, json={"detail": "Código inválido"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json(), {"detail": "Código inválido"})

    def test_400_quando_codigo_escola_vazio(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/  /alunos/quantidade/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(), {"detail": "Código da escola obrigatório."}
        )


class MatriculasAlunoEscolaViewTest(SimpleTestCase):
    """Valida o endpoint legado E24."""

    _URL = "/api/escolas/100001/alunos/1234567/matriculas/"

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

        resp = client.get("/api/escolas/400496/alunos/8577981/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_service.assert_called_once_with("400496", "8577981")

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_400_quando_codigo_aluno_nao_numerico(
        self, mock_service: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/100001/alunos/abc/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "O código da escola e do aluno são obrigatórios"},
        )
        mock_service.assert_not_called()

    def test_400_quando_codigo_escola_vazio(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/  /alunos/1234567/matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "O código da escola e do aluno são obrigatórios"},
        )

    def test_400_quando_codigo_aluno_vazio(self) -> None:
        client = _cliente_autenticado()

        resp = client.get("/api/escolas/100001/alunos/  /matriculas/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(),
            {"detail": "O código da escola e do aluno são obrigatórios"},
        )

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_503_quando_sidecar_indisponivel(
        self, mock_service: MagicMock
    ) -> None:
        mock_service.side_effect = _request_error()
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("apps.matriculas.views.services.get_matriculas_aluno_escola")
    def test_404_quando_sidecar_retorna_erro_http(
        self, mock_service: MagicMock
    ) -> None:
        request = httpx.Request("GET", "https://sidecar/test")
        response = httpx.Response(
            404, json={"detail": "Aluno não encontrado"}, request=request
        )
        mock_service.side_effect = httpx.HTTPStatusError(
            "Erro", request=request, response=response
        )
        client = _cliente_autenticado()

        resp = client.get(self._URL)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.json(), {"detail": "Aluno não encontrado"})


class FuncoesAuxiliaresTest(SimpleTestCase):
    """Testes das funções auxiliares de views."""

    def test_to_int_com_string_valida(self) -> None:
        from apps.matriculas.views import _to_int

        self.assertEqual(_to_int("123"), 123)
        self.assertEqual(_to_int("0"), 0)

    def test_to_int_com_string_invalida(self) -> None:
        from apps.matriculas.views import _to_int

        self.assertIsNone(_to_int("abc"))
        self.assertIsNone(_to_int(""))

    def test_to_int_com_none(self) -> None:
        from apps.matriculas.views import _to_int

        self.assertIsNone(_to_int(None))

    def test_extrair_codigo_ue_com_string(self) -> None:
        from apps.matriculas.views import _extrair_codigo_ue

        self.assertEqual(_extrair_codigo_ue("100001"), "100001")
        self.assertEqual(_extrair_codigo_ue("  100002  "), "100002")
        self.assertIsNone(_extrair_codigo_ue(""))
        self.assertIsNone(_extrair_codigo_ue("   "))

    def test_extrair_codigo_ue_com_dict(self) -> None:
        from apps.matriculas.views import _extrair_codigo_ue

        self.assertEqual(_extrair_codigo_ue({"codigo_ue": "100001"}), "100001")
        self.assertEqual(_extrair_codigo_ue({"codigoUE": "100002"}), "100002")
        self.assertEqual(_extrair_codigo_ue({"ueCodigo": "100003"}), "100003")
        self.assertEqual(_extrair_codigo_ue({"codigo_eol": "100004"}), "100004")
        self.assertEqual(_extrair_codigo_ue({"codigoEol": "100005"}), "100005")
        self.assertEqual(
            _extrair_codigo_ue({"codigoEolEscola": "100006"}), "100006"
        )
        self.assertEqual(
            _extrair_codigo_ue({"codigo_escola": "100007"}), "100007"
        )
        self.assertEqual(
            _extrair_codigo_ue({"codigoEscola": "100008"}), "100008"
        )

    def test_extrair_codigo_ue_com_tipo_invalido(self) -> None:
        from apps.matriculas.views import _extrair_codigo_ue

        self.assertIsNone(_extrair_codigo_ue(123))
        self.assertIsNone(_extrair_codigo_ue([]))
        self.assertIsNone(_extrair_codigo_ue(None))

    def test_extrair_codigos_ue_dre_com_lista(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        result = _extrair_codigos_ue_dre(
            [
                {"codigo_ue": "100001"},
                {"codigoUE": "100002"},
                "100003",
            ]
        )
        self.assertEqual(result, ["100001", "100002", "100003"])

    def test_extrair_codigos_ue_dre_com_dict_codigos_ue(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        result = _extrair_codigos_ue_dre(
            {"codigos_ue": ["100001", "100002", "100003"]}
        )
        self.assertEqual(result, ["100001", "100002", "100003"])

    def test_extrair_codigos_ue_dre_com_dict_unico(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        result = _extrair_codigos_ue_dre({"codigo_ue": "100001"})
        self.assertEqual(result, ["100001"])

    def test_extrair_codigos_ue_dre_remove_duplicatas(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        result = _extrair_codigos_ue_dre(
            ["100001", "100002", "100001", "100003"]
        )
        self.assertEqual(result, ["100001", "100002", "100003"])

    def test_extrair_codigos_ue_dre_ignora_invalidos(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        result = _extrair_codigos_ue_dre([None, 123, {}, "100001"])
        self.assertEqual(result, ["100001"])

    def test_extrair_codigos_ue_dre_com_tipo_invalido(self) -> None:
        from apps.matriculas.views import _extrair_codigos_ue_dre

        self.assertEqual(_extrair_codigos_ue_dre("invalido"), [])
        self.assertEqual(_extrair_codigos_ue_dre(123), [])

    def test_agregar_turnos_por_ue_lista_vazia(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        self.assertIsNone(_agregar_turnos_por_ue([]))

    def test_agregar_turnos_por_ue_sem_ativos(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        alunos = [
            {"codigo_situacao_matricula": 2, "tipo_turno": 1},
            {"codigo_situacao_matricula": 3, "tipo_turno": 1},
        ]
        self.assertIsNone(_agregar_turnos_por_ue(alunos))

    def test_agregar_turnos_por_ue_sem_tipo_turno(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        alunos = [
            {"codigo_situacao_matricula": 1},
            {"codigo_situacao_matricula": 1, "tipo_turno": None},
        ]
        self.assertIsNone(_agregar_turnos_por_ue(alunos))

    def test_agregar_turnos_por_ue_item_nao_dict(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        alunos = [
            "invalido",
            None,
            123,
            {"codigo_situacao_matricula": 1, "tipo_turno": 1, "codigo_matricula": "1"},
        ]
        result = _agregar_turnos_por_ue(alunos)
        assert result is not None
        self.assertEqual(result["totalMatricula"], 1)

    def test_agregar_turnos_por_ue_remove_duplicatas(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        alunos = [
            {
                "codigo_situacao_matricula": 1,
                "tipo_turno": 1,
                "codigo_matricula": "999",
            },
            {
                "codigo_situacao_matricula": 1,
                "tipo_turno": 1,
                "codigo_matricula": "999",
            },
        ]
        result = _agregar_turnos_por_ue(alunos)
        assert result is not None
        self.assertEqual(result["totalMatricula"], 1)

    def test_agregar_turnos_por_ue_sem_codigo_matricula(self) -> None:
        from apps.matriculas.views import _agregar_turnos_por_ue

        alunos = [
            {"codigo_situacao_matricula": 1, "tipo_turno": 1},
            {"codigo_situacao_matricula": 1, "tipo_turno": 2},
        ]
        result = _agregar_turnos_por_ue(alunos)
        assert result is not None
        self.assertEqual(result["totalMatricula"], 2)
        self.assertEqual(len(result["turnos"]), 2)

    def test_ano_letivo_corrente(self) -> None:
        from datetime import datetime
        from unittest.mock import patch

        from apps.matriculas.views import _ano_letivo_corrente

        with patch("apps.matriculas.views.timezone.localdate") as mock_date:
            mock_date.return_value = datetime(2026, 7, 31).date()
            self.assertEqual(_ano_letivo_corrente(), "2026")

    @patch("apps.matriculas.views._agregar_turnos_por_ue")
    @patch("apps.matriculas.views.alunos_services.get_alunos_da_ue")
    @patch("apps.matriculas.views._ano_letivo_corrente")
    def test_fallback_total_matriculas_por_turno_ue_retorna_agregado(
        self,
        mock_ano: MagicMock,
        mock_get_alunos: MagicMock,
        mock_agregar: MagicMock,
    ) -> None:
        from apps.matriculas.views import (
            _fallback_total_matriculas_por_turno_ue,
        )

        mock_ano.return_value = "2026"
        mock_get_alunos.return_value = [
            {"codigo_situacao_matricula": 1, "tipo_turno": 1}
        ]
        mock_agregar.return_value = {
            "totalMatricula": 1,
            "turnos": [{"turno": "Manhã", "tipoTurno": 1, "quantidade": 1}],
        }

        result = _fallback_total_matriculas_por_turno_ue("100001")

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["totalMatricula"], 1)
        mock_get_alunos.assert_called_once_with("100001", "2026")
        mock_agregar.assert_called_once()

    @patch("apps.matriculas.views.alunos_services.get_alunos_da_ue")
    @patch("apps.matriculas.views._ano_letivo_corrente")
    def test_fallback_total_matriculas_por_turno_ue_retorna_none_sem_alunos(
        self,
        mock_ano: MagicMock,
        mock_get_alunos: MagicMock,
    ) -> None:
        from apps.matriculas.views import (
            _fallback_total_matriculas_por_turno_ue,
        )

        mock_ano.return_value = "2026"
        mock_get_alunos.return_value = []

        result = _fallback_total_matriculas_por_turno_ue("100001")

        self.assertIsNone(result)

    @patch("apps.matriculas.views._fallback_total_matriculas_por_turno_ue")
    @patch("apps.matriculas.views._extrair_codigos_ue_dre")
    @patch("apps.matriculas.views.institucional_services.get_ues_por_dre")
    def test_fallback_total_matriculas_por_turno_dre_agrega_escolas(
        self,
        mock_get_ues: MagicMock,
        mock_extrair: MagicMock,
        mock_fallback_ue: MagicMock,
    ) -> None:
        from apps.matriculas.views import (
            _fallback_total_matriculas_por_turno_dre,
        )

        mock_get_ues.return_value = [{"codigo_ue": "100001"}]
        mock_extrair.return_value = ["100001", "100002"]
        mock_fallback_ue.side_effect = [
            {
                "totalMatricula": 10,
                "turnos": [
                    {"turno": "Manhã", "tipoTurno": 1, "quantidade": 10}
                ],
            },
            None,
        ]

        result = _fallback_total_matriculas_por_turno_dre("108800")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["codigoEolEscola"], "100001")
        self.assertEqual(result[0]["totalMatriculas"], 10)
        mock_get_ues.assert_called_once_with("108800")
        mock_extrair.assert_called_once()
        self.assertEqual(mock_fallback_ue.call_count, 2)
