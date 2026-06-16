"""Valida os serviços do domínio institucional."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.institucional import services

# Prefixo das rotas do sidecar institucional.
_BASE = "/api/v1/institucional"


class GetDREsTest(SimpleTestCase):
    """Valida a consulta de DREs."""

    @patch("apps.institucional.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de listagem de DREs."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_dres()

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/")
        self.assertEqual(result, [])


class GetDresPorCodigosTest(SimpleTestCase):
    """Valida a consulta de DREs por lista de códigos."""

    @patch("apps.institucional.services._client")
    def test_chama_post_com_codigos(self, mock_client: MagicMock) -> None:
        """Envia os códigos via POST e retorna as DREs correspondentes."""
        mock_client.post.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = [{"codigoDRE": "108100"}]

        result = services.get_dres_por_codigos(["108100"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/dres/", payload=["108100"]
        )
        self.assertEqual(result[0]["codigoDRE"], "108100")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_sem_registros(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna None quando o sidecar não encontra registros."""
        mock_client.post.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_dres_por_codigos(["INEXISTENTE"])

        self.assertIsNone(result)


class GetDRETest(SimpleTestCase):
    """Valida a consulta de uma DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path com o código da DRE e retorna os dados."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [{"codigoDRE": "BT"}]

        result = services.get_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/")
        self.assertEqual(result[0]["codigoDRE"], "BT")


class GetSubprefeiturasPorDRETest(SimpleTestCase):
    """Valida a consulta de subprefeituras por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de subprefeituras com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoSubprefeitura": "00", "nomeSubprefeitura": "TESTE"}
        ]

        result = services.get_subprefeituras_por_dre("BT")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/dres/BT/subprefeituras/"
        )
        self.assertEqual(result[0]["codigoSubprefeitura"], "00")


class GetEscolasPorDRETest(SimpleTestCase):
    """Valida a consulta de escolas por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de escolas com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_escolas_por_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/escola/")
        self.assertEqual(result, [])


class GetUesPorDRETest(SimpleTestCase):
    """Valida a consulta de códigos de UEs por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de UEs com o código da DRE e retorna os códigos."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = ["019251", "019252"]

        result = services.get_ues_por_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/ues/")
        self.assertEqual(result, ["019251", "019252"])


class GetUnidadesPorDRETest(SimpleTestCase):
    """Valida a consulta de unidades administrativas por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de unidades com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_unidades_por_dre("BT")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/BT/unidades/")
        self.assertEqual(result, [])


class GetEscolaTest(SimpleTestCase):
    """Valida a consulta de uma escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_escola(
        self, mock_client: MagicMock
    ) -> None:
        """Monta o path com o código da escola e retorna os dados."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "codigoEscola": "019308"
        }

        result = services.get_escola("019308")

        mock_client.get.assert_called_once_with(f"{_BASE}/escolas/019308/")
        self.assertEqual(result["codigoEscola"], "019308")


class GetDadosEscolaTest(SimpleTestCase):
    """Valida a consulta de dados completos de uma escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_dados_com_codigo(self, mock_client: MagicMock) -> None:
        """Monta o path de dados com o código da escola."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = {
            "codigo": "019308",
            "nome": "EMEF TESTE",
        }

        result = services.get_dados_escola("019308")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/dados/019308/"
        )
        self.assertEqual(result["codigo"], "019308")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_nao_encontrado(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna None quando o sidecar não encontra a escola."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_dados_escola("999999")

        self.assertIsNone(result)


class GetTiposEscolasTest(SimpleTestCase):
    """Valida a consulta de tipos de escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de tipos de escola e retorna a lista."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {
                "codigo": 1,
                "descricaoSigla": "EMEF",
                "dtAtualizacao": "2026-04-17T00:00:00",
            }
        ]

        result = services.get_tipos_escolas()

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/tiposEscolas/"
        )
        self.assertEqual(result[0]["descricaoSigla"], "EMEF")


class GetEquipamentosTest(SimpleTestCase):
    """Valida a consulta de equipamentos."""

    @patch("apps.institucional.services._client")
    def test_sem_filtros_nao_passa_params(
        self, mock_client: MagicMock
    ) -> None:
        """Não envia params quando nenhum filtro é informado."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_equipamentos()

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/", params=None
        )
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_com_codigo_eol_passa_params(self, mock_client: MagicMock) -> None:
        """Envia codigoEol nos params quando o filtro é informado."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoEol": "019716"}
        ]

        result = services.get_equipamentos(codigo_eol="019716")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/",
            params={"codigoEol": "019716"},
        )
        self.assertEqual(result[0]["codigoEol"], "019716")

    @patch("apps.institucional.services._client")
    def test_com_multiplos_filtros(self, mock_client: MagicMock) -> None:
        """Envia múltiplos filtros combinados nos params."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        services.get_equipamentos(tipos_escola=["1", "2"], tipos_unidade=["1"])

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/",
            params={"tiposEscola": ["1", "2"], "tiposUnidade": ["1"]},
        )


class GetTodasUnidadesTest(SimpleTestCase):
    """Valida a consulta de todas as unidades educacionais."""

    @patch("apps.institucional.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de listagem de todas as unidades."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_todas_unidades()

        mock_client.get.assert_called_once_with(f"{_BASE}/escolas/todas-unidades/")
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_retorna_lista_unidades(self, mock_client: MagicMock) -> None:
        """Retorna payload paginado de unidades do sidecar."""
        mock_unidade = {
            "codigoEscola": "019308",
            "nomeEscola": "EMEF TESTE",
            "codigoDRE": "BT",
            "nomeDRE": "DRE BUTANTA",
        }
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "count": 1,
            "results": [mock_unidade],
        }

        result = services.get_todas_unidades()

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["codigoEscola"], "019308")


class GetTiposUnidadeEducacaoTest(SimpleTestCase):
    """Valida a consulta de tipos de unidade educacional."""

    @patch("apps.institucional.services._client")
    def test_chama_path_correto(self, mock_client: MagicMock) -> None:
        """Monta o path de listagem de tipos de unidade educacional."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_tipos_unidade_educacao()

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/tipos_unidade_educacao/"
        )
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_retorna_lista_tipos(self, mock_client: MagicMock) -> None:
        """Retorna a lista de strings de tipos de unidade do sidecar."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL"
        ]

        result = services.get_tipos_unidade_educacao()

        self.assertEqual(result[0], "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL")
