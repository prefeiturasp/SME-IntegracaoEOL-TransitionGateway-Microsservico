# language: pt

Funcionalidade: API - Professores

  Cenário: Validar funcionário ativo
    Dado que possuo acesso à API de professores
    Quando realizo consulta de funcionário ativo
    Então o status da resposta deve ser válido para professores
    E o retorno deve ser booleano

  Cenário: Validar nome do servidor
    Dado que possuo acesso à API de professores
    Quando realizo consulta de nome do servidor
    Então o status da resposta deve ser válido para professores
    E o retorno deve conter nome e cpf

  Cenário: Validar professor válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de validade do professor
    Então o status da resposta deve ser válido para professores
    E o retorno deve ser booleano

  Cenário: Validar nome do professor
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF
    Então o status da resposta deve ser válido para professores
    E o retorno deve conter o nome do professor