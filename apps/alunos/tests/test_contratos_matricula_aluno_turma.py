"""Contratos de saída das consultas de matrícula/aluno/turma."""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, override_settings
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

from apps.alunos.serializers import (
    AlunoMatriculaTurmaSerializer,
    AlunoNaTurmaConsideraInativosSerializer,
    AlunosDaTurmaPorAnoLetivoSerializer,
    MatriculasAlunoNaTurmaSerializer,
    MatriculasTurmasDoAlunoSerializer,
)

DADOS_MATRICULA = {
    "codigo_aluno": 7000001,
    "nome_aluno": "ALUNO FICTICIO UM",
    "nome_social_aluno": None,
    "data_nascimento": "2018-06-21",
    "codigo_situacao_matricula": 1,
    "situacao_matricula": "Ativo",
    "data_situacao": "2025-12-16T12:32:50.857000-03:00",
    "data_matricula": "2025-12-16T12:10:53.233000-03:00",
    "numero_aluno_chamada": None,
    "celular_responsavel": None,
    "possui_deficiencia": True,
    "nome_responsavel": "RESPONSAVEL FICTICIO UM",
    "tipo_responsavel": 1,
    "data_atualizacao_contato": "2025-02-10T17:40:53.043000-03:00",
    "codigo_matricula": 40000003,
    "sequencia": 1,
    "codigo_turma": 9100003,
    "codigo_escola": "000006",
    "ano_letivo": 2025,
    "codigo_dre": "100000",
    # Nem campos de outro domínio nem novos campos do MS devem vazar.
    "codigoComponenteCurricular": 999,
    "transferencia_Interna": True,
    "remanejado": True,
    "escolaTransferencia": "000007",
    "turmaTransferencia": "9100004",
    "turmaRemanejamento": "9100005",
    "parecerConclusivo": "A",
    "tipoTurma": 9,
    "id": 123,
    "campo_extra_do_ms": "não publicar",
}

RESPOSTA_MATRICULA = {
    "codigoAluno": 7000001,
    "nomeAluno": "ALUNO FICTICIO UM",
    "dataNascimento": "2018-06-21T00:00:00Z",
    "nomeSocialAluno": None,
    "codigoSituacaoMatricula": 1,
    "situacaoMatricula": "Ativo",
    "dataSituacao": "2025-12-16T12:32:50.857Z",
    "dataMatricula": "2025-12-16T12:10:53.233Z",
    "numeroAlunoChamada": "000",
    "celularResponsavel": "",
    "possuiDeficiencia": 1,
    "nomeResponsavel": "RESPONSAVEL FICTICIO UM",
    "tipoResponsavel": 1,
    "dataAtualizacaoContato": "2025-02-10T17:40:53.043Z",
    "codigoMatricula": 40000003,
    "sequencia": 1,
    "codigoTurma": 9100003,
    "codigoEscola": "000006",
    "ano": 2025,
    "codigoDre": "100000",
}

CAMPOS_ARTIFICIAIS = {
    "codigoComponenteCurricular": 0,
    "transferencia_Interna": False,
    "remanejado": False,
    "escolaTransferencia": None,
    "turmaTransferencia": None,
    "turmaRemanejamento": None,
    "parecerConclusivo": None,
    "tipoTurma": 0,
    "id": None,
}

CONTRATOS = (
    (
        MatriculasAlunoNaTurmaSerializer,
        "/api/turmas/9100003/aluno/7000001/matriculas",
        "/api/turmas/{codigo_turma}/aluno/{codigo_aluno}/matriculas",
        "get_alunos_por_turma",
        True,
        {"considerar_inativos": True, "codigo_aluno": "7000001"},
    ),
    (
        AlunoNaTurmaConsideraInativosSerializer,
        "/api/turmas/9100003/aluno/7000001/considera-inativos/true",
        "/api/turmas/{codigo_turma}/aluno/{codigo_aluno}/"
        "considera-inativos/{considera_inativos}",
        "get_alunos_turma_considera_inativos",
        False,
        {"considerar_inativos": True, "codigo_aluno": "7000001"},
    ),
    (
        MatriculasTurmasDoAlunoSerializer,
        "/api/turmas/alunos/7000001",
        "/api/turmas/alunos/{codigo_aluno}",
        "get_matriculas_turmas_aluno",
        True,
        {"data_aula_ticks": None, "ano_letivo": None},
    ),
    (
        AlunosDaTurmaPorAnoLetivoSerializer,
        "/api/turmas/9100003/alunos/anosLetivos/2025",
        "/api/turmas/{codigo_turma}/alunos/anosLetivos/{ano_letivo}",
        "get_alunos_por_turma",
        True,
        {"considerar_inativos": True, "ano_letivo": 2025},
    ),
)


class SerializersConsultaMatriculaTest(SimpleTestCase):
    """Verifica campos exatos e conversões dos quatro contratos."""

    def test_campos_exatos_sem_dados_artificiais_ou_extras(self) -> None:
        """Preserva os campos definidos e omite dados artificiais ou extras."""
        for serializer, *_ in CONTRATOS:
            with self.subTest(contrato=serializer.__name__):
                self.assertEqual(
                    serializer(DADOS_MATRICULA).data, RESPOSTA_MATRICULA
                )

    def test_defaults_para_texto_ausente_nulo_ou_vazio(self) -> None:
        """Preserva chamada 000 e celular vazio quando não informados."""
        for serializer, *_ in CONTRATOS:
            for valor in (None, "", "ausente"):
                with self.subTest(contrato=serializer.__name__, valor=valor):
                    dados = dict(DADOS_MATRICULA)
                    for campo in (
                        "numero_aluno_chamada",
                        "celular_responsavel",
                    ):
                        if valor == "ausente":
                            dados.pop(campo)
                        else:
                            dados[campo] = valor
                    self.assertEqual(
                        serializer(dados).data, RESPOSTA_MATRICULA
                    )

    def test_textos_preenchidos_e_indicador_zero(self) -> None:
        """Preserva zeros à esquerda e indicadores inteiros."""
        dados = {
            **DADOS_MATRICULA,
            "numero_aluno_chamada": "007",
            "celular_responsavel": "11999990000",
            "possui_deficiencia": False,
        }
        esperado = {
            **RESPOSTA_MATRICULA,
            "numeroAlunoChamada": "007",
            "celularResponsavel": "11999990000",
            "possuiDeficiencia": 0,
        }
        for serializer, *_ in CONTRATOS:
            with self.subTest(contrato=serializer.__name__):
                self.assertEqual(serializer(dados).data, esperado)

    def test_datas_e_responsavel_nulos(self) -> None:
        """Preserva os campos opcionais quando seus valores são nulos."""
        dados = {
            **DADOS_MATRICULA,
            "data_nascimento": None,
            "data_situacao": None,
            "data_matricula": None,
            "data_atualizacao_contato": None,
            "nome_responsavel": None,
            "tipo_responsavel": None,
        }
        esperado = {
            **RESPOSTA_MATRICULA,
            "dataNascimento": None,
            "dataSituacao": None,
            "dataMatricula": None,
            "dataAtualizacaoContato": None,
            "nomeResponsavel": None,
            "tipoResponsavel": None,
        }
        for serializer, *_ in CONTRATOS:
            with self.subTest(contrato=serializer.__name__):
                self.assertEqual(serializer(dados).data, esperado)

    def test_serializer_amplo_preserva_campos_das_outras_rotas(self) -> None:
        """Preserva o contrato amplo compartilhado pelas outras views."""
        self.assertEqual(
            AlunoMatriculaTurmaSerializer(DADOS_MATRICULA).data,
            {**RESPOSTA_MATRICULA, **CAMPOS_ARTIFICIAIS},
        )


class ViewsConsultaMatriculaTest(SimpleTestCase):
    """Verifica contratos públicos, cardinalidade e ausência de dados."""

    def setUp(self) -> None:
        """Prepara cliente autenticado sem acessar o banco."""
        self.client = APIClient()
        self.client.force_authenticate(user=User(username="teste-contrato"))

    def test_respostas_exatas_e_parametros_por_consulta(self) -> None:
        """Verifica os campos de saída, a cardinalidade e os parâmetros."""
        segunda = {**DADOS_MATRICULA, "codigo_matricula": 40000004}
        for _, rota, _, metodo, lista, parametros in CONTRATOS:
            with (
                self.subTest(rota=rota),
                patch(f"apps.alunos.views.services.{metodo}") as consulta,
            ):
                consulta.return_value = [DADOS_MATRICULA, segunda]
                resposta = self.client.get(rota)
                self.assertEqual(resposta.status_code, 200)
                esperado = (
                    [
                        RESPOSTA_MATRICULA,
                        {**RESPOSTA_MATRICULA, "codigoMatricula": 40000004},
                    ]
                    if lista
                    else RESPOSTA_MATRICULA
                )
                self.assertEqual(resposta.json(), esperado)
                codigo = "7000001" if "/turmas/alunos/" in rota else "9100003"
                consulta.assert_called_once_with(codigo, **parametros)

    def test_ausencia_preserva_lista_vazia_ou_sem_conteudo(self) -> None:
        """Preserva 200 com lista vazia ou 204 conforme a consulta."""
        for indice, (_, rota, _, metodo, _, _) in enumerate(CONTRATOS):
            with (
                self.subTest(rota=rota),
                patch(f"apps.alunos.views.services.{metodo}", return_value=[]),
            ):
                resposta = self.client.get(rota)
                if indice in (0, 2):
                    self.assertEqual(resposta.status_code, 200)
                    self.assertEqual(resposta.json(), [])
                else:
                    self.assertEqual(resposta.status_code, 204)
                    self.assertEqual(resposta.content, b"")

    @override_settings(APPEND_SLASH=True)
    def test_rotas_sem_barra_mantem_contrato_original(self) -> None:
        """Responde diretamente sem barra e mantém 404 com barra final."""
        for _, rota, _, metodo, lista, _ in CONTRATOS[:2]:
            with (
                self.subTest(rota=rota),
                patch(
                    f"apps.alunos.views.services.{metodo}",
                    return_value=[DADOS_MATRICULA],
                ) as consulta,
            ):
                sem_barra = self.client.get(rota)
                self.assertEqual(sem_barra.status_code, 200)
                self.assertNotIn("Location", sem_barra)
                esperado = (
                    [RESPOSTA_MATRICULA] if lista else RESPOSTA_MATRICULA
                )
                self.assertEqual(sem_barra.json(), esperado)
                consulta.reset_mock()
                com_barra = self.client.get(f"{rota}/")
                self.assertEqual(com_barra.status_code, 404)
                consulta.assert_not_called()

    def test_considera_inativos_false(self) -> None:
        """Preserva o contrato e repassa o filtro booleano falso."""
        with patch(
            "apps.alunos.views.services.get_alunos_turma_considera_inativos",
            return_value=[DADOS_MATRICULA],
        ) as servico:
            rota = CONTRATOS[1][1].replace("/true", "/false")
            resposta = self.client.get(rota)
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.json(), RESPOSTA_MATRICULA)
            servico.assert_called_once_with(
                "9100003", considerar_inativos=False, codigo_aluno="7000001"
            )


class SchemaConsultaMatriculaTest(SimpleTestCase):
    """Verifica que cada operação documenta o contrato que publica."""

    def test_componentes_distintos_com_campos_exatos(self) -> None:
        """Documenta o componente específico e os campos de cada consulta."""
        schema = SchemaGenerator().get_schema(request=None, public=True)
        for serializer, _, rota, _, lista, _ in CONTRATOS:
            with self.subTest(rota=rota):
                respostas = schema["paths"][rota]["get"]["responses"]
                resposta = respostas["200"]["content"]["application/json"][
                    "schema"
                ]
                if lista:
                    self.assertEqual(resposta["type"], "array")
                    resposta = resposta["items"]
                componente = serializer.__name__.removesuffix("Serializer")
                self.assertEqual(
                    resposta, {"$ref": f"#/components/schemas/{componente}"}
                )
                campos = schema["components"]["schemas"][componente][
                    "properties"
                ]
                self.assertEqual(set(campos), set(RESPOSTA_MATRICULA))
                for campo in ("numeroAlunoChamada", "celularResponsavel"):
                    self.assertFalse(campos[campo].get("nullable", False))
                self.assertTrue(campos["nomeSocialAluno"]["nullable"])
                if rota == CONTRATOS[1][2] or rota == CONTRATOS[3][2]:
                    self.assertNotIn("content", respostas["204"])
        for _, _, rota, _, _, _ in CONTRATOS[:2]:
            self.assertNotIn(f"{rota}/", schema["paths"])
