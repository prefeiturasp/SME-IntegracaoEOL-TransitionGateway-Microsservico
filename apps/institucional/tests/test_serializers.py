"""Valida os serializers do domínio institucional."""

from django.test import SimpleTestCase

from apps.institucional.serializers import (
    DRESerializer,
    DadosEscolaSerializer,
    EquipamentoSerializer,
    EscolaPorDreETipoSerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    SubprefeiturasSerializer,
    TipoEscolaSerializer,
)


class DRESerializerTest(SimpleTestCase):
    """Valida o serializer de DRE."""

    def test_payload_valido(self) -> None:
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
    def test_payload_valido(self) -> None:
        data = {
            "codigoSubprefeitura": "00",
            "nomeSubprefeitura": "SUBPREFEITURA TESTE",
        }
        s = SubprefeiturasSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
        data = {"codigoSubprefeitura": "00"}
        s = SubprefeiturasSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("nomeSubprefeitura", s.errors)


class EscolaPorDreETipoSerializerTest(SimpleTestCase):
    def test_payload_valido(self) -> None:
        data = {
            "codigoEscola": "019308",
            "nomeEscola": "EMEF TESTE",
            "codigoDRE": "BT",
        }
        s = EscolaPorDreETipoSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
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
        s = EscolaResumoSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
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
        s = EscolaSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
        payload = {
            **self._PAYLOAD,
            "tipoEscolaId": None,
            "codigoIntegracao": None,
        }
        s = EscolaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)


class DadosEscolaSerializerTest(SimpleTestCase):
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
        s = DadosEscolaSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_opcionais_aceitos(self) -> None:
        payload = {
            k: v
            for k, v in self._PAYLOAD.items()
            if k not in ("codigoINEP", "nomeExibicao")
        }
        s = DadosEscolaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_obrigatorio_ausente_invalido(self) -> None:
        payload = {k: v for k, v in self._PAYLOAD.items() if k != "codigo"}
        s = DadosEscolaSerializer(data=payload)
        self.assertFalse(s.is_valid())
        self.assertIn("codigo", s.errors)


class TipoEscolaSerializerTest(SimpleTestCase):
    def test_payload_valido(self) -> None:
        data = {
            "codigo": 1,
            "descricaoSigla": "EMEF",
            "dtAtualizacao": "2026-04-17T00:00:00",
        }
        s = TipoEscolaSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_dt_atualizacao_opcional(self) -> None:
        data = {"codigo": 1, "descricaoSigla": "EMEF"}
        s = TipoEscolaSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_obrigatorio_ausente_invalido(self) -> None:
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
        s = EquipamentoSerializer(data=self._PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campos_nullable_aceitos(self) -> None:
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
        payload = {
            k: v
            for k, v in self._PAYLOAD.items()
            if k != "cd_equipamento"
        }
        s = EquipamentoSerializer(data=payload)
        self.assertFalse(s.is_valid())
        self.assertIn("cd_equipamento", s.errors)
