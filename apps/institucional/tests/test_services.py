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
        mock_client.json_or_none.return_value = [{"codigoDRE": "100000"}]

        result = services.get_dres_por_codigos(["100000"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/dres/", payload=["100000"]
        )
        self.assertEqual(result[0]["codigoDRE"], "100000")

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
        mock_client.get.return_value.json.return_value = [{"codigoDRE": "X1"}]

        result = services.get_dre("X1")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/X1/")
        self.assertEqual(result[0]["codigoDRE"], "X1")


class GetSubprefeiturasPorDRETest(SimpleTestCase):
    """Valida a consulta de subprefeituras por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de subprefeituras com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoSubprefeitura": "00", "nomeSubprefeitura": "TESTE"}
        ]

        result = services.get_subprefeituras_por_dre("X1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/dres/X1/subprefeituras/"
        )
        self.assertEqual(result[0]["codigoSubprefeitura"], "00")


class GetEscolasPorDRETest(SimpleTestCase):
    """Valida a consulta de escolas por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de escolas com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_escolas_por_dre("X1")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/X1/escola/")
        self.assertEqual(result, [])


class GetEscolasSigpaePorDRETest(SimpleTestCase):
    """Valida a consulta de escolas SIGPAE por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path SIGPAE com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = [
            {"codigoEscola": "000001", "nomeEscola": "EMEF TESTE"}
        ]

        result = services.get_escolas_sigpae_por_dre("X1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/dres/X1/escola/Sigpae/"
        )
        self.assertEqual(result[0]["codigoEscola"], "000001")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_sem_conteudo(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna None quando o sidecar responde sem conteúdo."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_escolas_sigpae_por_dre("X1")

        self.assertIsNone(result)


class GetUesPorDRETest(SimpleTestCase):
    """Valida a consulta de códigos de UEs por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de UEs com o código da DRE e retorna os códigos."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = ["000002", "000003"]

        result = services.get_ues_por_dre("X1")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/X1/ues/")
        self.assertEqual(result, ["000002", "000003"])


class GetUnidadesPorDRETest(SimpleTestCase):
    """Valida a consulta de unidades administrativas por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de unidades com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = []

        result = services.get_unidades_por_dre("X1")

        mock_client.get.assert_called_once_with(f"{_BASE}/dres/X1/unidades/")
        self.assertEqual(result, [])


class GetUnidadesCodigoIntegracaoPorDRETest(SimpleTestCase):
    """Valida a consulta de códigos de integração por DRE."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_dre(self, mock_client: MagicMock) -> None:
        """Monta o path de código integração com o código da DRE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoUe": "000001", "nomeUe": "EMEF TESTE"}
        ]

        result = services.get_unidades_codigo_integracao_por_dre("X1")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/dres/X1/unidades/codigo-integracao/"
        )
        self.assertEqual(result[0]["codigoUe"], "000001")


class GetEscolaTest(SimpleTestCase):
    """Valida a consulta de uma escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_escola(
        self, mock_client: MagicMock
    ) -> None:
        """Monta o path com o código da escola e retorna os dados."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = {
            "codigoEscola": "000001"
        }

        result = services.get_escola("000001")

        mock_client.get.assert_called_once_with(f"{_BASE}/escolas/000001/")
        self.assertEqual(result["codigoEscola"], "000001")


class PostEscolasTest(SimpleTestCase):
    """Valida a consulta de escolas por lista de códigos."""

    @patch("apps.institucional.services._client")
    def test_chama_post_com_lista_de_codigos(
        self, mock_client: MagicMock
    ) -> None:
        """Envia os códigos via POST e retorna as escolas encontradas."""
        mock_client.post.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = [
            {"codigoEscola": "000008", "nomeEscola": "ESCOLA FICTICIA UM"}
        ]

        result = services.post_escolas(["000008"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/escolas/", payload=["000008"]
        )
        self.assertEqual(result[0]["codigoEscola"], "000008")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_sem_registros(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna None quando o sidecar não encontra registros."""
        mock_client.post.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.post_escolas(["INEXISTENTE"])

        self.assertIsNone(result)


class GetSubprefeiturasPorEscolaTest(SimpleTestCase):
    """Valida a consulta de subprefeituras por escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_escola(
        self, mock_client: MagicMock
    ) -> None:
        """Monta o path de subprefeituras com o código da escola."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {
                "codigoSubprefeitura": "50",
                "nomeSubprefeitura": "SUBPREFEITURA FICTICIA UM",
            }
        ]

        result = services.get_subprefeituras_por_escola("000001")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/000001/subprefeituras/"
        )
        self.assertEqual(result[0]["codigoSubprefeitura"], "50")


