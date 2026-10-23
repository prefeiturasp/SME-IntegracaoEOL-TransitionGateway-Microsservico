# language: pt

Funcionalidade: API - Professores

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

  Cenário: Validar autocomplete de professores com DRE, UE e nome válidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de autocomplete de professores com DRE, UE e nome válidos
    Então retorna o status 200
    E o retorno deve conter lista de professores no autocomplete

  Cenário: Validar retorno vazio de autocomplete de professores com DRE, UE e nome inválidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de autocomplete de professores com DRE, UE e nome inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar busca de professores por lista de RF com ano letivo e registro funcional válidos
    Dado que possuo acesso à API de professores
    Quando realizo envio de busca de professores por lista de RF com ano letivo e registro funcional válidos
    Então retorna o status 200
    E o retorno deve conter lista de professores por RF

  Cenário: Validar retorno vazio de busca de professores por lista de RF com ano letivo e registro funcional inválidos
    Dado que possuo acesso à API de professores
    Quando realizo envio de busca de professores por lista de RF com ano letivo e registro funcional inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar busca de professor por RF e ano letivo válidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter dados do professor por RF

  Cenário: Validar retorno vazio de professor por RF e ano letivo inválidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF e ano letivo inválidos
    Então retorna o status 204

  Cenário: Validar busca de professor por RF, DRE e UE com dados válidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF, ano letivo, DRE e UE válidos
    Então retorna o status 200
    E o retorno deve conter dados do professor por RF, DRE e UE

  Cenário: Validar retorno vazio de professor por RF, DRE e UE com dados inválidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de professor por RF, ano letivo, DRE e UE inválidos
    Então retorna o status 204

  Cenário: Validar turmas de professor por disciplina com registro funcional, disciplina e turma válidos
    Dado que possuo acesso à API de professores
    Quando realizo envio de turmas de professor por disciplina com registro funcional, disciplina e turma válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas do professor por disciplina

  Cenário: Validar retorno vazio de turmas de professor por disciplina com registro funcional, disciplina e turma inválidos
    Dado que possuo acesso à API de professores
    Quando realizo envio de turmas de professor por disciplina com registro funcional, disciplina e turma inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar professor EMEI com registro funcional válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de EMEI do professor com registro funcional válido
    Então retorna o status 200
    E o retorno deve ser um RF EMEI verdadeiro

  Cenário: Validar professor EMEI com registro funcional inválido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de EMEI do professor com registro funcional inválido
    Então retorna o status 200
    E o retorno deve ser falso

  Cenário: Validar turmas do professor com registro funcional válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas do professor com registro funcional válido
    Então retorna o status 200
    E o retorno deve conter lista de turmas do professor

  Cenário: Validar retorno vazio de turmas do professor com registro funcional inválido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas do professor com registro funcional inválido
    Então retorna o status 204

  Cenário: Validar turmas do professor por ano letivo com registro funcional válido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas do professor por ano letivo com registro funcional válido
    Então retorna o status 200
    E o retorno deve conter lista de turmas do professor

  Cenário: Validar retorno vazio de turmas do professor por ano letivo com registro funcional inválido
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas do professor por ano letivo com registro funcional inválido
    Então retorna o status 404
    E a mensagem de erro deve ser Não foram encontradas turmas atribuídas.

  Cenário: Validar turmas atribuídas pelo professor na escola com dados válidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas atribuídas pelo professor na escola com dados válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas atribuídas ao professor na escola

  Cenário: Validar retorno vazio de turmas atribuídas pelo professor na escola com dados inválidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas atribuídas pelo professor na escola com dados inválidos
    Então retorna o status 404

  Cenário: Validar turmas de professores por escola e ano letivo válidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas de professores por escola e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas por escola e ano letivo

  Cenário: Validar retorno vazio de turmas de professores por escola e ano letivo inválidos
    Dado que possuo acesso à API de professores
    Quando realizo consulta de turmas de professores por escola e ano letivo inválidos
    Então retorna o status 404

  Cenário: Validar verificação de atribuição do professor em data válida
    Dado que possuo acesso à API de professores
    Quando realizo consulta de atribuição do professor em data válida
    Então retorna o status 200
    E o retorno deve ser falso

  Cenário: Validar verificação de atribuição do professor em data inválida
    Dado que possuo acesso à API de professores
    Quando realizo consulta de atribuição do professor em data inválida
    Então retorna o status 400

  Cenário: Validar status da atribuição do professor em turma
    Dado que possuo acesso à API de professores
    Quando realizo consulta de status da atribuição do professor em turma
    Então retorna o status 200
    E o retorno deve conter status da atribuição do professor

  Cenário: Validar verificação de atribuição do professor em turma e disciplina com data válida
    Dado que possuo acesso à API de professores
    Quando realizo consulta de atribuição do professor em turma e disciplina com data válida
    Então retorna o status 200
    E o retorno deve ser falso

  Cenário: Validar atribuições de professor em turma e disciplina no formato ISO
    Dado que possuo acesso à API de professores
    Quando realizo consulta de atribuições de professor em turma e disciplina no formato ISO
    Então retorna o status 200
    E o retorno deve conter lista de atribuições de turma e disciplina em data ISO