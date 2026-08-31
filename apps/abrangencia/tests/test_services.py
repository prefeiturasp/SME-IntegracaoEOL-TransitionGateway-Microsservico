"""Valida os serviços do domínio de abrangência."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.abrangencia import services

_BASE_TURMAS = "/api/v1/pedagogico/turmas"

_PAYLOAD_SIDECAR = {
    "abrangencia": None,
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
                            "dataFim": "2026-12-18T00:00:00Z",
                            "ehistorico": False,
                            "ensinoEspecial": False,
                            "etapaEJA": 0,
                            "serieEnsino": None,
                            "dataInicioTurma": "2026-02-02T00:00:00Z",
                            "extinta": False,
                            "situacao": None,
                            "ueCodigo": None,
                        }
                    ],
                }
            ],
        }
    ],
}


class GetEstruturaVigentePorDreTest(SimpleTestCase):
    """Valida a busca da estrutura vigente por DRE."""

    @patch("apps.abrangencia.services._client")
    def test_chama_path_correto_e_remove_abrangencia(
        self, mock_client: MagicMock
    ) -> None:
        response = MagicMock()
        mock_client.get.return_value = response
        mock_client.json_or_none.return_value = _PAYLOAD_SIDECAR

        resultado = services.get_estrutura_vigente_por_dre("100000")

        mock_client.get.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-atribuidas-dre-ue/todas/",
            params={"codigo_dre": "100000"},
        )
        response.raise_for_status.assert_called_once_with()
        self.assertNotIn("abrangencia", resultado)
        self.assertEqual(resultado["dres"][0]["codigo"], "100000")

    @patch("apps.abrangencia.services._client")
    def test_formata_datas_da_turma_no_padrao_legado(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value = MagicMock()
        mock_client.json_or_none.return_value = _PAYLOAD_SIDECAR

        resultado = services.get_estrutura_vigente_por_dre("100000")

        turma = resultado["dres"][0]["ues"][0]["turmas"][0]
        # America/Sao_Paulo = UTC-3, sem horário de verão.
        self.assertEqual(turma["dataFim"], "2026-12-17T21:00:00")
        self.assertEqual(turma["dataInicioTurma"], "2026-02-01T21:00:00")

    @patch("apps.abrangencia.services._client")
    def test_payload_vazio_retorna_dres_vazio(
        self, mock_client: MagicMock
    ) -> None:
        mock_client.get.return_value = MagicMock()
        mock_client.json_or_none.return_value = None

        resultado = services.get_estrutura_vigente_por_dre("999999")

        self.assertEqual(resultado, {"dres": []})


class GetEstruturaVigentePorTurmasTest(SimpleTestCase):
    """Valida a busca da estrutura vigente por lista de turmas."""

    def test_sem_codigos_nao_chama_sidecar(self) -> None:
        with patch("apps.abrangencia.services._client") as mock_client:
            resultado = services.get_estrutura_vigente_por_turmas([])

        self.assertEqual(resultado, {"dres": []})
        mock_client.post.assert_not_called()

    @patch("apps.abrangencia.services._client")
    def test_chama_path_correto_com_codigos(
        self, mock_client: MagicMock
    ) -> None:
        response = MagicMock()
        mock_client.post.return_value = response
        mock_client.json_or_none.return_value = _PAYLOAD_SIDECAR

        resultado = services.get_estrutura_vigente_por_turmas([9000001])

        mock_client.post.assert_called_once_with(
            f"{_BASE_TURMAS}/turmas-atribuidas-dre-ue/por-turmas/",
            payload=[9000001],
        )
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            resultado["dres"][0]["ues"][0]["turmas"][0]["codigo"], 9000001
        )
