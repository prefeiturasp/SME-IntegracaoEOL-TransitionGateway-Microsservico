"""Valida as views do domínio institucional."""

from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient

_DRE = {"codigoDRE": "X1", "nomeDRE": "DRE FICTICIA UM", "siglaDRE": "DRE-X1"}

# Escola retornada pelo sidecar, com campos extras a serem filtrados.
_ESCOLA_RESUMO = {
    "codigoEscola": "000001",
    "nomeEscola": "EMEF TESTE",
    "codigoDRE": "X1",
    "tipoEscola": "EMEF",
    "siglaTipoEscola": "EMEF",
    "nomeDRE": "DRE FICTICIA UM",
    "siglaDRE": "DRE-X1",
    "codigoSubprefeitura": "1",
    "nomeSubprefeitura": "SUBPREFEITURA FICTICIA UM",
    "tipoEscolaId": 1,
    "tipoUnidadeId": 1,
    "subprefeituraId": 1,
    "dreId": "abc-123",
    "codigoIntegracao": None,
}

# Detalhe de escola (reaproveita os dados do resumo).
_ESCOLA = {**_ESCOLA_RESUMO}

_ESCOLA_POR_TIPO = {
    "codigoEscola": "000001",
    "nomeEscola": "EMEF TESTE",
    "codigoDRE": "X1",
    "tipoEscola": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
    "siglaTipoEscola": "EMEF",
    "nomeDRE": "DIRETORIA REGIONAL FICTICIA UM",
    "siglaDRE": "DRE - X1",
    "codigoSubprefeitura": "50",
    "nomeSubprefeitura": "SUBPREFEITURA FICTICIA UM",
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

_ESCOLA_SIGPAE = {
    "codigoEscola": "000001",
    "nomeEscola": "EMEF TESTE",
    "codigoDRE": "100000",
    "tipoEscola": "EMEF",
    "siglaTipoEscola": "EMEF",
    "nomeDRE": "DRE FICTICIA UM",
    "siglaDRE": "DRE-X1",
    "codigoSubprefeitura": "50",
    "nomeSubprefeitura": "SUBPREFEITURA FICTICIA UM",
}

_UNIDADE_CODIGO_INTEGRACAO = {
    "codigoUe": "000001",
    "nomeUe": "EMEF TESTE",
    "codigoIntegracao": None,
}

_TIPO_ESCOLA = {
    "codigo": 1,
    "descricaoSigla": "EMEF",
    "dtAtualizacao": "2026-04-17T00:00:00",
}

_EQUIPAMENTO = {
    "cd_equipamento": "100000",
    "nm_exibicao_equipamento": "DRE - X1",
    "nm_equipamento": "DIRETORIA REGIONAL FICTICIA UM",
    "cd_tp_equipamento": 3,
    "dc_tp_equipamento": "UNIDADE ADMINISTRATIVA",
    "cd_tp_escola": 0,
    "dc_tipo_escola": "",
    "sg_tp_escola": "",
    "cd_diretoria_referencia": "100000",
    "nm_diretoria_referencia": "DIRETORIA REGIONAL FICTICIA UM",
    "nm_exibicao_diretoria_referencia": "DRE - X1",
    "cd_diretoria_portal": "100000",
    "nm_diretoria_portal": "DIRETORIA REGIONAL FICTICIA UM",
    "nm_exibicao_diretoria_portal": "DRE - X1",
    "cd_logradouro": 10001,
    "logradouro": "RUA FICTICIA Nº 200",
    "bairro": "BAIRRO FICTICIO DOIS",
    "codigoSubprefeitura": "50",
    "nomeSubprefeitura": "SUBPREFEITURA FICTICIA UM",
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
            "/api/DREs/", ["100000"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(["100000"])

    @patch("apps.institucional.views.services.get_dres_por_codigos")
    def test_post_204_sem_registros(self, mock_svc: MagicMock) -> None:
        """Retorna 204 quando nenhuma DRE é encontrada para os códigos."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().post(
            "/api/DREs/", ["INEXISTENTE"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class EscolaProfessoresViewTest(SimpleTestCase):
    """Valida a view de professores por escola."""

    @patch("apps.institucional.views.professores_services")
    def test_com_ano_retorna_professores(self, mock_svc: MagicMock) -> None:
        """Retorna professores de uma escola por ano letivo."""
        mock_svc.get_professores_escola.return_value = [
            {
                "codigo_rf": 1,
                "nome": "Ana",
                "cargo": None,
                "cpf": None,
                "data_inicio_exercicio": None,
            }
        ]

        resp = _cliente_autenticado().get(
            "/api/escolas/000004/professores/2026/"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()[0]["codigoRF"], 1)
        mock_svc.get_professores_escola.assert_called_once_with(
            "000004",
            2026,
        )

    @patch("apps.institucional.views.professores_services")
    def test_sem_ano_usa_zero(self, mock_svc: MagicMock) -> None:
        """Retorna professores usando o ano padrão do legado."""
        mock_svc.get_professores_escola.return_value = []

        resp = _cliente_autenticado().get("/api/escolas/000004/professores/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_svc.get_professores_escola.assert_called_once_with(
            "000004",
            0,
        )


class DREDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de DRE."""

    @patch("apps.institucional.views.services.get_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_DRE]
        resp = _cliente_autenticado().get("/api/DREs/100000/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

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
        resp = _cliente_autenticado().get("/api/DREs/100000/")
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
            _cliente_autenticado().get("/api/DREs/100000/")


class SubprefeiturasPorDREViewTest(SimpleTestCase):
    """Valida a view de subprefeituras por DRE."""

    @patch("apps.institucional.views.services.get_subprefeituras_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_SUBPREFEITURA]
        resp = _cliente_autenticado().get("/api/DREs/100000/subprefeituras/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

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
            _cliente_autenticado().get("/api/DREs/100000/subprefeituras/")


class EscolasPorDREViewTest(SimpleTestCase):
    """Valida a view de escolas por DRE."""

    @patch("apps.institucional.views.services.get_escolas_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_ESCOLA_RESUMO]
        resp = _cliente_autenticado().get("/api/DREs/100000/escola/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

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
            _cliente_autenticado().get("/api/DREs/100000/escola/")


class EscolasSigpaePorDREViewTest(SimpleTestCase):
    """Valida a view de escolas SIGPAE por DRE."""

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_200_repassa_codigo_dre(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da DRE ao service."""
        mock_svc.return_value = [_ESCOLA_SIGPAE]
        resp = _cliente_autenticado().get("/api/DREs/100000/escola/Sigpae/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_200_filtra_campos_do_contrato(self, mock_svc: MagicMock) -> None:
        """Retorna apenas os 9 campos previstos no contrato D09."""
        payload_expandido = {
            **_ESCOLA_SIGPAE,
            "tipoEscolaId": 1,
            "tipoUnidadeId": 1,
            "subprefeituraId": 50,
            "dreId": "100000",
            "codigoIntegracao": None,
        }
        mock_svc.return_value = [payload_expandido]

        resp = _cliente_autenticado().get("/api/DREs/100000/escola/Sigpae/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(
            set(item.keys()),
            {
                "codigoEscola",
                "nomeEscola",
                "codigoDRE",
                "tipoEscola",
                "siglaTipoEscola",
                "nomeDRE",
                "siglaDRE",
                "codigoSubprefeitura",
                "nomeSubprefeitura",
            },
        )

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_200_lista_vazia_quando_sem_conteudo(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 200 com lista vazia sem conteúdo da API."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get("/api/DREs/100000/escola/Sigpae/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/escola/Sigpae/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/DREs/100000/escola/Sigpae/")

    @patch("apps.institucional.views.services.get_escolas_sigpae_por_dre")
    def test_502_quando_sidecar_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o sidecar institucional está indisponível."""
        mock_svc.side_effect = httpx.RequestError(
            "connection failed", request=MagicMock()
        )
        resp = _cliente_autenticado().get("/api/DREs/100000/escola/Sigpae/")
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Serviço de institucional indisponível."}
        )


class EscolasPorDREeTipoViewTest(SimpleTestCase):
    """Valida a view de escolas por DRE e tipo de escola."""

    @patch("apps.institucional.views.services.get_escolas_por_dre_e_tipo")
    def test_200_filtra_campos_do_contrato(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os campos do contrato de escola por DRE e tipo."""
        mock_svc.return_value = [_ESCOLA_POR_TIPO]
        resp = _cliente_autenticado().get("/api/DREs/100000/escolas/EMEF/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000", "EMEF")
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
            _cliente_autenticado().get("/api/DREs/100000/escolas/EMEF/")


class UesPorDREViewTest(SimpleTestCase):
    """Valida a view de códigos de UEs por DRE."""

    @patch("apps.institucional.views.services.get_ues_por_dre")
    def test_200_retorna_lista_codigos(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de códigos de UEs da DRE."""
        mock_svc.return_value = ["000002", "000003"]
        resp = _cliente_autenticado().get("/api/DREs/100000/ues/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

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
            _cliente_autenticado().get("/api/DREs/100000/ues/")


class UnidadesPorDREViewTest(SimpleTestCase):
    """Valida a view de unidades administrativas por DRE."""

    @patch("apps.institucional.views.services.get_unidades_por_dre")
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de unidades administrativas da DRE."""
        mock_svc.return_value = [{"codigoEol": "000001"}]
        resp = _cliente_autenticado().get("/api/DREs/100000/unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

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
            _cliente_autenticado().get("/api/DREs/100000/unidades/")


class UnidadeCodigoIntegracaoPorDREViewTest(SimpleTestCase):
    """Valida a view de UEs com código de integração por DRE."""

    @patch(
        "apps.institucional.views.services.get_unidades_codigo_integracao_por_dre"
    )
    def test_200_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com a lista de UEs e código de integração."""
        mock_svc.return_value = [_UNIDADE_CODIGO_INTEGRACAO]
        resp = _cliente_autenticado().get(
            "/api/DREs/100000/unidades/codigo-integracao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("100000")

    @patch(
        "apps.institucional.views.services.get_unidades_codigo_integracao_por_dre"
    )
    def test_200_filtra_campos_do_contrato(self, mock_svc: MagicMock) -> None:
        """Retorna apenas os 3 campos previstos no contrato D11."""
        payload_expandido = {
            **_UNIDADE_CODIGO_INTEGRACAO,
            "tipoEscolaId": 1,
            "tipoUnidadeId": 1,
            "subprefeituraId": 50,
            "dreId": "100000",
        }
        mock_svc.return_value = [payload_expandido]

        resp = _cliente_autenticado().get(
            "/api/DREs/100000/unidades/codigo-integracao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        item = resp.json()[0]
        self.assertEqual(
            set(item.keys()),
            {
                "codigoUe",
                "nomeUe",
                "codigoIntegracao",
            },
        )

    @patch(
        "apps.institucional.views.services.get_unidades_codigo_integracao_por_dre"
    )
    def test_404_quando_dre_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/DREs/INEXISTENTE/unidades/codigo-integracao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "apps.institucional.views.services.get_unidades_codigo_integracao_por_dre"
    )
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get(
                "/api/DREs/100000/unidades/codigo-integracao/"
            )

    @patch(
        "apps.institucional.views.services.get_unidades_codigo_integracao_por_dre"
    )
    def test_502_quando_sidecar_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o sidecar institucional está indisponível."""
        mock_svc.side_effect = httpx.RequestError(
            "connection failed", request=MagicMock()
        )
        resp = _cliente_autenticado().get(
            "/api/DREs/100000/unidades/codigo-integracao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Serviço de institucional indisponível."}
        )


class DadosEscolaViewTest(SimpleTestCase):
    """Valida a view de dados completos de escola."""

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da escola ao service."""
        mock_svc.return_value = _DADOS_ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/dados/000001/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("000001")

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_quando_retorna_lista_com_dict(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 200 usando o primeiro item da lista do service."""
        mock_svc.return_value = [_DADOS_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/dados/000001/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("nomeDRE", resp.json())

    @patch("apps.institucional.views.services.get_dados_escola")
    def test_200_quando_item_nao_e_dict(self, mock_svc: MagicMock) -> None:
        """Retorna 200 quando o item da lista não é um dicionário."""
        mock_svc.return_value = ["valor_escalar"]
        resp = _cliente_autenticado().get("/api/escolas/dados/000001/")
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
            _cliente_autenticado().get("/api/escolas/dados/000001/")


class SubprefeiturasPorEscolaViewTest(SimpleTestCase):
    """Valida a view de subprefeituras por escola."""

    @patch("apps.institucional.views.services.get_subprefeituras_por_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da escola ao service."""
        mock_svc.return_value = [_SUBPREFEITURA]
        resp = _cliente_autenticado().get(
            "/api/escolas/000001/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("000001")

    @patch("apps.institucional.views.services.get_subprefeituras_por_escola")
    def test_404_quando_escola_inexistente(self, mock_svc: MagicMock) -> None:
        """Retorna 404 quando o sidecar responde com 404."""
        mock_svc.side_effect = _httpx_404()
        resp = _cliente_autenticado().get(
            "/api/escolas/INEXISTENTE/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.institucional.views.services.get_subprefeituras_por_escola")
    def test_propaga_erro_http_nao_404(self, mock_svc: MagicMock) -> None:
        """Propaga HTTPStatusError quando o status do sidecar não é 404."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_svc.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with self.assertRaises(httpx.HTTPStatusError):
            _cliente_autenticado().get("/api/escolas/000001/subprefeituras/")

    @patch("apps.institucional.views.services.get_subprefeituras_por_escola")
    def test_502_quando_sidecar_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o sidecar institucional está indisponível."""
        mock_svc.side_effect = httpx.RequestError(
            "connection failed", request=MagicMock()
        )
        resp = _cliente_autenticado().get(
            "/api/escolas/000001/subprefeituras/"
        )
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Serviço de institucional indisponível."}
        )


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


class EscolasListPostViewTest(SimpleTestCase):
    """Valida a view de escolas por lista de códigos."""

    @patch("apps.institucional.views.services.post_escolas")
    def test_200_retorna_lista_escolas(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com as escolas encontradas para os códigos."""
        mock_svc.return_value = [
            {
                "codigoEscola": "000008",
                "nomeEscola": "ESCOLA FICTICIA UM",
                "nomeDRE": "NUCLEO DE ACAO EDUCATIVA FICTICIO",
                "siglaDRE": "NUCLEO DE ACAO EDUCATIVA FICTICIO",
                "codigoDRE": "100010",
                "tipoEscola": "ESC.MUN. DE ENS. SUPLETIVO DE 1.GRAU",
                "siglaTipoEscola": "EMES 1.G",
                "codigoTipoEscola": 30,
                "tipoEscolaId": 30,
                "tipoUnidadeId": 30,
                "dreId": "100010",
                "codigoIntegracao": None,
            }
        ]

        resp = _cliente_autenticado().post(
            "/api/escolas/", ["000008"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigoEscola": "000008",
                    "nomeEscola": "ESCOLA FICTICIA UM",
                    "nomeDRE": "NUCLEO DE ACAO EDUCATIVA FICTICIO",
                    "siglaDRE": "NUCLEO DE ACAO EDUCATIVA FICTICIO",
                    "codigoDRE": "100010",
                    "tipoEscola": "ESC.MUN. DE ENS. SUPLETIVO DE 1.GRAU",
                    "siglaTipoEscola": "EMES 1.G",
                }
            ],
        )
        mock_svc.assert_called_once_with(["000008"])

    @patch("apps.institucional.views.services.post_escolas")
    def test_200_lista_vazia_quando_sem_registros(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 200 com lista vazia quando a API não encontra escolas."""
        mock_svc.return_value = None

        resp = _cliente_autenticado().post(
            "/api/escolas/", ["999999"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_svc.assert_called_once_with(["999999"])

    @patch("apps.institucional.views.services.post_escolas")
    def test_400_quando_sidecar_retorna_400(self, mock_svc: MagicMock) -> None:
        """Retorna 400 quando o sidecar valida a lista como inválida."""
        mock_svc.side_effect = _httpx_status_error(
            400, {"detail": "Lista de códigos é obrigatória."}
        )

        resp = _cliente_autenticado().post("/api/escolas/", [], format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.json(), {"detail": "Lista de códigos é obrigatória."}
        )

    @patch("apps.institucional.views.services.post_escolas")
    def test_502_quando_sidecar_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o serviço institucional está indisponível."""
        mock_svc.side_effect = httpx.RequestError(
            "connection failed", request=MagicMock()
        )

        resp = _cliente_autenticado().post(
            "/api/escolas/", ["000008"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Serviço de institucional indisponível."}
        )


class EscolaDetalheViewTest(SimpleTestCase):
    """Valida a view de detalhe de escola."""

    @patch("apps.institucional.views.services.get_escola")
    def test_200_repassa_codigo_escola(self, mock_svc: MagicMock) -> None:
        """Retorna 200 repassando o código da escola ao service."""
        mock_svc.return_value = _ESCOLA
        resp = _cliente_autenticado().get("/api/escolas/000001/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("000001")

    @patch("apps.institucional.views.services.get_escola")
    def test_200_quando_retorna_lista(self, mock_svc: MagicMock) -> None:
        """Retorna 200 usando o primeiro item da lista do service."""
        mock_svc.return_value = [_ESCOLA]
        resp = _cliente_autenticado().get("/api/escolas/000001/")
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
            _cliente_autenticado().get("/api/escolas/000001/")


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
            "/api/escolas/equipamentos/?codigoEol=000005"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with(
            codigos_subprefeitura=None,
            codigos_dre=None,
            tipos_unidade=None,
            tipos_escola=None,
            nome_escola=None,
            codigo_eol="000005",
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
            "codigoEscola": "000009",
            "nomeEscola": "ESCOLA FICTICIA DOIS",
            "nomeDRE": "DIRETORIA REGIONAL FICTICIA TRES",
            "siglaDRE": "DRE - X3",
            "codigoDRE": "X1",
            "tipoEscola": "CENTRO DE EDUCACAO INFANTIL DIRETO",
            "siglaTipoEscola": "CEI DIRET",
            "codigoTipoEscola": 10,
            "tipoEscolaId": 10,
        }
        mock_svc.return_value = [mock_unidade]
        resp = _cliente_autenticado().get("/api/escolas/todas-unidades/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(
            resp.json()[0],
            {
                "codigoEscola": "000009",
                "nomeEscola": "ESCOLA FICTICIA DOIS",
                "nomeDRE": "DIRETORIA REGIONAL FICTICIA TRES",
                "siglaDRE": "DRE - X3",
                "codigoDRE": "X1",
                "tipoEscola": "CENTRO DE EDUCACAO INFANTIL DIRETO",
                "siglaTipoEscola": "CEI DIRET",
            },
        )
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
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("indisponível", resp.json()["detail"])


class TiposUnidadeEducacaoViewTest(SimpleTestCase):
    """Valida a view de tipos de unidade educacional."""

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_200_retorna_lista_tipos(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista de tipos de unidade educacional."""
        mock_svc.return_value = ["ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL"]
        resp = _cliente_autenticado().get(
            "/api/escolas/tipos_unidade_educacao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(
            resp.json()[0], "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL"
        )
        mock_svc.assert_called_once_with()

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_200_lista_vazia(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com lista vazia quando não há tipos."""
        mock_svc.return_value = []
        resp = _cliente_autenticado().get(
            "/api/escolas/tipos_unidade_educacao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])

    @patch("apps.institucional.views.services.get_tipos_unidade_educacao")
    def test_502_quando_servico_institucional_indisponivel(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 502 quando o serviço institucional é indisponível."""
        mock_svc.side_effect = httpx.RequestError("Connection error")
        resp = _cliente_autenticado().get(
            "/api/escolas/tipos_unidade_educacao/"
        )
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("indisponível", resp.json()["detail"])


class UnidadeEolViewTest(SimpleTestCase):
    """Valida a view de unidade EOL."""

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_200_retorna_unidade(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os dados resumidos da unidade."""
        mock_svc.return_value = {
            "codigo": "000001",
            "sigla": "EMEF",
            "nomeUnidade": "EMEF TESTE",
            "tipo": 1,
            "codigoReferencia": "000001",
        }
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/000001/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_svc.assert_called_once_with("000001")

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_204_quando_sidecar_nao_retorna_conteudo(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar não encontra a unidade."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/000000/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch("apps.institucional.views.services.get_unidade_eol")
    def test_204_quando_sidecar_retorna_404(self, mock_svc: MagicMock) -> None:
        """Retorna 204 quando o sidecar responde 404 para unidade ausente."""
        mock_svc.side_effect = _httpx_status_error(
            404, {"detail": "Unidade EOL não encontrada."}
        )
        resp = _cliente_autenticado().get("/api/escolas/unidade-eol/000000/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class SincronizacoesInstitucionaisViewTest(SimpleTestCase):
    """Valida a view de sincronizações institucionais."""

    @patch(
        "apps.institucional.views.services.get_sincronizacoes_institucionais"
    )
    def test_200_retorna_sincronizacao(self, mock_svc: MagicMock) -> None:
        """Retorna 200 com os dados da sincronização institucional."""
        mock_svc.return_value = {
            "ueCodigo": "000001",
            "dataAtualizacao": "2019-05-06T14:42:12.843",
            "ueNome": "EMEF TESTE",
            "dreCodigo": 100000,
            "tipoEscolaCodigo": 1,
            "dreId": "100000",
        }
        resp = _cliente_autenticado().get(
            "/api/escolas/000001/sincronizacoes-institucionais/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            {
                "ueCodigo": "000001",
                "dataAtualizacao": "2019-05-06T14:42:12.843",
                "dreCodigo": 100000,
                "ueNome": "EMEF TESTE",
                "tipoEscolaCodigo": 1,
            },
        )
        mock_svc.assert_called_once_with("000001")

    @patch(
        "apps.institucional.views.services.get_sincronizacoes_institucionais"
    )
    def test_204_quando_sidecar_nao_retorna_conteudo(
        self, mock_svc: MagicMock
    ) -> None:
        """Retorna 204 quando o sidecar não encontra a sincronização."""
        mock_svc.return_value = None
        resp = _cliente_autenticado().get(
            "/api/escolas/000000/sincronizacoes-institucionais/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch(
        "apps.institucional.views.services.get_sincronizacoes_institucionais"
    )
    def test_204_quando_api_retorna_404(self, mock_svc: MagicMock) -> None:
        """Retorna 204 quando a API responde 404."""
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
            {"codigo": "000001", "nome": "UE PARCEIRA", "email": None}
        ]
        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", ["000001"], format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), mock_svc.return_value)
        mock_svc.assert_called_once_with(["000001"])

    @patch("apps.institucional.views.services.get_dados_escola")
    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_200_nao_complementa_codigos_ausentes(
        self, mock_post: MagicMock, mock_dados: MagicMock
    ) -> None:
        """Mantém apenas as unidades retornadas pelo serviço institucional."""
        mock_post.return_value = [
            {
                "codigo": "000012",
                "nome": "ESCOLA FICTICIA TRES",
                "email": "escola.ficticia@sme.prefeitura.sp.gov.br",
            }
        ]

        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/",
            ["000012", "000006", "000011"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json(),
            [
                {
                    "codigo": "000012",
                    "nome": "ESCOLA FICTICIA TRES",
                    "email": "escola.ficticia@sme.prefeitura.sp.gov.br",
                }
            ],
        )
        mock_post.assert_called_once_with(["000012", "000006", "000011"])
        mock_dados.assert_not_called()

    @patch("apps.institucional.views.services.get_dados_escola")
    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_200_retorna_vazio_sem_consulta_complementar(
        self, mock_post: MagicMock, mock_dados: MagicMock
    ) -> None:
        """Retorna lista vazia quando não há parceiras no institucional."""
        mock_post.return_value = []

        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", ["000011"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), [])
        mock_post.assert_called_once_with(["000011"])
        mock_dados.assert_not_called()

    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_200_preserva_resposta_do_institucional(
        self, mock_post: MagicMock
    ) -> None:
        """Preserva a lista retornada pelo serviço institucional."""
        mock_post.return_value = [
            {
                "codigo": "000011",
                "nome": "ESCOLA FICTICIA QUATRO",
                "email": "escola.ficticia@gmail.com",
            }
        ]

        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/",
            ["000011"],
            format="json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json(), mock_post.return_value)
        mock_post.assert_called_once_with(["000011"])

    @patch("apps.institucional.views.services.post_unidades_parceiras")
    def test_502_quando_sidecar_falha_por_transporte(
        self, mock_post: MagicMock
    ) -> None:
        """Retorna 502 quando o serviço institucional está indisponível."""
        mock_post.side_effect = httpx.ConnectError("timeout")

        resp = _cliente_autenticado().post(
            "/api/escolas/unidades-parceiras/", ["000012"], format="json"
        )

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            resp.json(), {"detail": "Serviço de institucional indisponível."}
        )
        mock_post.assert_called_once_with(["000012"])

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
