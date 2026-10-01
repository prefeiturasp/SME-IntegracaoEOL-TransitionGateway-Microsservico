# language: pt

Funcionalidade: API - DREs

  @ignore
  Cenário: Validar listagem de todas as DREs
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de listagem de DREs
    Então retorna o status 200
    E o retorno deve conter lista de DREs

  @ignore
  Cenário: Validar DREs por lista de códigos
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de DRE por lista de códigos
    Então retorna o status 200
    E o retorno deve conter dados das DREs

  @ignore
  @ignore
  Cenário: Validar DREs por lista de códigos não encontradas
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de DRE por lista de códigos não encontradas
    Então retorna o status 204

  @ignore
  Cenário: Validar detalhe de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de detalhe da DRE
    Então retorna o status 200
    E o retorno deve conter dados da DRE

  @ignore
  Cenário: Validar detalhe de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de detalhe da DRE não encontrada
    Então retorna o status 404

  @ignore
  Cenário: Validar escolas de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas da DRE
    Então retorna o status 200
    E o retorno deve conter lista de escolas da DRE

  @ignore
  @ignore
  Cenário: Validar escolas de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  @ignore
  Cenário: Validar escolas de uma DRE por tipo de unidade
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas por tipo
    Então retorna o status 200
    E o retorno deve conter lista de escolas da DRE

  @ignore
  Cenário: Validar subprefeituras de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de subprefeituras da DRE
    Então retorna o status 200
    E o retorno deve conter lista de subprefeituras da DRE

  @ignore
  @ignore
  Cenário: Validar subprefeituras de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de subprefeituras da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar UEs de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de UEs da DRE
    Então retorna o status 200
    E o retorno deve conter lista de UEs da DRE

  @ignore
  @ignore
  Cenário: Validar UEs de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de UEs da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar unidades de uma DRE
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades da DRE
    Então retorna o status 200
    E o retorno deve conter lista de unidades da DRE

  @ignore
  @ignore
  Cenário: Validar unidades de uma DRE não encontrada
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades da DRE não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar escolas Sigpae por código EOL da DRE válido
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas Sigpae pelo código EOL da DRE válido
    Então retorna o status 200
    E o retorno deve conter lista de escolas Sigpae

  @ignore
  Cenário: Validar retorno vazio de escolas Sigpae para código EOL da DRE inexistente
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de escolas Sigpae pelo código EOL da DRE inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar unidades por código de integração da DRE com código EOL válido
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades por código de integração da DRE com código EOL válido
    Então retorna o status 200
    E o retorno deve conter lista de unidades de uma DRE

  @ignore
  Cenário: Validar retorno vazio de unidades por código de integração para código EOL da DRE inexistente
    Dado que possuo acesso à API de DREs
    Quando realizo consulta de unidades por código de integração da DRE com código EOL inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia