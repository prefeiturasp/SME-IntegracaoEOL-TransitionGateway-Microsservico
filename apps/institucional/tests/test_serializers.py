from django.test import SimpleTestCase

from apps.institucional.serializers import (
    DRESerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    EquipamentoSerializer,
)


class DRESerializerTest(SimpleTestCase):
    def test_payload_valido(self) -> None:
        data = {"codigoDRE": "BT", "nomeDRE": "DRE BUTANTA", "siglaDRE": "DRE-BT"}
        s = DRESerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_campo_ausente_invalido(self) -> None:
        data = {"codigoDRE": "BT", "nomeDRE": "DRE BUTANTA"}
        s = DRESerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("siglaDRE", s.errors)


class EscolaResumoSerializerTest(SimpleTestCase):
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
        payload = {**self._PAYLOAD, "tipoEscolaId": None,
                   "tipoUnidadeId": None, "subprefeituraId": None, "codigoIntegracao": None}
        s = EscolaResumoSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)


class EscolaSerializerTest(SimpleTestCase):
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
        payload = {**self._PAYLOAD, "tipoEscolaId": None, "codigoIntegracao": None}
        s = EscolaSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)


class EquipamentoSerializerTest(SimpleTestCase):
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
        payload = {k: v for k, v in self._PAYLOAD.items() if k != "cd_equipamento"}
        s = EquipamentoSerializer(data=payload)
        self.assertFalse(s.is_valid())
        self.assertIn("cd_equipamento", s.errors)
