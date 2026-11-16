"""Testa o contrato unificado e a indicação de migração no Swagger."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from drf_spectacular.generators import SchemaGenerator

from apps.professores import services
from apps.professores.tests.test_views import _cliente_autenticado

BASE = "/api/professores"


class BuscaProfessorPorRfTest(SimpleTestCase):
    """Valida filtros, resposta, erros e roteamento para o MS Professores."""

    @patch("apps.professores.views.services.buscar_professor_por_rf")
    def test_repassa_filtros_e_preserva_rf(self, consulta: MagicMock) -> None:
        """Envia booleano validado e mantém zeros à esquerda."""
        consulta.return_value = {"codigo_rf": "000001", "nome": "Professor"}
        resposta = _cliente_autenticado().get(
            f"{BASE}/000001/anos_letivos/2024",
            {
                "dre_id": "108100",
                "ue_id": "000532",
                "buscar_outros_cargos": "true",
                "tipo_busca": "rf_dre_ue",
            },
        )
        assert resposta.status_code == 200
        assert resposta.json() == {"codigoRF": "000001", "nome": "Professor"}
        consulta.assert_called_once_with(
            "000001",
            2024,
            {
                "dre_id": "108100",
                "ue_id": "000532",
                "buscar_outros_cargos": True,
                "tipo_busca": "rf_dre_ue",
            },
        )

    @patch("apps.professores.views.services.buscar_professor_por_rf")
    def test_ausente_e_padrao(self, consulta: MagicMock) -> None:
        """Retorna 204 e usa false por padrão."""
        consulta.return_value = None
        resposta = _cliente_autenticado().get(
            f"{BASE}/000001/anos_letivos/2024"
        )
        assert resposta.status_code == 204
        consulta.assert_called_once_with(
            "000001", 2024, {"buscar_outros_cargos": False}
        )

    @patch("apps.professores.views.services.buscar_professor_por_rf")
    def test_rejeita_filtros_invalidos_antes_de_consultar(
        self, consulta: MagicMock
    ) -> None:
        """Não chama o serviço com parâmetros inválidos."""
        client = _cliente_autenticado()
        for rf, ano, filtros in (
            ("000001", 0, {}),
            ("%20", 2024, {}),
            ("000001", 2024, {"buscar_outros_cargos": "invalido"}),
            ("000001", 2024, {"dre_id": "123456789012345678901"}),
            ("000001", 2024, {"tipo_busca": "invalido"}),
        ):
            assert (
                client.get(
                    f"{BASE}/{rf}/anos_letivos/{ano}", filtros
                ).status_code
                == 400
            )
        consulta.assert_not_called()

    @patch("apps.professores.services._client")
    def test_consulta_unificada_com_localizacao(
        self, client: MagicMock
    ) -> None:
        """Repassa todos os filtros para o contrato único do MS."""
        filtros = {
            "dre_id": "108100",
            "ue_id": "000532",
            "buscar_outros_cargos": False,
        }
        retorno = services.buscar_professor_por_rf("000001", 2024, filtros)
        client.get.assert_called_once_with(
            "/api/v1/professores/000001/anos_letivos/2024/", params=filtros
        )
        client.json_or_none.assert_called_once_with(client.get.return_value)
        assert retorno == client.json_or_none.return_value

    @patch("apps.professores.services._client")
    def test_sem_localizacao_usa_contrato_unificado(
        self, client: MagicMock
    ) -> None:
        """Não seleciona uma rota antiga no Gateway."""
        services.buscar_professor_por_rf(
            "000001", 2024, {"buscar_outros_cargos": True}
        )
        client.get.assert_called_once_with(
            "/api/v1/professores/000001/anos_letivos/2024/",
            params={"buscar_outros_cargos": True},
        )

    @patch("apps.professores.services._client")
    def test_tipo_explicito_preserva_dre_ue_sem_filtros(
        self, client: MagicMock
    ) -> None:
        """O MS recebe o seletor mesmo sem DRE/UE."""
        services.buscar_professor_por_rf(
            "000001",
            2024,
            {"tipo_busca": "rf_dre_ue", "buscar_outros_cargos": False},
        )
        client.get.assert_called_once_with(
            "/api/v1/professores/000001/anos_letivos/2024/",
            params={"tipo_busca": "rf_dre_ue", "buscar_outros_cargos": False},
        )

    @patch("apps.professores.services._client")
    def test_tipo_rf_explicito_e_filtros_sao_repassados_ao_ms(
        self, client: MagicMock
    ) -> None:
        """A decisão de aplicar filtros permanece no MS."""
        services.buscar_professor_por_rf(
            "000001",
            2024,
            {
                "tipo_busca": "rf",
                "dre_id": "108100",
                "ue_id": "000532",
                "buscar_outros_cargos": True,
            },
        )
        client.get.assert_called_once_with(
            "/api/v1/professores/000001/anos_letivos/2024/",
            params={
                "tipo_busca": "rf",
                "dre_id": "108100",
                "ue_id": "000532",
                "buscar_outros_cargos": True,
            },
        )

    @patch("apps.professores.services._client")
    def test_outros_cargos_nao_altera_consulta_com_dre(
        self, client: MagicMock
    ) -> None:
        """Encaminha o booleano para o MS, que mantém a regra existente."""
        services.buscar_professor_por_rf(
            "000001", 2024, {"dre_id": "108100", "buscar_outros_cargos": True}
        )
        client.get.assert_called_once_with(
            "/api/v1/professores/000001/anos_letivos/2024/",
            params={"dre_id": "108100", "buscar_outros_cargos": True},
        )

    def test_swagger_indica_substituicao(self) -> None:
        """Deprecia apenas as rotas antigas e documenta os novos filtros."""
        paths = SchemaGenerator().get_schema(public=True)["paths"]
        for rota in ("BuscarPorRf", "BuscarPorRfDreUe"):
            operacao = paths[f"{BASE}/{{codigo_rf}}/{rota}/{{ano_letivo}}"][
                "get"
            ]
            assert operacao["deprecated"] is True
            assert "anos_letivos" in operacao["description"]
        nova = paths[f"{BASE}/{{codigo_rf}}/anos_letivos/{{ano_letivo}}"][
            "get"
        ]
        assert not nova.get("deprecated", False)
        assert {"dre_id", "ue_id", "buscar_outros_cargos", "tipo_busca"} <= {
            parametro["name"] for parametro in nova["parameters"]
        }
