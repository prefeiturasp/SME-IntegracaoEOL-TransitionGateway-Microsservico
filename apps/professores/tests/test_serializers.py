"""Valida serializers do domínio professores."""

from unittest.mock import patch

from django.http import QueryDict
from django.test import SimpleTestCase
from rest_framework import serializers

from apps.professores.serializers import (
    BuscarProfessorTitularPorDisciplinaSerializer,
    AbrangenciaTemporariaSerializer,
    CargoFuncionarioConectaSerializer,
    DisciplinasFuncionarioPathSerializer,
    DisciplinaTurmaAgrupamentoSerializer,
    DisciplinaTurmaAtribuidaSerializer,
    DreUeAtribuicaoCargoSerializer,
    FuncionarioCargoSerializer,
    FuncionarioConectaFormacaoSerializer,
    FuncionarioDadosSigpaeSerializer,
    FuncionarioExternoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoExternaSerializer,
    FuncionarioLegadoSerializer,
    FuncionarioLoginSerializer,
    FuncionariosConectaFormacaoFiltroSerializer,
    FuncionariosEscolaCargosQuerySerializer,
    FuncionariosEscolaFuncoesExternasQuerySerializer,
    FuncionarioSgpLegadoSerializer,
    FuncionarioUnidadeLegadoSerializer,
    ProfessorAtribuicaoInternaSerializer,
    ProfessorAtribuicaoPeriodoPathSerializer,
    FuncionariosPerfisQuerySerializer,
    FuncionarioUnidadeLegadoSerializer,
    ProfessorAtribuicaoTurmaDisciplinaSerializer,
    ProfessorAutocompleteQuerySerializer,
    ProfessorAutoCompleteSerializer,
    ProfessoresTitularesParametrosSerializer,
    ProfessoresTitularesPorTurmasQuerySerializer,
    ProfessoresTitularesPorUeParametrosSerializer,
    ProfessorRecorrenciaDataSerializer,
    ProfessorBuscarPorRfQuerySerializer,
    ProfessorRfDreUeQuerySerializer,
    ProfessorStatusAtribuicaoSerializer,
    ProfessorTurmaAtribuidaSimplificadaSerializer,
    SupervisorLegadoSerializer,
    TextoEstritoField,
    TurmaAtribuidaProfessorSerializer,
    TurmaElegivelLegadoSerializer,
    TurmasAtribuidasLegadoSerializer,
    UsuarioConectaFormacaoSerializer,
    VerificarAtribuicaoDisciplinaQuerySerializer,
)


