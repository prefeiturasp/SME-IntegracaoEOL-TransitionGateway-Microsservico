"""Valida as views do domínio institucional."""

from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_DRE = {"codigoDRE": "BT", "nomeDRE": "DRE BUTANTA", "siglaDRE": "DRE-BT"}

# Escola retornada pelo sidecar, com campos extras a serem filtrados.
_ESCOLA_RESUMO = {
    "codigoEscola": "019308",
    "nomeEscola": "EMEF TESTE",
    "codigoDRE": "BT",
    "tipoEscola": "EMEF",
    "siglaTipoEscola": "EMEF",
    "nomeDRE": "DRE BUTANTA",
    "siglaDRE": "DRE-BT",
    "codigoSubprefeitura": "1",
    "nomeSubprefeitura": "BUTANTA",
    "tipoEscolaId": 1,
    "tipoUnidadeId": 1,
    "subprefeituraId": 1,
    "dreId": "abc-123",
    "codigoIntegracao": None,
}

# Detalhe de escola (reaproveita os dados do resumo).
_ESCOLA = {**_ESCOLA_RESUMO}

_ESCOLA_POR_TIPO = {
    "codigoEscola": "019308",
    "nomeEscola": "EMEF TESTE",
    "codigoDRE": "BT",
    "tipoEscola": "EMEF",
    "siglaTipoEscola": "EMEF",
}

_DADOS_ESCOLA = {
    "nomeDRE": "DIRETORIA REGIONAL TESTE",
    "siglaDRE": "DRE-T",
    "codigoDRE": "000000",
    "codigoINEP": "00000000",
    "siglaTipoEscola": "EMEF",
    "nome": "NOME ESCOLA TESTE",
    "nomeExibicao": "NOME EXIBICAO TESTE",
    "codigo": "000000",
}

_SUBPREFEITURA = {
    "codigoSubprefeitura": "00",
    "nomeSubprefeitura": "SUBPREFEITURA TESTE",
}

_TIPO_ESCOLA = {
    "codigo": 1,
    "descricaoSigla": "EMEF",
    "dtAtualizacao": "2026-04-17T00:00:00",
}

_EQUIPAMENTO = {
    "cd_equipamento": "108100",
    "nm_exibicao_equipamento": "DRE - BT",
    "nm_equipamento": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
    "cd_tp_equipamento": 3,
    "dc_tp_equipamento": "UNIDADE ADMINISTRATIVA",
    "cd_tp_escola": 0,
    "dc_tipo_escola": "",
    "sg_tp_escola": "",
    "cd_diretoria_referencia": "108100",
    "nm_diretoria_referencia": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
    "nm_exibicao_diretoria_referencia": "DRE - BT",
    "cd_diretoria_portal": "108100",
    "nm_diretoria_portal": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
    "nm_exibicao_diretoria_portal": "DRE - BT",
    "cd_logradouro": 127140,
    "logradouro": "RUA PADRE EUGÊNIO LOPES Nº 361",
    "bairro": "VILA PROGREDIOR",
    "codigoSubprefeitura": "50",
    "nomeSubprefeitura": "BUTANTA",
    "ehCeu": False,
}


def _cliente_autenticado() -> APIClient:
    """Cria um APIClient autenticado para os testes."""
    client = APIClient()
    client.force_authenticate(user=User(username="test-user"))
    return client


def _httpx_404() -> httpx.HTTPStatusError:
    """Cria um HTTPStatusError simulando resposta 404 do sidecar."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    return httpx.HTTPStatusError(
        "404", request=MagicMock(), response=mock_response
    )


class DREListViewTest(SimpleTestCase):
    """Valida a view de listagem de DREs."""

    @patch("apps.institucional.views.services.get_dres")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().get("/api/DREs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_dres")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/DREs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_dres_por_codigos")
    def test_post_200_retorna_dres(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().post(
            "/api/DREs/", ["108100"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(["108100"])

    @patch("apps.institucional.views.services.get_dres_por_codigos")
    def test_post_204_sem_registros(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = None
        resp = _cliente_autenticado().post(
            "/api/DREs/", ["INEXISTENTE"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DREDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de DRE."""

    @patch("apps.institucional.views.services.get_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().get("/api/DREs/108100/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_dre")
    def test_404_quando_sidecar_retorna_404(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dre")
    def test_404_quando_array_vazio(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/DREs/108100/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class SubprefeiturasPorDREViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_SUBPREFEITURA]
        resp = _cliente_autenticado().get(
            "/api/DREs/108100/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class EscolasPorDREViewTest(SimpleTestCase):
    """Valida a view de escolas por DRE."""

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_ESCOLA_RESUMO]
        resp = _cliente_autenticado().get("/api/DREs/108100/escola/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/escola/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class EscolasPorDREeTipoViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_200_filtra_campos_do_contrato(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.return_value = [_ESCOLA_POR_TIPO]
        resp = _cliente_autenticado().get(
            "/api/DREs/108100/escolas/EMEF/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100", "EMEF")
        payload = resp.json()[0]
        self.assertIn("codigoEscola", payload)
        self.assertIn("nomeEscola", payload)
        self.assertIn("codigoDRE", payload)
        self.assertNotIn("tipoEscola", payload)

    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/escolas/EMEF/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class UesPorDREViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_200_retorna_lista_codigos(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = ["019251", "019252"]
        resp = _cliente_autenticado().get("/api/DREs/108100/ues/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/ues/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class UnidadesPorDREViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [{"codigoEol": "019308"}]
        resp = _cliente_autenticado().get("/api/DREs/108100/unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/unidades/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class DadosEscolaViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _DADOS_ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/dados/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_404_quando_sidecar_retorna_404(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/escolas/dados/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_404_quando_retorna_none(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = None
        resp = _cliente_autenticado().get("/api/escolas/dados/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class TiposEscolasViewTest(SimpleTestCase):
    @patch("apps.institucional.views.services.get_tipos_escolas")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_TIPO_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/tiposEscolas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_tipos_escolas")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/tiposEscolas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])


class EscolaDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de escola."""

    @patch("apps.institucional.views.services.get_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = _ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_escola")
    def test_404_quando_escola_inexistente(
        self, mock_svc: MagicMock
    ) -> None:
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/escolas/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class EquipamentosViewTest(SimpleTestCase):
    """Valida a view de equipamentos."""

    @patch("apps.institucional.views.services.get_equipamentos")
    def test_200_sem_filtros(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_EQUIPAMENTO]
        resp = _cliente_autenticado().get("/api/escolas/equipamentos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigos_subprefeitura=None,
            codigos_dre=None,
            tipos_unidade=None,
            tipos_escola=None,
            nome_escola=None,
            codigo_eol=None,
        )

    @patch("apps.institucional.views.services.get_equipamentos")
    def test_200_com_filtro_codigo_eol(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = [_EQUIPAMENTO]
        resp = _cliente_autenticado().get(
            "/api/escolas/equipamentos/?codigoEol=019716"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigos_subprefeitura=None,
            codigos_dre=None,
            tipos_unidade=None,
            tipos_escola=None,
            nome_escola=None,
            codigo_eol="019716",
        )

    @patch("apps.institucional.views.services.get_equipamentos")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/equipamentos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
