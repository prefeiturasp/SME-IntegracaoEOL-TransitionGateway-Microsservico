"""Valida os serializers do domínio institucional."""

from django.test import SimpleTestCase

from apps.institucional.serializers import (
    DadosEscolaSerializer,
    DRESerializer,
    EquipamentoSerializer,
    EscolaSigpaeSerializer,
    EscolaPorDreETipoSerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    SincronizacaoInstitucionalSerializer,
    UnidadeEolSerializer,
    UnidadeCodigoIntegracaoSerializer,
    UnidadeParceiraSerializer,
    SubprefeiturasSerializer,
    TipoEscolaSerializer,
)


class DRESerializerTest(SimpleTestCase):
    """Valida o serializer de DRE."""

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos obrigatórios preenchidos."""
        data = {
            "codigoDRE": "BT",
            "nomeDRE": "DRE BUTANTA",
            "siglaDRE": "DRE-BT",
        }
        s = DRESerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
        """Rejeita o payload quando falta o campo siglaDRE."""
        data = {"codigoDRE": "BT", "nomeDRE": "DRE BUTANTA"}
        s = DRESerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("siglaDRE", s.errors)


class SubprefeiturasSerializerTest(SimpleTestCase):
    """Valida o serializer de subprefeitura."""

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos obrigatórios preenchidos."""
        data = {
            "codigoSubprefeitura": "00",
            "nomeSubprefeitura": "SUBPREFEITURA TESTE",
        }
        s = SubprefeiturasSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
        """Rejeita o payload quando falta o campo nomeSubprefeitura."""
        data = {"codigoSubprefeitura": "00"}
        s = SubprefeiturasSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("nomeSubprefeitura", s.errors)


class EscolaSigpaeSerializerTest(SimpleTestCase):
    """Valida o serializer de escola SIGPAE."""

    def test_payload_valido(self) -> None:
        """Aceita payload completo do contrato D09."""
        data = {
            "codigoEscola": "019308",
            "nomeEscola": "EMEF TESTE",
            "codigoDRE": "108100",
            "tipoEscola": "EMEF",
            "siglaTipoEscola": "EMEF",
            "nomeDRE": "DRE BUTANTA",
            "siglaDRE": "DRE-BT",
            "codigoSubprefeitura": "50",
            "nomeSubprefeitura": "BUTANTA",
        }
        s = EscolaSigpaeSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_payload_com_campos_extras_nao_entra_no_contrato(self) -> None:
        """Ignora campos extras fora do contrato D09 na saída validada."""
        data = {
            "codigoEscola": "019308",
            "nomeEscola": "EMEF TESTE",
            "codigoDRE": "108100",
            "tipoEscola": "EMEF",
            "siglaTipoEscola": "EMEF",
            "nomeDRE": "DRE BUTANTA",
            "siglaDRE": "DRE-BT",
            "codigoSubprefeitura": "50",
            "nomeSubprefeitura": "BUTANTA",
            "tipoEscolaId": 1,
        }
        s = EscolaSigpaeSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("tipoEscolaId", s.validated_data)


class UnidadeCodigoIntegracaoSerializerTest(SimpleTestCase):
    """Valida o serializer de código de integração por DRE."""

    def test_payload_valido(self) -> None:
        """Aceita payload completo do contrato D11."""
        data = {
            "codigoUe": "019308",
            "nomeUe": "EMEF TESTE",
            "codigoIntegracao": None,
        }
        s = UnidadeCodigoIntegracaoSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_payload_com_campos_extras_nao_entra_no_contrato(self) -> None:
        """Ignora campos extras fora do contrato D11 na saída validada."""
        data = {
            "codigoUe": "019308",
            "nomeUe": "EMEF TESTE",
            "codigoIntegracao": None,
            "dreId": "108100",
        }
        s = UnidadeCodigoIntegracaoSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("dreId", s.validated_data)


class EscolaPorDreETipoSerializerTest(SimpleTestCase):
    """Valida o serializer de escola por DRE e tipo."""

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos obrigatórios preenchidos."""
        data = {
            "codigoEscola": "019308",
            "nomeEscola": "EMEF TESTE",
            "codigoDRE": "BT",
        }
        s = EscolaPorDreETipoSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
        """Rejeita o payload quando falta o campo codigoDRE."""
        data = {"codigoEscola": "019308", "nomeEscola": "EMEF TESTE"}
        s = EscolaPorDreETipoSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("codigoDRE", s.errors)


class EscolaResumoSerializerTest(SimpleTestCase):
    """Valida o serializer de resumo de escola."""

    # Resumo de escola completo aceito pelo serializer.
    _PAYLOAD = {
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

    def test_payload_completo_valido(self) -> None:
        """Aceita payload completo, incluindo campos nullable."""
        s = EscolaResumoSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
        """Aceita payload com campos nullable enviados como None."""
        payload = {
            **self._PAYLOAD,
            "tipoEscolaId": None,
            "tipoUnidadeId": None,
            "subprefeituraId": None,
            "codigoIntegracao": None,
        }
        s = EscolaResumoSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)


class EscolaSerializerTest(SimpleTestCase):
    """Valida o serializer de detalhe de escola."""

    # Detalhe de escola completo aceito pelo serializer.
    _PAYLOAD = {
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

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos preenchidos."""
        s = EscolaSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
        """Aceita payload com campos nullable enviados como None."""
        payload = {
            **self._PAYLOAD,
            "tipoEscolaId": None,
            "codigoIntegracao": None,
        }
        s = EscolaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)


