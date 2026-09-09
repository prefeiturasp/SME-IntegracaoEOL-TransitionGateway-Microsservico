# language: pt

Funcionalidade: API - Abrangência

  Cenário: Validar estrutura vigente por código DRE válido
    Dado que possuo acesso à API de abrangência
    Quando realizo consulta de estrutura vigente pelo código DRE válido
    Então retorna o status 200
    E o retorno deve conter dados de estrutura vigente

  Cenário: Validar retorno de estrutura vigente com código DRE inexistente
    Dado que possuo acesso à API de abrangência
    Quando realizo consulta de estrutura vigente pelo código DRE inexistente
    Então retorna o status 204

  Cenário: Validar estrutura vigente por filtro de turmas válido
    Dado que possuo acesso à API de abrangência
    Quando realizo envio de estrutura vigente com filtro de turmas válido
    Então retorna o status 200
    E o retorno deve conter dados de estrutura vigente

  Cenário: Validar retorno de estrutura vigente com filtro de turmas inexistente
    Dado que possuo acesso à API de abrangência
    Quando realizo envio de estrutura vigente com filtro de turmas inexistente
    Então retorna o status 204