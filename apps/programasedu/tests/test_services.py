"""Valida os serviços do domínio de programas educacionais."""

import gzip
import json
from unittest.mock import MagicMock, patch

import httpx
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from apps.programasedu import services
from apps.programasedu.serializers import AlunoTurmaPapSerializer

_CACHE_LOCAL = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


class ListarTurmasPapTest(SimpleTestCase):
    """Valida a consulta de turmas PAP."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de turmas PAP."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"codigoTurma": "X", "turmaNome": "1A"}]
        mock_get.return_value = mock_resp

        result = services.listar_turmas_pap(
            ano_letivo=2026, codigo_escola="123"
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/turmas-pap/2026/ues/123"
        )
        self.assertEqual(result, [{"codigoTurma": "X", "turmaNome": "1A"}])


class VerificarAlunosPapTest(SimpleTestCase):
    """Valida a verificação de alunos em turmas PAP."""

    @patch.object(services._client, "get")
    def test_propaga_codigos_alunos(self, mock_get: MagicMock) -> None:
        """Verifica que os codigos dos alunos sao enviados como parametro."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.verificar_alunos_pap(
            ano_letivo=2026, codigos_alunos=["1", "2"]
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/alunos-pap/2026",
            params={"codigos_alunos": ["1", "2"]},
        )


_LINHA_SIDECAR = (
    b'[{"ano_letivo":2025,"codigo_turma":9100001,"codigo_ue":"000001",'
    b'"codigo_dre":"100000","codigo_aluno":9100002,'
    b'"componente_curricular_id":50}]'
)
_LINHA_CONTRATO = [
    {
        "anoLetivo": 2025,
        "codigoTurma": 9100001,
        "codigoUe": "000001",
        "codigoDre": "100000",
        "codigoAluno": 9100002,
        "componenteCurricularId": 50,
    }
]


def _resposta_sidecar(corpo: bytes) -> MagicMock:
    """Cria uma resposta simulada do serviço de programas."""
    resposta = MagicMock()
    resposta.content = corpo
    return resposta


