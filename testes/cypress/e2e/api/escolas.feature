# language: pt

Funcionalidade: API - Escolas

  Cenário: Validar detalhe de uma escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de detalhe da escola
    Então retorna o status 200
    E o retorno deve conter dados da escola

  Cenário: Validar detalhe de uma escola não encontrada
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de detalhe da escola não encontrada
    Então retorna o status 404

  Cenário: Validar dados completos de uma escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de dados completos da escola
    Então retorna o status 200
    E o retorno deve conter dados completos da escola

  Cenário: Validar dados completos de uma escola não encontrada
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de dados completos da escola não encontrada
    Então retorna o status 404

  Cenário: Validar tipos de escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de tipos de escola
    Então retorna o status 200
    E o retorno deve conter lista de tipos de escola

  Cenário: Validar funcionários da escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários da escola
    Então retorna o status 200
    E o retorno deve conter lista de funcionários da escola

  Cenário: Validar funcionários da escola sem resultados
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários da escola não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar equipamentos das escolas
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de equipamentos das escolas
    Então retorna o status 200
    E o retorno deve conter lista de equipamentos das escolas

  Cenário: Validar unidade por código EOL
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de unidade EOL da escola
    Então retorna o status 200
    E o retorno deve conter dados da unidade pelo código EOL

  Cenário: Validar sincronizações institucionais da escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de sincronizações institucionais da escola
    Então retorna o status 200
    E o retorno deve conter lista de sincronizações institucionais

  Cenário: Validar unidades parceiras
    Dado que possuo acesso à API de escolas
    Quando realizo requisição de unidades parceiras
    Então retorna o status 200
    E o retorno deve conter lista de unidades parceiras

  Cenário: Validar todas as unidades
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de todas as unidades
    Então retorna o status 200
    E o retorno deve conter lista de unidades

  Cenário: Validar tipos de unidade de educação
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de tipos de unidade de educação
    Então retorna o status 200
    E o retorno deve conter lista de tipos de unidades educacionais