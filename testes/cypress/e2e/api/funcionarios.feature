# language: pt

Funcionalidade: API - Funcionários

  Cenário: Validar nome do servidor
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de nome do servidor
    Então retorna o status 200
    E o retorno deve conter nome e cpf

  Cenário: Validar nome do servidor não encontrado
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de nome do servidor não encontrado
    Então retorna o status 204

  Cenário: Validar nome do funcionário no EOL
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de nome do funcionário no EOL
    Então retorna o status 200
    E o retorno deve conter o nome do funcionário

  Cenário: Validar nome do funcionário no EOL não encontrado
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de nome do funcionário no EOL não encontrado
    Então retorna o status 204

  Cenário: Validar funcionários pelos RFs informados
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionários por RFs
    Então retorna o status 200
    E o retorno deve conter os RFs dos funcionários

  Cenário: Validar funcionários por RFs informados não encontrados
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionários por RFs com RFs inválidos
    Então retorna o status 200
    E o retorno deve ser vazio