@override_settings(CACHES=_CACHE_LOCAL)
class ListarAlunosPapTest(SimpleTestCase):
    """Valida a consulta, a tradução e o cache de alunos PAP."""

    def setUp(self) -> None:
        """Isola o cache entre os testes."""
        cache.clear()
        self.addCleanup(cache.clear)

    @patch.object(services._client, "get")
    def test_ano_corrente_chama_path_e_traduz_campos(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica o path e o contrato do ano corrente."""
        mock_get.return_value = _resposta_sidecar(_LINHA_SIDECAR)

        corpo = services.listar_alunos_pap_ano_corrente()

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/pap/ano-corrente"
        )
        self.assertEqual(json.loads(gzip.decompress(corpo)), _LINHA_CONTRATO)

    @patch.object(services._client, "get")
    def test_ano_corrente_usa_cache(self, mock_get: MagicMock) -> None:
        """Verifica que a segunda consulta não chama o serviço."""
        mock_get.return_value = _resposta_sidecar(_LINHA_SIDECAR)

        primeira = services.listar_alunos_pap_ano_corrente()
        segunda = services.listar_alunos_pap_ano_corrente()

        self.assertEqual(primeira, segunda)
        mock_get.assert_called_once()

    @patch.object(services._client, "get")
    def test_ano_encerrado_usa_cache_por_ano(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que cada ano encerrado tem a sua chave de cache."""
        mock_get.return_value = _resposta_sidecar(_LINHA_SIDECAR)
        ano = timezone.now().year - 1

        services.listar_alunos_pap_por_ano(ano_letivo=ano)
        services.listar_alunos_pap_por_ano(ano_letivo=ano)
        services.listar_alunos_pap_por_ano(ano_letivo=ano - 1)

        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(
            f"/api/v1/programasedu/alunos/pap/ano-letivo/{ano}"
        )

    @patch.object(services._client, "get")
    def test_ano_corrente_ou_futuro_nao_usa_cache(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que anos corrente e futuro sempre consultam o serviço."""
        mock_get.return_value = _resposta_sidecar(b"[]")
        ano = timezone.now().year

        services.listar_alunos_pap_por_ano(ano_letivo=ano)
        services.listar_alunos_pap_por_ano(ano_letivo=ano)
        services.listar_alunos_pap_por_ano(ano_letivo=ano + 1)

        self.assertEqual(mock_get.call_count, 3)

    @patch.object(services._client, "get")
    def test_erro_do_servico_nao_vai_para_o_cache(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que resposta de erro não é armazenada."""
        erro = _resposta_sidecar(b"{}")
        erro.raise_for_status.side_effect = httpx.HTTPError("falha")
        mock_get.side_effect = [erro, _resposta_sidecar(_LINHA_SIDECAR)]

        with self.assertRaises(httpx.HTTPError):
            services.listar_alunos_pap_ano_corrente()
        corpo = services.listar_alunos_pap_ano_corrente()

        self.assertEqual(json.loads(gzip.decompress(corpo)), _LINHA_CONTRATO)
        self.assertEqual(mock_get.call_count, 2)

    @patch.object(services._client, "get")
    def test_cache_invalido_volta_a_consultar(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica a recuperação quando o valor em cache é inválido."""
        mock_get.return_value = _resposta_sidecar(_LINHA_SIDECAR)
        with (
            patch.object(
                services.cache, "obter_ou_calcular", return_value=b"lixo"
            ),
            self.assertLogs("apps.programasedu.services", "WARNING"),
        ):
            corpo = services.listar_alunos_pap_ano_corrente()

        self.assertEqual(json.loads(gzip.decompress(corpo)), _LINHA_CONTRATO)

    def test_traduz_lista_vazia(self) -> None:
        """Verifica que a lista vazia permanece vazia."""
        self.assertEqual(services._traduzir_alunos_pap(b"[]"), b"[]")

    def test_traduz_json_com_espacos_apos_dois_pontos(self) -> None:
        """Verifica a tradução quando o JSON vem com espaço após ':'."""
        corpo = (
            b'[{"ano_letivo": 2025, "codigo_turma": 9100001, '
            b'"codigo_ue": "000001", "codigo_dre": "100000", '
            b'"codigo_aluno": 9100002, "componente_curricular_id": 50}]'
        )

        traduzido = services._traduzir_alunos_pap(corpo)

        self.assertEqual(json.loads(traduzido), _LINHA_CONTRATO)

    def test_formato_inesperado_usa_serializer(self) -> None:
        """Verifica o fallback quando a chave não casa com o padrão."""
        corpo = (
            b'[{"ano_letivo" : 2025, "codigo_turma" : 9100001, '
            b'"codigo_ue" : "000001", "codigo_dre" : "100000", '
            b'"codigo_aluno" : 9100002, "componente_curricular_id" : 50}]'
        )

        with self.assertLogs("apps.programasedu.services", "WARNING"):
            traduzido = services._traduzir_alunos_pap(corpo)

        self.assertEqual(json.loads(traduzido), _LINHA_CONTRATO)

    def test_paridade_com_o_serializer(self) -> None:
        """Verifica que a tradução em bytes equivale ao serializer."""
        linhas = json.loads(_LINHA_SIDECAR)
        esperado = AlunoTurmaPapSerializer(linhas, many=True).data

        self.assertEqual(
            json.loads(services._traduzir_alunos_pap(_LINHA_SIDECAR)),
            json.loads(JSONRenderer().render(esperado)),
        )


class ListarComponentesTurmasProgramaAlunoTest(SimpleTestCase):
    """Valida a consulta de componentes das turmas de programa do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de componentes do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="123", ano_letivo=2026
        )

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/123/turmas-programa/2026"
            "/componentes-curriculares"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.listar_componentes_turmas_programa_aluno(
            codigo_aluno="7410182", ano_letivo=2026
        )

        self.assertEqual(result, [])


class ObterDadosSrmPaeeAlunoTest(SimpleTestCase):
    """Valida a consulta de dados de SRM/PAEE colaborativo do aluno."""

    @patch.object(services._client, "get")
    def test_chama_path_correto(self, mock_get: MagicMock) -> None:
        """Verifica o path usado na consulta de SRM/PAEE do aluno."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        services.obter_dados_srm_paee_aluno(codigo_aluno="123")

        mock_get.assert_called_once_with(
            "/api/v1/programasedu/alunos/srm-paee/aluno/123"
        )

    @patch.object(services._client, "get")
    def test_retorna_lista_vazia_quando_corpo_vazio(
        self, mock_get: MagicMock
    ) -> None:
        """Verifica que corpo vazio resulta em lista vazia."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        result = services.obter_dados_srm_paee_aluno(codigo_aluno="7410182")

        self.assertEqual(result, [])


class ObterTurmaSrmERegularDoAlunoTest(SimpleTestCase):
    """Valida a orquestração de turmas SRM e regulares do aluno."""

    @patch("apps.programasedu.services.pedagogico_services.listar_turmas")
    @patch("apps.programasedu.services.obter_dados_srm_paee_aluno")
    @patch(
        "apps.programasedu.services.alunos_services."
        "get_turmas_srm_regular_aluno"
    )
    def test_repassa_srm_e_compoe_shape(
        self,
        mock_turmas: MagicMock,
        mock_srm: MagicMock,
        mock_listar: MagicMock,
    ) -> None:
        """Verifica o repasse das turmas SRM e a composição dos campos."""
        mock_turmas.return_value = [
            {
                "codigo_aluno": 7000001,
                "ano_letivo": 2026,
                "nome_aluno": "ALUNO FICTICIO",
                "nome_social_aluno": None,
                "codigo_situacao_matricula": 11,
                "situacao_matricula": "Deslocamento",
                "data_situacao": "2026-01-06",
                "data_nascimento": "2025-11-05",
                "numero_aluno_chamada": None,
                "codigo_turma": 9100001,
                "nome_responsavel": "RESPONSAVEL FICTICIO",
                "tipo_responsavel": 1,
                "ddd_celular": "11",
                "numero_celular": "988887777",
                "data_atualizacao_contato": "2025-01-23",
                "codigo_tipo_turma": 1,
            },
            {
                "codigo_aluno": 7000001,
                "ano_letivo": 2026,
                "codigo_turma": 555,
                "codigo_tipo_turma": 3,
                "ddd_celular": None,
                "numero_celular": None,
            },
        ]
        mock_srm.return_value = [{"codigo_turma": 555}]
        mock_listar.return_value = [
            {
                "codigo": 9100001,
                "nome_turma": "2B",
                "tipo_turno": 1,
                "codigo_etapa_ensino": 5,
                "codigo_ciclo_ensino": 3,
            },
            {
                "codigo": 555,
                "nome_turma": "SRM",
                "tipo_turno": 2,
                "codigo_etapa_ensino": 1,
                "codigo_ciclo_ensino": 2,
            },
        ]

        resultado = services.obter_turma_srm_e_regular_do_aluno("7000001")

        mock_turmas.assert_called_once_with("7000001", [555])
        self.assertEqual(
            sorted(r["codigo_turma"] for r in resultado), [555, 9100001]
        )
        regular = next(r for r in resultado if r["codigo_turma"] == 9100001)
        self.assertEqual(regular["tipo_turno"], 1)
        self.assertEqual(regular["turma_nome"], "2B")
        self.assertEqual(regular["etapa_ensino"], 5)
        self.assertEqual(regular["ciclo_ensino"], 3)
        self.assertEqual(regular["desc_etapa_ensino"], "FUND9A")
        # numero_aluno_chamada ausente → default "000" (paridade legado).
        self.assertEqual(regular["numero_aluno_chamada"], "000")
        self.assertEqual(regular["celular_responsavel"], "11988887777")
        self.assertIsNone(regular["desc_ciclo_ensino"])
        self.assertEqual(
            regular["data_atualizacao_tabela"], "0001-01-01T00:00:00"
        )

    @patch("apps.programasedu.services.obter_dados_srm_paee_aluno")
    @patch(
        "apps.programasedu.services.alunos_services."
        "get_turmas_srm_regular_aluno"
    )
    def test_sem_turmas_retorna_vazio(
        self, mock_turmas: MagicMock, mock_srm: MagicMock
    ) -> None:
        """Verifica que aluno sem turmas resulta em lista vazia."""
        mock_srm.return_value = []
        mock_turmas.return_value = []

        self.assertEqual(
            services.obter_turma_srm_e_regular_do_aluno("123"), []
        )
