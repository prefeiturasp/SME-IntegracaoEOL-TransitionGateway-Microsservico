# language: pt

Funcionalidade: API - DREs

  Cenário: Validar listagem de todas as DREs
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de listagem de DREs
    Então retorna o status 200
    E o retorno deve conter lista de DREs

  Cenário: Validar DREs por lista de códigos
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de DRE por lista de códigos
    Então retorna o status 200
    E o retorno deve conter dados das DREs

  Cenário: Validar DREs por lista de códigos não encontradas
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de DRE por lista de códigos não encontradas
    Então retorna o status 204

  Cenário: Validar detalhe de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de detalhe da DRE
    Então retorna o status 200
    E o retorno deve conter dados da DRE

  Cenário: Validar detalhe de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de detalhe da DRE não encontrada
    Então retorna o status 404

  Cenário: Validar escolas de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas da DRE
    Então retorna o status 200
    E o retorno deve conter lista de escolas da DRE

  @ignore
  Cenário: Validar escolas de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar escolas de uma DRE por tipo de unidade
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas por tipo
    Então retorna o status 200
    E o retorno deve conter lista de escolas da DRE

  Cenário: Validar subprefeituras de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de subprefeituras da DRE
    Então retorna o status 200
    E o retorno deve conter lista de subprefeituras da DRE

  Cenário: Validar subprefeituras de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de subprefeituras da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar UEs de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de UEs da DRE
    Então retorna o status 200
    E o retorno deve conter lista de UEs da DRE

  Cenário: Validar UEs de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de UEs da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar unidades de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades da DRE
    Então retorna o status 200
    E o retorno deve conter lista de unidades da DRE

  Cenário: Validar unidades de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia
