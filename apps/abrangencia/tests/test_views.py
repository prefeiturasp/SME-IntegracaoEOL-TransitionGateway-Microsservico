"""Valida as views do domínio de abrangência."""

from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_PREFIX = "/api/abrangencia/estrutura-vigente"

_ESTRUTURA: dict[str, Any] = {
    "dres": [
        {
            "abreviacao": "X",
            "codigo": "100000",
            "nome": "DIRETORIA REGIONAL FICTICIA",
            "ues": [
                {
                    "codigo": "000001",
                    "nome": "EMEF FICTICIA DE TESTE",
                    "codTipoEscola": 1,
                    "turmas": [
                        {
                            "ano": "5",
                            "anoLetivo": 2026,
                            "codigo": 9000001,
                            "tipoTurma": 1,
                            "modalidade": "Fundamental",
                            "codigoModalidade": 5,
                            "nomeTurma": "5A",
                            "semestre": 0,
                            "duracaoTurno": 6,
                            "tipoTurno": 1,
                            "dataFim": None,
                            "ehistorico": False,
                            "ensinoEspecial": False,
                            "etapaEJA": 0,
                            "serieEnsino": None,
                            "dataInicioTurma": None,
                            "extinta": False,
                            "situacao": None,
                            "ueCodigo": None,
                        }
                    ],
                }
            ],
        }
    ]
}

_ESTRUTURA_VAZIA: dict[str, Any] = {"dres": []}


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()
    client.force_authenticate(user=User(username="teste"))
    return client


class EstruturaVigentePorDreViewTest(SimpleTestCase):
    """Valida a view GET de estrutura vigente por DRE."""

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_dre")
    def test_200_retorna_estrutura(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _ESTRUTURA
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/100000/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["dres"][0]["codigo"], "100000")
        mock_svc.assert_called_once_with("100000")

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_dre")
    def test_204_quando_dres_vazio(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _ESTRUTURA_VAZIA
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/999999/")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        mock_svc.assert_called_once_with("999999")

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_dre")
    def test_400_quando_codigo_dre_em_branco(
        self, mock_svc: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.get(f"{_PREFIX}/%20/")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    def test_403_sem_api_key(self) -> None:
        resp = APIClient().get(f"{_PREFIX}/100000/")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class EstruturaVigenteViewTest(SimpleTestCase):
    """Valida a view POST de estrutura vigente por lista de turmas."""

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_200_retorna_estrutura(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _ESTRUTURA
        client = _cliente_autenticado()

        resp = client.post(f"{_PREFIX}/", [9000001], format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["dres"][0]["codigo"], "100000")
        mock_svc.assert_called_once_with([9000001])

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_204_quando_dres_vazio(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _ESTRUTURA_VAZIA
        client = _cliente_autenticado()

        resp = client.post(f"{_PREFIX}/", [9000001], format="json")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_400_quando_lista_vazia(self, mock_svc: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.post(f"{_PREFIX}/", [], format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_400_quando_apenas_codigos_invalidos(
        self, mock_svc: MagicMock
    ) -> None:
        client = _cliente_autenticado()

        resp = client.post(f"{_PREFIX}/", ["abc"], format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_400_quando_corpo_nao_e_lista(self, mock_svc: MagicMock) -> None:
        client = _cliente_autenticado()

        resp = client.post(f"{_PREFIX}/", {"codigo": 9000001}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        mock_svc.assert_not_called()

    @patch("apps.abrangencia.views.services.get_estrutura_vigente_por_turmas")
    def test_ignora_codigos_invalidos_na_lista(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = _ESTRUTURA
        client = _cliente_autenticado()

        resp = client.post(
            f"{_PREFIX}/", [9000001, "abc", None], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with([9000001])

    def test_403_sem_api_key(self) -> None:
        resp = APIClient().post(f"{_PREFIX}/", [9000001], format="json")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
