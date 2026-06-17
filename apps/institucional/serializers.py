"""Serializers de saída do domínio institucional."""

from rest_framework import serializers


class DRESerializer(serializers.Serializer):
    """Serializa dados de Diretoria Regional de Educação."""

    codigoDRE = serializers.CharField()
    nomeDRE = serializers.CharField()
    siglaDRE = serializers.CharField()


class SubprefeiturasSerializer(serializers.Serializer):
    """Serializa subprefeitura vinculada a uma DRE."""

    codigoSubprefeitura = serializers.CharField()
    nomeSubprefeitura = serializers.CharField()


class EscolaPorDreETipoSerializer(serializers.Serializer):
    """Serializa escola retornada por DRE e tipo."""

    codigoEscola = serializers.CharField()
    nomeEscola = serializers.CharField()
    codigoDRE = serializers.CharField()


class EscolaResumoSerializer(serializers.Serializer):
    """Serializa o resumo de escola por DRE."""

    codigoEscola = serializers.CharField()
    nomeEscola = serializers.CharField()
    codigoDRE = serializers.CharField()
    tipoEscola = serializers.CharField()
    siglaTipoEscola = serializers.CharField()
    nomeDRE = serializers.CharField()
    siglaDRE = serializers.CharField()
    codigoSubprefeitura = serializers.CharField()
    nomeSubprefeitura = serializers.CharField()


class EscolaSerializer(serializers.Serializer):
    """Serializa dados de escola."""

    codigoEscola = serializers.CharField()
    nomeEscola = serializers.CharField()
    nomeDRE = serializers.CharField()
    siglaDRE = serializers.CharField()
    codigoDRE = serializers.CharField()
    tipoEscola = serializers.CharField()
    siglaTipoEscola = serializers.CharField()
    codigoTipoEscola = serializers.IntegerField(
        allow_null=True, required=False
    )


class DadosEscolaSerializer(serializers.Serializer):
    """Serializa dados completos de escola."""

    nomeDRE = serializers.CharField()
    siglaDRE = serializers.CharField()
    codigoDRE = serializers.CharField()
    codigoINEP = serializers.CharField(allow_null=True, required=False)
    siglaTipoEscola = serializers.CharField()
    nome = serializers.CharField()
    nomeExibicao = serializers.CharField(allow_null=True, required=False)
    codigo = serializers.CharField()


class TipoEscolaSerializer(serializers.Serializer):
    """Serializa tipo de escola."""

    codigo = serializers.IntegerField()
    descricaoSigla = serializers.CharField()
    dtAtualizacao = serializers.CharField(allow_null=True, required=False)


class EquipamentoSerializer(serializers.Serializer):
    """Serializa dados de equipamento escolar."""

    cd_equipamento = serializers.CharField()
    nm_exibicao_equipamento = serializers.CharField(allow_null=True)
    nm_equipamento = serializers.CharField(allow_null=True)
    cd_tp_equipamento = serializers.IntegerField(allow_null=True)
    dc_tp_equipamento = serializers.CharField(allow_null=True)
    cd_tp_escola = serializers.IntegerField(allow_null=True)
    dc_tipo_escola = serializers.CharField(allow_null=True, allow_blank=True)
    sg_tp_escola = serializers.CharField(allow_null=True, allow_blank=True)
    cd_diretoria_referencia = serializers.CharField(allow_null=True)
    nm_diretoria_referencia = serializers.CharField(allow_null=True)
    nm_exibicao_diretoria_referencia = serializers.CharField(allow_null=True)
    cd_diretoria_portal = serializers.CharField(allow_null=True)
    nm_diretoria_portal = serializers.CharField(allow_null=True)
    nm_exibicao_diretoria_portal = serializers.CharField(allow_null=True)
    cd_logradouro = serializers.IntegerField(allow_null=True)
    logradouro = serializers.CharField(allow_null=True)
    bairro = serializers.CharField(allow_null=True)
    codigoSubprefeitura = serializers.CharField(allow_null=True)
    nomeSubprefeitura = serializers.CharField(allow_null=True)
    ehCeu = serializers.BooleanField()


class UnidadeEducacionalSerializer(serializers.Serializer):
    """Serializa unidade educacional."""

    codigoEscola = serializers.CharField()
    nomeEscola = serializers.CharField()
    codigoDRE = serializers.CharField()
    nomeDRE = serializers.CharField()
    siglaDRE = serializers.CharField()
    tipoEscola = serializers.CharField()
    siglaTipoEscola = serializers.CharField()


class TipoUnidadeEducacaoSerializer(serializers.Serializer):
    """Serializa tipo de unidade educacional."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()
    sigla = serializers.CharField()
