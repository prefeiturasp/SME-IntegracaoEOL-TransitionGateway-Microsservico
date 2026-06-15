# language: pt

Funcionalidade: API - Professores

  Cenário: Validar funcionário ativo
    Dado que possuo acesso à API de professores
    Quando realizo consulta de funcionário ativo
    Então retorna o status 200
    E o retorno deve ser verdadeiro

  Cenário: Validar funcionário não ativo
    Dado que possuo acesso à API de professores
    Quando realizo consulta de funcionário não ativo
    Então retorna o status 200
    E o retorno deve ser falso

  Cenário: Validar nome do servidor
    Dado que possuo acesso à API de professores
    Quando realizo consulta de nome do servidor
    Então retorna o status 200
    E o retorno deve conter nome e cpf

  Cenário: Validar nome do servidor não encontrado
    Dado que possuo acesso à API de professores
    Quando realizo consulta de nome do servidor não encontrado
    Então retorna o status 204

  Cenário: Validar professor válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de validade do professor
    Então retorna o status 200
    E o retorno deve ser verdadeiro

  Cenário: Validar professor não válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de validade do professor não válido
    Então retorna o status 200
    E o retorno deve ser falso

  Cenário: Validar nome do professor
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF
    Então retorna o status 200
    E o retorno deve conter o nome do professor

  Cenário: Validar nome do professor não encontrado
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF com RF inválido 
    Então retorna o status 204