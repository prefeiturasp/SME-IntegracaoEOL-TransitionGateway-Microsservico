# language: pt

Funcionalidade: API - Alunos

  Cenário: Validar informações do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de informações do aluno
    Então retorna o status 200
    E o retorno deve conter informações do aluno

  Cenário: Validar informações do aluno não encontrado
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de informações do aluno não encontrado
    Então retorna o status 204
    E o retorno deve ser vazio

  Cenário: Validar necessidades especiais do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de necessidades especiais do aluno
    Então retorna o status 200
    E o retorno deve conter informações das necessidades especiais

  Cenário: Validar turmas do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno
    Então retorna o status 200
    E o retorno deve conter informações das turmas

  Cenário: Validar lista de alunos por códigos
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de lista de alunos por códigos
    Então retorna o status 200
    E o retorno deve conter informações dos alunos por códigos

  @ignore
  Cenário: Validar alunos PAP do ano corrente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos PAP do ano corrente
    Então retorna o status 200

  Cenário: Validar alunos PAP por ano letivo
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos PAP por ano letivo
    Então retorna o status 200
    E o retorno deve conter informações dos alunos PAP por ano letivo

  Cenário: Validar dados SRM/PAEE do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados SRM PAEE do aluno
    Então retorna o status 200
    E o retorno deve conter dados de SRM PAEE

  Cenário: Validar dados SRM/PAEE do aluno não encontrado
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados SRM PAEE do aluno não encontrado
    Então retorna o status 200
    E o retorno deve ser vazio

  Cenário: Validar turmas do aluno por código
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas do aluno por código
    Então retorna o status 200
    E o retorno deve conter informações das turmas do aluno

  Cenário: Validar turmas PAP por ano letivo e escola
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas PAP por ano letivo e escola
    Então retorna o status 200
    E o retorno deve conter lista de turmas PAP

  Cenário: Validar componentes de turmas de programa do aluno
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de componentes das turmas de programa do aluno
    Então retorna o status 200
    E o retorno deve conter componentes das turmas de programa

  Cenário: Validar verificação de alunos em turmas PAP
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de verificação de alunos em turmas PAP
    Então retorna o status 200

  Cenário: Validar turmas PAP por ano letivo e escola
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas PAP por ano letivo e escola
    Então retorna o status 200
    E o retorno deve conter lista de turmas PAP

  Cenário: Validar componentes de turmas de programa do aluno
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de componentes das turmas de programa do aluno
    Então retorna o status 200
    E o retorno deve conter componentes das turmas de programa