class GetUnidadeEolTest(SimpleTestCase):
    """Valida a consulta de unidade EOL."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_eol(self, mock_client: MagicMock) -> None:
        """Monta o path da unidade EOL com o código informado."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = {
            "codigo": "000002",
            "nomeUnidade": "EMEF EXEMPLO",
        }

        result = services.get_unidade_eol("000002")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/unidade-eol/000002/"
        )
        self.assertEqual(result["codigo"], "000002")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_sidecar_responde_204(
        self, mock_client: MagicMock
    ) -> None:
        """Propaga ausência de conteúdo do sidecar."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_unidade_eol("000000")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/unidade-eol/000000/"
        )
        self.assertIsNone(result)


class GetDadosEscolaTest(SimpleTestCase):
    """Valida a consulta de dados completos de uma escola."""

    @patch("apps.institucional.services._client")
    def test_chama_path_dados_com_codigo(self, mock_client: MagicMock) -> None:
        """Monta o path de dados com o código da escola."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = {
            "codigo": "000001",
            "nome": "EMEF TESTE",
        }

        result = services.get_dados_escola("000001")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/dados/000001/"
        )
        self.assertEqual(result["codigo"], "000001")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_nao_encontrado(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna None quando o sidecar não encontra a escola."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_dados_escola("999999")

        self.assertIsNone(result)


class GetSincronizacoesInstitucionaisTest(SimpleTestCase):
    """Valida a consulta de sincronizações institucionais."""

    @patch("apps.institucional.services._client")
    def test_chama_path_com_codigo_ue(self, mock_client: MagicMock) -> None:
        """Monta o path da sincronização institucional com a UE."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = {
            "ueCodigo": "000002",
            "ueNome": "EMEF EXEMPLO",
        }

        result = services.get_sincronizacoes_institucionais("000002")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/000002/sincronizacoes-institucionais/"
        )
        self.assertEqual(result["ueCodigo"], "000002")

    @patch("apps.institucional.services._client")
    def test_retorna_none_quando_sidecar_responde_204(
        self, mock_client: MagicMock
    ) -> None:
        """Propaga ausência de conteúdo do sidecar."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.json_or_none.return_value = None

        result = services.get_sincronizacoes_institucionais("000000")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/000000/sincronizacoes-institucionais/"
        )
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


class PostUnidadesParceirasTest(SimpleTestCase):
    """Valida a consulta de unidades parceiras."""

    @patch("apps.institucional.services._client")
    def test_chama_post_com_lista_de_codigos(
        self, mock_client: MagicMock
    ) -> None:
        """Envia os códigos via POST e retorna as unidades parceiras."""
        mock_client.post.return_value.raise_for_status = MagicMock()
        mock_client.post.return_value.json.return_value = [
            {"codigo": "000002", "nome": "UE PARCEIRA"}
        ]

        result = services.post_unidades_parceiras(["000002"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/escolas/unidades-parceiras/", ["000002"]
        )
        self.assertEqual(result[0]["codigo"], "000002")


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
            {"codigoEol": "000005"}
        ]

        result = services.get_equipamentos(codigo_eol="000005")

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/equipamentos/",
            params={"codigoEol": "000005"},
        )
        self.assertEqual(result[0]["codigoEol"], "000005")

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
        mock_client.get.return_value.json.return_value = {
            "count": 0,
            "results": [],
        }

        result = services.get_todas_unidades()

        mock_client.get.assert_called_once_with(
            f"{_BASE}/escolas/todas-unidades/",
            params={"limite": 1000, "offset": 0},
        )
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_retorna_lista_unidades(self, mock_client: MagicMock) -> None:
        """Consolida todas as paginas em uma unica lista."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.side_effect = [
            MagicMock(
                json=MagicMock(
                    return_value={
                        "count": 2,
                        "results": [{"codigoEscola": "000009"}],
                    }
                ),
                raise_for_status=MagicMock(),
            ),
            MagicMock(
                json=MagicMock(
                    return_value={
                        "count": 2,
                        "results": [{"codigoEscola": "000010"}],
                    }
                ),
                raise_for_status=MagicMock(),
            ),
        ]

        result = services.get_todas_unidades()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["codigoEscola"], "000009")
        self.assertEqual(result[1]["codigoEscola"], "000010")
        self.assertEqual(mock_client.get.call_count, 2)

    @patch("apps.institucional.services._client")
    def test_retorna_lista_quando_sidecar_ja_retorna_lista(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna lista direta quando sidecar nao usa envelope."""
        mock_client.get.return_value.raise_for_status = MagicMock()
        mock_client.get.return_value.json.return_value = [
            {"codigoEscola": "000009"}
        ]

        result = services.get_todas_unidades()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["codigoEscola"], "000009")


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


