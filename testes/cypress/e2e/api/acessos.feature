# language: pt

Funcionalidade: API - Acessos
  
  Cenário: Validar funcionário ativo
    Dado que possuo acesso à API de acessos
    Quando realizo consulta de funcionário ativo
    Então retorna o status 200
    E o retorno deve ser verdadeiro

  Cenário: Validar funcionário não ativo
    Dado que possuo acesso à API de acessos
    Quando realizo consulta de funcionário não ativo
    Então retorna o status 200
    E o retorno deve ser falso