class ProfessoresTitularesPorTurmasQuerySerializerTest(SimpleTestCase):
    """Valida os códigos da busca de titulares por várias turmas."""

    def test_converte_nome_legado_para_snake_case(self) -> None:
        """Disponibiliza os códigos validados com nome interno Python."""
        serializer = ProfessoresTitularesPorTurmasQuerySerializer(
            data={"codigosTurmas": ["3022108", "3022109"]}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data,
            {"codigos_turmas": ["3022108", "3022109"]},
        )

    def test_rejeita_lista_vazia(self) -> None:
        """Exige ao menos um código de turma."""
        serializer = ProfessoresTitularesPorTurmasQuerySerializer(
            data={"codigosTurmas": []}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("codigosTurmas", serializer.errors)


class TextoEstritoFieldTest(SimpleTestCase):
    """Valida campo de texto estrito."""

    def test_erro_quando_super_nao_retorna_texto(self) -> None:
        field = TextoEstritoField()

        with (
            patch.object(
                serializers.CharField,
                "to_internal_value",
                return_value=123,
            ),
            self.assertRaises(serializers.ValidationError),
        ):
            field.to_internal_value("abc")


class VerificarAtribuicaoDisciplinaQuerySerializerTest(SimpleTestCase):
    """Valida a conversão do indicador de território do saber."""

    def test_converte_false_textual_em_booleano(self) -> None:
        serializer = VerificarAtribuicaoDisciplinaQuerySerializer(
            data={"territorioSaber": "false"}
        )

        self.assertTrue(serializer.is_valid())
        self.assertIs(serializer.validated_data["territorioSaber"], False)

    def test_aplica_false_quando_parametro_ausente(self) -> None:
        serializer = VerificarAtribuicaoDisciplinaQuerySerializer(data={})

        self.assertTrue(serializer.is_valid())
        self.assertIs(serializer.validated_data["territorioSaber"], False)

    def test_rejeita_booleano_invalido(self) -> None:
        serializer = VerificarAtribuicaoDisciplinaQuerySerializer(
            data={"territorioSaber": "talvez"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("territorioSaber", serializer.errors)


class FuncionariosPerfisQuerySerializerTest(SimpleTestCase):
    """Valida filtros de funcionários por perfil."""

    def test_normaliza_aliases_legados(self) -> None:
        serializer = FuncionariosPerfisQuerySerializer(
            data={
                "CodigoDre": " 108100 ",
                "CodigoUe": " 000532 ",
                "CodigoRf": " 7654321 ",
                "NomeServidor": " ANA ",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {
                "codigo_dre": "108100",
                "codigo_ue": "000532",
                "codigo_rf": "7654321",
                "nome_servidor": "ANA",
            },
        )

    def test_rejeita_quando_sem_codigo_dre_ou_rf(self) -> None:
        serializer = FuncionariosPerfisQuerySerializer(
            data={"CodigoDre": " ", "CodigoRf": ""}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            FuncionariosPerfisQuerySerializer.mensagem_dre_ou_rf_obrigatorio,
        )


class CargoFuncionarioConectaSerializerTest(SimpleTestCase):
    """Valida contrato legado de cargos por RF."""

    def test_serializa_campos_legados(self) -> None:
        serializer = CargoFuncionarioConectaSerializer(
            {
                "rf": 7758626,
                "cpf": "12345678900",
                "cd_cargo_base": 3360,
                "cargo_base": "DIRETOR",
                "cd_dre_cargo_base": "108100",
                "cd_ue_cargo_base": "000532",
                "ue_cargo_base": "ESCOLA",
                "tipo_vinculo_cargo_base": 1,
                "data_inicio_cargo_base": "2024-01-01T00:00:00",
                "cd_cargo_sobreposto": None,
                "cargo_sobreposto": None,
                "cd_dre_cargo_sobreposto": None,
                "cd_ue_cargo_sobreposto": None,
                "ue_cargo_sobreposto": None,
                "tipo_vinculo_cargo_sobreposto": None,
                "data_inicio_cargo_sobreposto": None,
                "cd_funcao_atividade": None,
                "funcao_atividade": None,
                "cd_dre_funcao_atividade": None,
                "cd_ue_funcao_atividade": None,
                "ue_funcao_atividade": None,
                "tipo_vinculo_funcao_atividade": None,
                "data_inicio_funcao_atividade": None,
            }
        )

        self.assertEqual(serializer.data["cdCargoBase"], 3360)
        self.assertEqual(serializer.data["cargoBase"], "DIRETOR")
        self.assertEqual(serializer.data["cdDreCargoBase"], "108100")


class FuncionarioConectaFormacaoSerializerTest(SimpleTestCase):
    """Valida contrato de funcionários do Conecta Formação."""

    def test_serializa_campos_legados(self) -> None:
        serializer = FuncionarioConectaFormacaoSerializer(
            {
                "rf": "7758626",
                "nome": "ANA",
                "cpf": "12345678900",
                "cargo_codigo": "3360",
                "cargo": "DIRETOR",
                "cargo_dre_codigo": "108100",
                "cargo_ue_codigo": "000532",
                "funcao_codigo": None,
                "funcao": None,
                "funcao_dre_codigo": None,
                "funcao_ue_codigo": None,
                "tipo_vinculo": 1,
            }
        )

        self.assertEqual(serializer.data["cargoCodigo"], "3360")
        self.assertEqual(serializer.data["cargoDreCodigo"], "108100")
        self.assertEqual(serializer.data["tipoVinculo"], 1)


class FuncionariosConectaFormacaoFiltroSerializerTest(SimpleTestCase):
    """Valida filtros de funcionários do Conecta Formação."""

    def test_preserva_parametros_repetidos(self) -> None:
        query = QueryDict(
            "codigos_cargos=3360&codigos_cargos=3239"
            "&codigos_dres=108100&eh_tipo_jornada_jeif=true"
        )
        serializer = FuncionariosConectaFormacaoFiltroSerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["codigos_cargos"],
            [3360, 3239],
        )
        self.assertEqual(serializer.validated_data["codigos_dres"], ["108100"])
        self.assertIs(serializer.validated_data["eh_tipo_jornada_jeif"], True)


class AbrangenciaTemporariaSerializerTest(SimpleTestCase):
    """Valida parâmetros temporários de abrangência."""

    def test_normaliza_parametros_temporarios(self) -> None:
        query = QueryDict(
            "abrangencia=4&cargos=3239&funcoesId=1&grupo=2"
            "&dreCodigo=108100&ehPerfilManual=true"
        )
        serializer = AbrangenciaTemporariaSerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {
                "abrangencia": 4,
                "cargos": [3239],
                "funcoes": [1],
                "grupo": 2,
                "dre_codigo": "108100",
                "eh_perfil_manual": True,
            },
        )

    def test_ignora_inteiros_invalidos(self) -> None:
        query = QueryDict("abrangencia=abc&cargos=abc&funcoesId=1")
        serializer = AbrangenciaTemporariaSerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["abrangencia"])
        self.assertIsNone(serializer.validated_data["cargos"])
        self.assertEqual(serializer.validated_data["funcoes"], [1])


class DisciplinasFuncionarioPathSerializerTest(SimpleTestCase):
    """Valida parâmetros de caminho das disciplinas do funcionário."""

    def test_valida_parametros_obrigatorios(self) -> None:
        serializer = DisciplinasFuncionarioPathSerializer(
            data={
                "login": "000001",
                "id_perfil": "perfil",
                "codigo_turma": "3030050",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_rejeita_login_vazio(self) -> None:
        serializer = DisciplinasFuncionarioPathSerializer(
            data={
                "login": " ",
                "id_perfil": "perfil",
                "codigo_turma": "3030050",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "É necessário informar o login.",
        )


class QueryParamsSerializerTest(SimpleTestCase):
    """Valida serializers de parâmetros de consulta."""

    def test_preserva_listas_e_campos_simples(self) -> None:
        query = QueryDict("cargos=3239&cargos=3240&dre_codigo=1")
        serializer = FuncionariosEscolaCargosQuerySerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {"cargos": ["3239", "3240"], "dre_codigo": "1"},
        )

    def test_exige_codigo_dre_em_funcoes_externas(self) -> None:
        serializer = FuncionariosEscolaFuncoesExternasQuerySerializer(
            data=QueryDict("funcoes=5")
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("codigo_dre", serializer.errors)

    def test_normaliza_filtros_de_rf_dre_ue(self) -> None:
        query = QueryDict("dre_id=1&ue_id=019465&buscar_outros_cargos=true")
        serializer = ProfessorRfDreUeQuerySerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {
                "dre_id": "1",
                "ue_id": "019465",
                "buscar_outros_cargos": "true",
            },
        )

    def test_normaliza_autocomplete(self) -> None:
        query = QueryDict("ue_id=019465&nome=ana")
        serializer = ProfessorAutocompleteQuerySerializer(data=query)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {"ue_id": "019465", "nome": "ana"},
        )


class ProfessorBuscarPorRfQuerySerializerTest(SimpleTestCase):
    """Valida filtros da busca de professor por RF."""

    def test_converte_booleano_textual(self) -> None:
        serializer = ProfessorBuscarPorRfQuerySerializer(
            data=QueryDict("buscar_outros_cargos=false")
        )

        self.assertTrue(serializer.is_valid())
        self.assertIs(
            serializer.validated_data["buscar_outros_cargos"],
            False,
        )

    def test_rejeita_booleano_invalido(self) -> None:
        serializer = ProfessorBuscarPorRfQuerySerializer(
            data=QueryDict("buscar_outros_cargos=sim")
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("buscar_outros_cargos", serializer.errors)


class DreUeAtribuicaoCargoSerializerTest(SimpleTestCase):
    """Valida contrato de atribuição por cargo."""

    def test_serializa_campos_legados(self) -> None:
        serializer = DreUeAtribuicaoCargoSerializer(
            {
                "codigo_dre": "108100",
                "codigo_ue": "000532",
            }
        )

        self.assertEqual(serializer.data["dreCodigo"], "108100")
        self.assertEqual(serializer.data["ueCodigo"], "000532")


class UsuarioConectaFormacaoSerializerTest(SimpleTestCase):
    """Valida contrato de usuários do Conecta Formação."""

    def test_serializa_campos_legados(self) -> None:
        serializer = UsuarioConectaFormacaoSerializer(
            {
                "login": "7758626",
                "nome": "ANA",
                "nome_social": None,
                "perfil": "perfil",
            }
        )

        self.assertEqual(serializer.data["login"], "7758626")
        self.assertIsNone(serializer.data["nomeSocial"])


class ProfessorStatusAtribuicaoSerializerTest(SimpleTestCase):
    """Valida o contrato legado do status da atribuição."""

    def test_mapeia_campos_do_sidecar(self) -> None:
        payload = {
            "ano_atribuicao": 2026,
            "data_cancelamento": None,
            "data_disponibilizacao": "2026-07-28",
            "data_fim_turma": "2026-12-22",
            "codigo_motivo_disponibilizacao": None,
        }

        self.assertEqual(
            ProfessorStatusAtribuicaoSerializer(payload).data,
            {
                "anoAtribuicao": 2026,
                "dataCancelamento": None,
                "dataDisponibilizacao": "2026-07-28",
                "dataFimTurma": "2026-12-22",
                "codigoMotivoDisponibilizacao": None,
            },
        )


class ProfessorAtribuicaoTurmaDisciplinaSerializerTest(SimpleTestCase):
    """Valida o contrato legado da atribuição por disciplina."""

    def test_mapeia_campos_e_aceita_lista_agrupada_nula(self) -> None:
        payload = {
            "codigo_turma": "3032577",
            "ano_letivo": None,
            "nome_turma": "7A",
            "data_inicio_atribuicao": "2026-06-09",
            "data_fim_atribuicao": "2026-12-22",
            "data_fim_turma": "2026-12-22",
            "ano_atribuicao": 2026,
            "codigo_rf": "6230504",
            "disciplina_id": "89",
            "disciplina_nome": "CIENCIAS",
            "disciplinas_agrupadas_ids": None,
            "nome_professor": "LAZARO PRETEL",
        }

        data = ProfessorAtribuicaoTurmaDisciplinaSerializer(payload).data

        self.assertEqual(data["codigoTurma"], 3032577)
        self.assertEqual(data["disciplinaId"], 89)
        self.assertIsNone(data["disciplinasAgrupadasIds"])


class ProfessorAtribuicaoInternaSerializerTest(SimpleTestCase):
    """Valida o contrato canônico consumido pelo serviço de professores."""

    def test_padroniza_tipos_e_completa_campos_ausentes(self) -> None:
        """Normaliza dados comuns aos endpoints de atribuição."""
        data = ProfessorAtribuicaoInternaSerializer(
            {
                "codigo_turma": 3032577,
                "ano_letivo": "2026",
                "disciplina_id": 89,
            }
        ).data

        self.assertEqual(data["codigo_turma"], "3032577")
        self.assertEqual(data["ano_letivo"], 2026)
        self.assertEqual(data["disciplina_id"], "89")
        self.assertIsNone(data["data_inicio_atribuicao"])
        self.assertEqual(data["disciplinas_agrupadas_ids"], [])


class ProfessorAtribuicaoPeriodoPathSerializerTest(SimpleTestCase):
    """Valida os parâmetros da consulta de atribuição por período."""

    def test_rejeita_periodo_invertido(self) -> None:
        """Rejeita data inicial posterior à data final."""
        serializer = ProfessorAtribuicaoPeriodoPathSerializer(
            data={
                "codigo_rf": "000001",
                "codigo_turma": "3032577",
                "componente_curricular_id": "89",
                "data_inicio_periodo": "2026-08-01",
                "data_fim_periodo": "2026-07-31",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class ProfessoresTitularesParametrosSerializerTest(SimpleTestCase):
    """Valida os filtros da busca de professores titulares."""

    def test_converte_data_e_booleano(self) -> None:
        """Converte parâmetros externos para o contrato interno."""
        serializer = ProfessoresTitularesParametrosSerializer(
            data={
                "codigo_turma": "3032577",
                "codigoRF": "000001",
                "dataReferencia": "2026-07-28",
                "realiza_agrupamento": "true",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["codigo_rf"], "000001")
        self.assertTrue(serializer.validated_data["realiza_agrupamento"])


class BuscarProfessorTitularPorDisciplinaSerializerTest(SimpleTestCase):
    """Valida o DTO legado de professor titular por disciplina."""

    def test_mapeia_campos_do_contrato_legado(self) -> None:
        """Converte os nomes internos para os nomes definidos no DTO."""
        data = BuscarProfessorTitularPorDisciplinaSerializer(
            {
                "professor_rf": "000001",
                "nome_professor": "PROFESSOR",
                "disciplina": "CIENCIAS",
                "disciplina_id": "89",
                "disciplinas_id": "89,90",
                "turma_id": 3032577,
            }
        ).data

        self.assertEqual(
            data,
            {
                "professorRf": "000001",
                "nome_Professor": "PROFESSOR",
                "disciplina": "CIENCIAS",
                "disciplina_Id": "89",
                "disciplinas_Id": "89,90",
                "turma_Id": 3032577,
            },
        )


class ProfessoresTitularesPorUeParametrosSerializerTest(SimpleTestCase):
    """Valida os parâmetros da busca de titulares por UE."""

    def test_converte_data_e_aplica_agrupamento_padrao(self) -> None:
        """Converte a data e usa agrupamento falso quando ausente."""
        serializer = ProfessoresTitularesPorUeParametrosSerializer(
            data={
                "ue_codigo": "094765",
                "data_referencia": "2026-08-10",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["data_referencia"].date().isoformat(),
            "2026-08-10",
        )
        self.assertIs(serializer.validated_data["realiza_agrupamento"], False)


class ProfessorRecorrenciaDataSerializerTest(SimpleTestCase):
    """Valida a serialização da permissão de persistência por data."""

    def test_mapeia_contrato_legado(self) -> None:
        serializer = ProfessorRecorrenciaDataSerializer(
            {
                "data": "2026-07-27T00:00:00",
                "pode_persistir": True,
            }
        )

        self.assertEqual(
            serializer.data,
            {
                "data": "2026-07-27T00:00:00",
                "podePersistir": True,
            },
        )


class FuncionarioSerializerTest(SimpleTestCase):
    """Valida serialização dos contratos de funcionário."""

    def test_serializa_campos(self) -> None:
        casos = [
            (
                FuncionarioCargoSerializer,
                {"codigo_rf": "7730900", "nome": None, "cargo_id": 3239},
                {
                    "funcionarioRF": "7730900",
                    "funcionarioNome": None,
                    "cargoId": 3239,
                },
            ),
            (
                FuncionarioFuncaoAtividadeSerializer,
                {
                    "codigo_rf": "7795246",
                    "nome": None,
                    "codigo_funcao_atividade": 30,
                },
                {
                    "funcionarioRF": "7795246",
                    "funcionarioNome": None,
                    "funcaoAtividadeId": 30,
                },
            ),
            (
                FuncionarioFuncaoExternaSerializer,
                {"cpf": "11610699840", "funcao_externo": 5},
                {"funcionarioCpf": "11610699840", "funcaoExternaId": 5},
            ),
            (
                SupervisorLegadoSerializer,
                {
                    "codigo_rf": "000001",
                    "nome_servidor": "NOME SERVIDOR",
                },
                {
                    "codigoRF": "000001",
                    "nomeServidor": "NOME SERVIDOR",
                },
            ),
        ]
        for serializer_cls, payload, esperado in casos:
            with self.subTest(serializer=serializer_cls.__name__):
                self.assertEqual(serializer_cls(payload).data, esperado)

    def test_serializa_funcionario_externo(self) -> None:
        payload = {
            "nome_pessoa": "NOME PESSOA",
            "nome_pai": "NOME PAI",
            "nome_mae": "NOME MAE",
            "data_nascimento": "1995-01-12T00:00:00",
            "rg": "000000043171462",
            "cpf": "42347206826",
            "titulo_eleitoral": "401921980116",
            "pis_pasep": "13866991818",
            "codigo_contrato_externo": 4796,
            "codigo_ue": "327221",
            "nome_ue": "JARDIM NORONHA",
            "funcao": "PROFESSOR",
            "tipo_funcionario": "FUNCIONARIO REDE PARCEIRA",
        }

        self.assertEqual(
            FuncionarioExternoSerializer(payload).data,
            {
                "nomePessoa": "NOME PESSOA",
                "nomePai": "NOME PAI",
                "nomeMae": "NOME MAE",
                "dataNascimento": "1995-01-12T00:00:00",
                "rg": "000000043171462",
                "cpf": "42347206826",
                "tituloEleitoral": "401921980116",
                "pisPasep": "13866991818",
                "codigoContratoExterno": 4796,
                "codigoUE": "327221",
                "nomeUe": "JARDIM NORONHA",
                "funcao": "PROFESSOR",
                "tipoFuncionario": "FUNCIONARIO REDE PARCEIRA",
            },
        )

    def test_serializa_funcionario_por_login(self) -> None:
        payload = {
            "login": "8970971",
            "nome_servidor": "NOME SERVIDOR",
            "perfil": "00000000-0000-0000-0000-000000000000",
        }

        self.assertEqual(
            FuncionarioLoginSerializer(payload).data,
            {
                "login": "8970971",
                "nomeServidor": "NOME SERVIDOR",
                "perfil": "00000000-0000-0000-0000-000000000000",
            },
        )

    def test_serializa_funcionario_por_unidade(self) -> None:
        payload = {
            "login": "16161610191",
            "nome_servidor": "LUCAS SOUZA",
            "perfil": "5be1e074-37d6-e911-abd6-f81654fe895d",
        }

        self.assertEqual(
            FuncionarioUnidadeLegadoSerializer(payload).data,
            {
                "login": "16161610191",
                "nomeServidor": "LUCAS SOUZA",
                "perfil": "5be1e074-37d6-e911-abd6-f81654fe895d",
            },
        )

    def test_serializa_dados_sigpae(self) -> None:
        payload = {
            "rf": "7758626",
            "cpf": "28386997842",
            "email": "ingrid.marcela@sme.prefeitura.sp.gov.br",
            "cargos": [
                {
                    "codigo_cargo": 3239,
                    "descricao_cargo": "PROF.ED.INF.E ENS.FUND.I",
                    "codigo_unidade": "092223",
                    "descricao_unidade": "MARIA ISABEL",
                    "codigo_dre": "108800",
                    "contrato_externo": False,
                }
            ],
            "nome": "INGRID MARCELA BARBA",
            "inexistente_eol": False,
        }

        self.assertEqual(
            FuncionarioDadosSigpaeSerializer(payload).data,
            {
                "rf": "7758626",
                "cpf": "28386997842",
                "email": "ingrid.marcela@sme.prefeitura.sp.gov.br",
                "cargos": [
                    {
                        "codigoCargo": 3239,
                        "descricaoCargo": "PROF.ED.INF.E ENS.FUND.I",
                        "codigoUnidade": "092223",
                        "descricaoUnidade": "MARIA ISABEL",
                        "codigoDre": "108800",
                        "contratoExterno": False,
                    }
                ],
                "nome": "INGRID MARCELA BARBA",
                "inexistenteEol": False,
            },
        )


class FuncionarioLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário no contrato legado."""

    def test_serializa_campos(self) -> None:
        payload = {
            "codigo_funcao_atividade": 30,
            "codigo_rf": "000001",
            "funcao_externo": 5,
            "nome": "ANA",
            "tipo_funcao_externo": 7,
        }

        self.assertEqual(
            FuncionarioLegadoSerializer(payload).data,
            {
                "cd_Cargo": 0,
                "codigoFuncaoAtividade": 30,
                "codigoRf": "000001",
                "funcaoExterno": 5,
                "login": "000001",
                "nomeServidor": "ANA",
                "tipoFuncaoExterno": 7,
            },
        )


class FuncionarioSgpLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de funcionário SGP no contrato legado."""

    def test_serializa_campos(self) -> None:
        payload = {
            "cd_cargo": "3360",
            "codigo_funcao_atividade": 30,
            "codigo_rf": "000001",
            "funcao_externo": 5,
            "login": None,
            "nome_servidor": "ANA",
            "tipo_funcao_externo": 7,
        }

        self.assertEqual(
            FuncionarioSgpLegadoSerializer(payload).data,
            {
                "cd_Cargo": 3360,
                "codigoFuncaoAtividade": 30,
                "codigoRf": "000001",
                "funcaoExterno": 5,
                "login": None,
                "nomeServidor": "ANA",
                "tipoFuncaoExterno": 7,
            },
        )


class DisciplinaTurmaSerializerTest(SimpleTestCase):
    """Valida serialização de disciplinas no contrato legado."""

    def test_disciplina_atribuida_preserva_tipo_escola(self) -> None:
        payload = {
            "codigo": 512,
            "codigo_componente_curricular_pai": None,
            "codigo_componente_territorio_saber": None,
            "descricao": "ARTE",
            "regencia": False,
            "tipo_escola": "EMEF",
            "territorio_saber": False,
        }

        self.assertEqual(
            DisciplinaTurmaAtribuidaSerializer(payload).data,
            {
                "codDisciplina": 512,
                "codDisciplinaPai": None,
                "codCompTerritorioSaber": None,
                "disciplina": "ARTE",
                "regencia": False,
                "tipoEscola": "EMEF",
                "territorioSaber": False,
                "professor": None,
            },
        )

    def test_disciplina_agrupamento_usa_zero_e_tipo_escola_nulo(self) -> None:
        payload = {
            "codigo": 138,
            "codigo_componente_curricular_pai": 512,
            "codigo_componente_territorio_saber": None,
            "codigos_territorios_agrupamento": [1, 2],
            "descricao": "LINGUA PORTUGUESA",
            "regencia": True,
            "territorio_saber": True,
        }

        self.assertEqual(
            DisciplinaTurmaAgrupamentoSerializer(payload).data[
                "codCompTerritorioSaber"
            ],
            0,
        )
        self.assertIsNone(
            DisciplinaTurmaAgrupamentoSerializer(payload).data["tipoEscola"]
        )


class TurmasAtribuidasLegadoSerializerTest(SimpleTestCase):
    """Valida agrupamento de turmas atribuídas."""

    def test_agrupa_por_dre_ue_e_remove_turma_repetida(self) -> None:
        payload = [
            {
                "codigo_dre": "108100",
                "dre": "DRE TESTE",
                "dre_abreviacao": "DRE-T",
                "codigo_escola": "000532",
                "ue": "EMEF TESTE",
                "codigo_tipo_escola": 1,
                "codigo_turma": 3030050,
                "ano": "1",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "codigo_modalidade": None,
                "nome_turma": "1A",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 4,
            },
            {
                "codigo_dre": "108100",
                "codigo_escola": "000532",
                "codigo_turma": 3030050,
            },
        ]

        data = TurmasAtribuidasLegadoSerializer(payload).data

        self.assertEqual(len(data["dres"]), 1)
        self.assertEqual(len(data["dres"][0]["ues"]), 1)
        self.assertEqual(len(data["dres"][0]["ues"][0]["turmas"]), 1)
        self.assertEqual(
            data["dres"][0]["ues"][0]["turmas"][0]["codigoModalidade"],
            0,
        )

    def test_aceita_campos_da_composicao_de_professor(self) -> None:
        payload = [
            {
                "cod_dre": "109200",
                "dre": "DIRETORIA REGIONAL DE EDUCACAO SAO MATEUS",
                "dre_abrev": "DRE - SM",
                "cod_escola": "013803",
                "ue": "JULIO DE GRAMMONT",
                "cod_tipo_escola": 1,
                "cod_turma": 3018605,
                "ano": "7",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "cod_modalidade": 5,
                "nome_turma": "7B",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 1,
            },
            {
                "cod_dre": "109200",
                "dre": "DIRETORIA REGIONAL DE EDUCACAO SAO MATEUS",
                "dre_abrev": "DRE - SM",
                "cod_escola": "013803",
                "ue": "JULIO DE GRAMMONT",
                "cod_tipo_escola": 1,
                "cod_turma": 3018602,
                "ano": "7",
                "ano_letivo": 2026,
                "modalidade": "Fundamental",
                "cod_modalidade": 5,
                "nome_turma": "7A",
                "semestre": 0,
                "duracao_turno": 5,
                "tipo_turno": 1,
            },
        ]

        data = TurmasAtribuidasLegadoSerializer(payload).data
        dre = data["dres"][0]
        ue = dre["ues"][0]

        self.assertEqual(dre["codigo"], "109200")
        self.assertEqual(dre["abreviacao"], "DRE - SM")
        self.assertEqual(ue["codigo"], "013803")
        self.assertEqual(ue["codTipoEscola"], 1)
        self.assertEqual(
            [turma["codigo"] for turma in ue["turmas"]],
            [3018602, 3018605],
        )
        self.assertEqual(ue["turmas"][0]["modalidade"], "Fundamental")
        self.assertEqual(ue["turmas"][0]["codigoModalidade"], 5)
        self.assertEqual(ue["turmas"][0]["duracaoTurno"], 5)

    def test_retorna_payload_nao_lista_sem_transformar(self) -> None:
        payload = {"abrangencia": None}

        self.assertEqual(
            TurmasAtribuidasLegadoSerializer(payload).data, payload
        )


class TurmaElegivelLegadoSerializerTest(SimpleTestCase):
    """Valida serialização de turma elegível."""

    def test_serializa_campos(self) -> None:
        payload = {"nome_turma": "1A", "cod_turma": 3030050}

        self.assertEqual(
            TurmaElegivelLegadoSerializer(payload).data,
            {"nomeTurma": "1A", "codTurma": 3030050},
        )


class ProfessorAutoCompleteSerializerTest(SimpleTestCase):
    """Valida serialização de professor para autocomplete."""

    def test_serializa_nome_servidor_como_nome(self) -> None:
        payload = {"codigo_rf": "000001", "nome_servidor": "ANA SILVA"}

        data = ProfessorAutoCompleteSerializer(payload).data

        self.assertEqual(
            data,
            {"codigoRF": "000001", "nome": "ANA SILVA"},
        )


class ProfessorTurmaAtribuidaSimplificadaSerializerTest(SimpleTestCase):
    """Valida serialização simplificada de turma atribuída ao professor."""

    def test_serializa_campos(self) -> None:
        payload = {
            "codigoTurma": 3030050,
            "nomeTurma": "1A",
            "componenteCurricular": "Matemática",
            "dataInicioAtribuicao": "2026-02-03",
            "dataFimAtribuicao": None,
            "ano": "1",
            "etapaEnsino": 1,
        }

        data = ProfessorTurmaAtribuidaSimplificadaSerializer(payload).data

        self.assertEqual(data, payload)


class TurmaAtribuidaProfessorSerializerTest(SimpleTestCase):
    """Valida serialização de turma atribuída ao professor."""

    def test_serializa_campos(self) -> None:
        mapeamento = [
            # (campo_entrada,      campo_saida,       valor)
            ("cod_escola", "codEscola", "019465"),
            ("cod_turma", "codTurma", 3030050),
            ("tipo_turma", "tipoTurma", 1),
            ("ano", "ano", "1"),
            ("ano_letivo", "anoLetivo", 2026),
            ("cod_modalidade", "codModalidade", 5),
            ("cod_dre", "codDre", "108100"),
            ("dre", "dre", "DRE TESTE"),
            ("dre_abrev", "dreAbrev", "DRE-T"),
            ("modalidade", "modalidade", "Fundamental"),
            ("nome_turma", "nomeTurma", "1A"),
            ("semestre", "semestre", 0),
            ("tipo_ue", "tipoUE", "EMEF"),
            ("cod_tipo_ue", "codTipoUE", 1),
            ("cod_ue", "codUe", "019465"),
            ("ue", "ue", "EMEF TESTE"),
            ("ue_abrev", "ueAbrev", "EMEF T."),
            ("tipo_escola", "tipoEscola", "EMEF"),
            ("cod_tipo_escola", "codTipoEscola", 1),
            ("duracao_turno", "duracaoTurno", 5),
            ("tipo_turno", "tipoTurno", 4),
            ("ensino_especial", "ensinoEspecial", False),
            ("serie_ensino", "serieEnsino", "1 ANO"),
            ("data_inicio_turma", "dataInicioTurma", "2024-02-01T00:00:00"),
            ("data_fim_turma", "dataFimTurma", None),
            ("extinta", "extinta", False),
        ]
        payload = {entrada: valor for entrada, _, valor in mapeamento}
        esperado = {saida: valor for _, saida, valor in mapeamento}

        self.assertEqual(
            TurmaAtribuidaProfessorSerializer(payload).data, esperado
        )