class DadosEscolaSerializerTest(SimpleTestCase):
    """Valida o serializer de dados completos de escola."""

    _PAYLOAD = {
        "nomeDRE": "DIRETORIA REGIONAL TESTE",
        "siglaDRE": "DRE-T",
        "codigoDRE": "000000",
        "codigoINEP": "00000000",
        "siglaTipoEscola": "EMEF",
        "nome": "NOME ESCOLA TESTE",
        "nomeExibicao": "NOME EXIBICAO TESTE",
        "codigo": "000000",
    }

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos preenchidos."""
        s = DadosEscolaSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_opcionais_aceitos(self) -> None:
        """Aceita payload sem os campos opcionais codigoINEP e nomeExibicao."""
        payload = {
            k: v
            for k, v in self._PAYLOAD.items()
            if k not in ("codigoINEP", "nomeExibicao")
        }
        s = DadosEscolaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_obrigatorio_ausente_invalido(self) -> None:
        """Rejeita o payload quando falta o campo obrigatório codigo."""
        payload = {k: v for k, v in self._PAYLOAD.items() if k != "codigo"}
        s = DadosEscolaSerializer(data=payload)
        self.assertFalse(s.is_valid())
        self.assertIn("codigo", s.errors)


class UnidadeEolSerializerTest(SimpleTestCase):
    """Valida o serializer de unidade EOL."""

    def test_payload_valido(self) -> None:
        """Aceita payload completo do contrato E03."""
        data = {
            "codigo": "019251",
            "sigla": "EMEF",
            "nomeUnidade": "EMEF EXEMPLO",
            "tipo": 1,
            "codigoReferencia": "019251",
        }
        serializer = UnidadeEolSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class SincronizacaoInstitucionalSerializerTest(SimpleTestCase):
    """Valida o serializer de sincronização institucional."""

    def test_payload_valido(self) -> None:
        """Aceita payload completo do contrato E23."""
        data = {
            "ueCodigo": "019251",
            "dataAtualizacao": None,
            "dreCodigo": 108100,
            "ueNome": "EMEF EXEMPLO",
            "tipoEscolaCodigo": 1,
        }
        serializer = SincronizacaoInstitucionalSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class UnidadeParceiraSerializerTest(SimpleTestCase):
    """Valida o serializer de unidade parceira."""

    def test_payload_valido(self) -> None:
        """Aceita payload do contrato E26."""
        data = {"codigo": "019251", "nome": "UE PARCEIRA", "email": None}
        serializer = UnidadeParceiraSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class TipoEscolaSerializerTest(SimpleTestCase):
    """Valida o serializer de tipo de escola."""

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos preenchidos."""
        data = {
            "codigo": 1,
            "descricaoSigla": "EMEF",
            "dtAtualizacao": "2026-04-17T00:00:00",
        }
        s = TipoEscolaSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_dt_atualizacao_opcional(self) -> None:
        """Aceita payload sem o campo opcional dtAtualizacao."""
        data = {"codigo": 1, "descricaoSigla": "EMEF"}
        s = TipoEscolaSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_obrigatorio_ausente_invalido(self) -> None:
        """Rejeita o payload quando falta o campo obrigatório codigo."""
        data = {"descricaoSigla": "EMEF"}
        s = TipoEscolaSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("codigo", s.errors)


class EquipamentoSerializerTest(SimpleTestCase):
    """Valida o serializer de equipamento."""

    # Equipamento completo aceito pelo serializer.
    _PAYLOAD = {
        "cd_equipamento": "108901",
        "nm_exibicao_equipamento": "ASSISTENCIA ADMINISTRATIVA-CE PE",
        "nm_equipamento": "ASSISTENCIA ADMINISTRATIVA-CE PE",
        "cd_tp_equipamento": 3,
        "dc_tp_equipamento": "UNIDADE ADMINISTRATIVA",
        "cd_tp_escola": 0,
        "dc_tipo_escola": "",
        "sg_tp_escola": "",
        "cd_diretoria_referencia": "108900",
        "nm_diretoria_referencia": "DRE - PE",
        "nm_exibicao_diretoria_referencia": "DRE - PE",
        "cd_diretoria_portal": "108900",
        "nm_diretoria_portal": "DRE - PE",
        "nm_exibicao_diretoria_portal": "DRE - PE",
        "cd_logradouro": "19674",
        "logradouro": "RUA APUCARANA Nº 215",
        "bairro": "TATUAPE",
        "codigoSubprefeitura": "65",
        "nomeSubprefeitura": "MOOCA",
        "ehCeu": False,
    }

    def test_payload_valido(self) -> None:
        """Aceita payload com todos os campos preenchidos."""
        s = EquipamentoSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
        """Aceita payload com todos os campos nullable enviados como None."""
        payload = {
            **self._PAYLOAD,
            "nm_exibicao_equipamento": None,
            "nm_equipamento": None,
            "cd_tp_equipamento": None,
            "dc_tp_equipamento": None,
            "cd_tp_escola": None,
            "dc_tipo_escola": None,
            "sg_tp_escola": None,
            "cd_diretoria_referencia": None,
            "nm_diretoria_referencia": None,
            "nm_exibicao_diretoria_referencia": None,
            "cd_diretoria_portal": None,
            "nm_diretoria_portal": None,
            "nm_exibicao_diretoria_portal": None,
            "cd_logradouro": None,
            "logradouro": None,
            "bairro": None,
            "codigoSubprefeitura": None,
            "nomeSubprefeitura": None,
        }
        s = EquipamentoSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)

    def test_cd_equipamento_obrigatorio(self) -> None:
        """Rejeita payload sem o campo obrigatório cd_equipamento."""
        payload = {
            k: v for k, v in self._PAYLOAD.items() if k != "cd_equipamento"
        }
        s = EquipamentoSerializer(data=payload)
        self.assertFalse(s.is_valid())
        self.assertIn("cd_equipamento", s.errors)
