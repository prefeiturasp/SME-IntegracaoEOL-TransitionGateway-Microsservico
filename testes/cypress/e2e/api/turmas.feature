# language: pt

Funcionalidade: API - Turmas

  Cenário: Validar dados de uma turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de dados da turma
    Então retorna o status 200
    E o retorno deve conter dados da turma

  Cenário: Validar listagem de turmas por códigos
    Dado que possuo acesso à API de turmas
    Quando realizo listagem de turmas por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  Cenário: Validar turmas programa por lista de códigos
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas programa por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  Cenário: Validar turmas regulares por lista de códigos
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas regulares por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas
