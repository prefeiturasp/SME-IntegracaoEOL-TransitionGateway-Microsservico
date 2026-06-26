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
    "tipoEscola": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
    "siglaTipoEscola": "EMEF",
    "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
    "siglaDRE": "DRE - BT",
    "codigoSubprefeitura": "50",
    "nomeSubprefeitura": "BUTANTA",
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


def _httpx_status_error(status_code: int, body: dict) -> httpx.HTTPStatusError:
    """Cria um HTTPStatusError com corpo JSON parametrizável."""

    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = body
    mock_response.text = body.get("detail", "")
    mock_response.reason_phrase = body.get("detail", "Erro")
    return httpx.HTTPStatusError(
        str(status_code), request=MagicMock(), response=mock_response
    )


class DREListViewTest(SimpleTestCase):
    """Valida a view de listagem de DREs."""

    @patch("apps.institucional.views.services.get_dres")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de DREs do sidecar."""
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().get("/api/DREs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_dres")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista vazia quando o sidecar não tem DREs."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/DREs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_dres_por_codigos")
    def test_post_200_retorna_dres(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com as DREs filtradas pelos códigos do body."""
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().post(
            "/api/DREs/", ["108100"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(["108100"])

    @patch("apps.institucional.views.services.get_dres_por_codigos")
    def test_post_204_sem_registros(self, mock_svc: MagicMock) -> None:
        """Retorna 204 quando nenhuma DRE é encontrada para os códigos."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().post(
            "/api/DREs/", ["INEXISTENTE"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DREDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de DRE."""

    @patch("apps.institucional.views.services.get_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().get("/api/DREs/108100/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_dre")
    def test_404_quando_sidecar_retorna_404(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dre")
    def test_404_quando_array_vazio(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar devolve array vazio."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/DREs/108100/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/")


class SubprefeiturasPorDREViewTest(SimpleTestCase):
    """Valida a view de subprefeituras por DRE."""

    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_SUBPREFEITURA]
        resp = _cliente_autenticado().get("/api/DREs/108100/subprefeituras/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/subprefeituras/")


class EscolasPorDREViewTest(SimpleTestCase):
    """Valida a view de escolas por DRE."""

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_ESCOLA_RESUMO]
        resp = _cliente_autenticado().get("/api/DREs/108100/escola/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/escola/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/escola/")


class EscolasPorDREeTipoViewTest(SimpleTestCase):
    """Valida a view de escolas por DRE e tipo de escola."""

    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_200_filtra_campos_do_contrato(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os campos do contrato de escola por DRE e tipo."""
        mock_svc.return_value = [_ESCOLA_POR_TIPO]
        resp = _cliente_autenticado().get("/api/DREs/108100/escolas/EMEF/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100", "EMEF")
        payload = resp.json()[0]
        self.assertIn("codigoEscola", payload)
        self.assertIn("nomeEscola", payload)
        self.assertIn("codigoDRE", payload)
        self.assertIn("tipoEscola", payload)
        self.assertIn("siglaTipoEscola", payload)
        self.assertIn("nomeDRE", payload)
        self.assertIn("siglaDRE", payload)
        self.assertIn("codigoSubprefeitura", payload)
        self.assertIn("nomeSubprefeitura", payload)

    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/escolas/EMEF/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/escolas/EMEF/")


class UesPorDREViewTest(SimpleTestCase):
    """Valida a view de códigos de UEs por DRE."""

    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_200_retorna_lista_codigos(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de códigos de UEs da DRE."""
        mock_svc.return_value = ["019251", "019252"]
        resp = _cliente_autenticado().get("/api/DREs/108100/ues/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/ues/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/ues/")


class UnidadesPorDREViewTest(SimpleTestCase):
    """Valida a view de unidades administrativas por DRE."""

    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de unidades administrativas da DRE."""
        mock_svc.return_value = [{"codigoEol": "019308"}]
        resp = _cliente_autenticado().get("/api/DREs/108100/unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("108100")

    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/DREs/INEXISTENTE/unidades/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/108100/unidades/")


class DadosEscolaViewTest(SimpleTestCase):
    """Valida a view de dados completos de escola."""

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da escola ao service."""
        mock_svc.return_value = _DADOS_ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/dados/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_quando_retorna_lista_com_dict(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 200 usando o primeiro item da lista do service."""
        mock_svc.return_value = [_DADOS_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/dados/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("nomeDRE", resp.json())

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_quando_item_nao_e_dict(self, mock_svc: MagicMock) -> None:
        """Retorna 200 quando o item da lista não é um dicionário."""
        mock_svc.return_value = ["valor_escalar"]
        resp = _cliente_autenticado().get("/api/escolas/dados/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_404_quando_sidecar_retorna_404(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/escolas/dados/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_404_quando_retorna_none(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o service devolve None."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get("/api/escolas/dados/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/escolas/dados/019308/")


class TiposEscolasViewTest(SimpleTestCase):
    """Valida a view de tipos de escola."""

    @patch("apps.institucional.views.services.get_tipos_escolas")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de tipos de escola do sidecar."""
        mock_svc.return_value = [_TIPO_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/tiposEscolas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_tipos_escolas")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista vazia quando não há tipos de escola."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/tiposEscolas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])


class EscolaDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de escola."""

    @patch("apps.institucional.views.services.get_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da escola ao service."""
        mock_svc.return_value = _ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_escola")
    def test_200_quando_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 usando o primeiro item da lista do service."""
        mock_svc.return_value = [_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @patch("apps.institucional.views.services.get_escola")
    def test_404_quando_escola_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get("/api/escolas/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_escola")
    def test_404_quando_item_vazio(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o service devolve lista vazia."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/999999/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_escola")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/escolas/019308/")


class EquipamentosViewTest(SimpleTestCase):
    """Valida a view de equipamentos."""

    @patch("apps.institucional.views.services.get_equipamentos")
    def test_200_sem_filtros(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com filtros não informados definidos como None."""
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
        """Retorna 200 repassando o filtro codigoEol ao service."""
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
        """Retorna 200 com lista vazia quando não há equipamentos."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/equipamentos/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])


class TodasUnidadesViewTest(SimpleTestCase):
    """Valida a view de todas as unidades educacionais."""

    @patch("apps.institucional.views.services.get_todas_unidades")
    def test_200_retorna_lista_unidades(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista de todas as unidades."""
        mock_unidade = {
            "codigoEscola": "400496",
            "nomeEscola": "13 DE MAIO",
            "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
            "siglaDRE": "DRE - IP",
            "codigoDRE": "BT",
            "tipoEscola": "CENTRO DE EDUCACAO INFANTIL DIRETO",
            "siglaTipoEscola": "CEI DIRET",
            "codigoTipoEscola": 10,
            "tipoEscolaId": 10,
        }
        mock_svc.return_value = [mock_unidade]
        resp = _cliente_autenticado().get("/api/escolas/todas-unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0], {
            "codigoEscola": "400496",
            "nomeEscola": "13 DE MAIO",
            "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
            "siglaDRE": "DRE - IP",
            "codigoDRE": "BT",
            "tipoEscola": "CENTRO DE EDUCACAO INFANTIL DIRETO",
            "siglaTipoEscola": "CEI DIRET",
        })
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_todas_unidades")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista vazia quando não há unidades."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/todas-unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_todas_unidades")
    def test_502_quando_servico_institucional_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o serviço institucional é indisponível."""
        mock_svc.side_effect = httpx.RequestError("Connection error")
        resp = _cliente_autenticado().get("/api/escolas/todas-unidades/")
        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("indisponível", resp.json()["detail"])


class TiposUnidadeEducacaoViewTest(SimpleTestCase):
    """Valida a view de tipos de unidade educacional."""

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_200_retorna_lista_tipos(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista de tipos de unidade educacional."""
        mock_svc.return_value = ["ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL"]
        resp = _cliente_autenticado().get("/api/escolas/tipos_unidade_educacao/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0], "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL")
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista vazia quando não há tipos."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get("/api/escolas/tipos_unidade_educacao/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_502_quando_servico_institucional_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o serviço institucional é indisponível."""
        mock_svc.side_effect = httpx.RequestError("Connection error")
        resp = _cliente_autenticado().get("/api/escolas/tipos_unidade_educacao/")
        self.assertEqual(resp.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("indisponível", resp.json()["detail"])


class UnidadeEolViewTest(SimpleTestCase):
    """Valida a view de unidade EOL."""

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_200_retorna_unidade(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os dados resumidos da unidade."""
        mock_svc.return_value = {
            "codigo": "019308",
            "sigla": "EMEF",
            "nomeUnidade": "EMEF TESTE",
            "tipo": 1,
            "codigoReferencia": "019308",
        }
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/019308/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_204_quando_sidecar_nao_retorna_conteudo(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar não encontra a unidade."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/000000/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_204_quando_sidecar_retorna_404(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar responde 404 para unidade ausente."""
        mock_svc.side_effect = _httpx_status_error(
            404, {"detail": "Unidade EOL não encontrada."}
        )
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/000000/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class SincronizacoesInstitucionaisViewTest(SimpleTestCase):
    """Valida a view de sincronizações institucionais."""

    @patch("apps.institucional.views.services.get_sincronizacoes_institucionais")
    def test_200_retorna_sincronizacao(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os dados da sincronização institucional."""
        mock_svc.return_value = {
            "ueCodigo": "019308",
            "dataAtualizacao": "2019-05-06T14:42:12.843",
            "ueNome": "EMEF TESTE",
            "dreCodigo": 108100,
            "tipoEscolaCodigo": 1,
            "dreId": "108100",
        }
        resp = _cliente_autenticado().get(
            "/api/escolas/019308/sincronizacoes-institucionais/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {
                "ueCodigo": "019308",
                "dataAtualizacao": "2019-05-06T14:42:12.843",
                "dreCodigo": 108100,
                "ueNome": "EMEF TESTE",
                "tipoEscolaCodigo": 1,
            },
        )
        mock_svc.assert_called_once_with("019308")

    @patch("apps.institucional.views.services.get_sincronizacoes_institucionais")
    def test_204_quando_sidecar_nao_retorna_conteudo(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar não encontra a sincronização."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get(
            "/api/escolas/000000/sincronizacoes-institucionais/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.institucional.views.services.get_sincronizacoes_institucionais")
    def test_204_quando_sidecar_retorna_404(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar responde 404 para sincronização ausente."""
        mock_svc.side_effect = _httpx_status_error(
            404, {"detail": "Unidade não encontrada."}
        )
        resp = _cliente_autenticado().get(
            "/api/escolas/000000/sincronizacoes-institucionais/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class UnidadesParceirasViewTest(SimpleTestCase):
    """Valida a view de unidades parceiras."""

    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_200_retorna_lista_parceiras(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de unidades parceiras."""
        mock_svc.return_value = [
            {"codigo": "019308", "nome": "UE PARCEIRA", "email": None}
        ]
        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", ["019308"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(["019308"])

    @patch("apps.institucional.views.services.get_dados_escola")
    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_200_complementa_retorno_quando_sidecar_retorna_vazio(
        self, mock_post: MagicMock, mock_dados: MagicMock
    ) -> None:
        """Retorna dados da UE quando a lista de parceiras vem vazia."""
        mock_post.return_value = []
        mock_dados.return_value = {
            "codigo": "092797",
            "siglaTipoEscola": "EMEF",
            "nome": "JULIO MESQUITA",
            "email": "emefjmesquita@sme.prefeitura.sp.gov.br",
        }

        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", ["092797"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigo": "092797",
                    "nome": "EMEF JULIO MESQUITA",
                    "email": "emefjmesquita@sme.prefeitura.sp.gov.br",
                }
            ],
        )
        mock_post.assert_called_once_with(["092797"])
        mock_dados.assert_called_once_with("092797")

    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_400_quando_sidecar_retorna_400(self, mock_svc: MagicMock) -> None:
        """Retorna 400 quando o sidecar valida a lista como inválida."""
        mock_svc.side_effect = _httpx_status_error(
            400, {"detail": "Lista de códigos é obrigatória."}
        )
        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", [], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(), {"detail": "Lista de códigos é obrigatória."}
        )