class GetUesRecorteFundMedioTest(SimpleTestCase):
    """Valida a consulta de UEs no recorte de tipo de escola."""

    @patch("apps.institucional.services._client")
    def test_chama_post_com_codigos(self, mock_client: MagicMock) -> None:
        """Envia os códigos via POST e retorna as UEs do recorte."""
        mock_client.json_or_none.return_value = [
            {"codigo": "000007", "codigoTipoEscola": 1}
        ]

        result = services.get_ues_recorte_fund_medio(["000007"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/escolas/recorte-fund-medio/",
            payload=["000007"],
        )
        self.assertEqual(result[0]["codigo"], "000007")

    @patch("apps.institucional.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self, mock_client: MagicMock
    ) -> None:
        """Sem códigos não consulta o sidecar."""
        result = services.get_ues_recorte_fund_medio([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_retorna_lista_vazia_quando_ms_responde_sem_corpo(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna lista vazia quando o sidecar não traz corpo."""
        mock_client.json_or_none.return_value = None

        result = services.get_ues_recorte_fund_medio(["000007"])

        self.assertEqual(result, [])


class GetCodigosUeEmeiTest(SimpleTestCase):
    """Valida a consulta de códigos de UE no recorte EMEI."""

    @patch("apps.institucional.services._client")
    def test_chama_post_e_extrai_codigos(self, mock_client: MagicMock) -> None:
        """Envia códigos via POST e devolve só os EMEI do corpo."""
        mock_client.json_or_none.return_value = {"codigos_ue": ["000007"]}

        result = services.get_codigos_ue_emei(["000007", "000999"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/escolas/recorte-emei/",
            payload=["000007", "000999"],
        )
        self.assertEqual(result, ["000007"])

    @patch("apps.institucional.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self, mock_client: MagicMock
    ) -> None:
        """Sem códigos não consulta o sidecar."""
        result = services.get_codigos_ue_emei([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])

    @patch("apps.institucional.services._client")
    def test_retorna_vazio_quando_ms_responde_sem_corpo(
        self, mock_client: MagicMock
    ) -> None:
        """Retorna lista vazia quando o sidecar não traz corpo."""
        mock_client.json_or_none.return_value = None

        result = services.get_codigos_ue_emei(["000007"])

        self.assertEqual(result, [])


class GetCodigosUeTipoSgpTest(SimpleTestCase):
    """Valida a consulta de códigos de UE no recorte tipo_escola_sgp."""

    @patch("apps.institucional.services._client")
    def test_chama_post_e_extrai_codigos(self, mock_client: MagicMock) -> None:
        """Envia códigos via POST e devolve só os do recorte SGP."""
        mock_client.json_or_none.return_value = {"codigos_ue": ["000007"]}

        result = services.get_codigos_ue_tipo_sgp(["000007", "000999"])

        mock_client.post.assert_called_once_with(
            f"{_BASE}/escolas/recorte-tipo-sgp/",
            payload=["000007", "000999"],
        )
        self.assertEqual(result, ["000007"])

    @patch("apps.institucional.services._client")
    def test_lista_vazia_nao_chama_sidecar(
        self, mock_client: MagicMock
    ) -> None:
        """Sem códigos não consulta o sidecar."""
        result = services.get_codigos_ue_tipo_sgp([])

        mock_client.post.assert_not_called()
        self.assertEqual(result, [])
