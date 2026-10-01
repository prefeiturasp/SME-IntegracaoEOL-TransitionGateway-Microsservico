# language: pt

Funcionalidade: API - Turmas

  @ignore
  Cenário: Validar dados de uma turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de dados da turma
    Então retorna o status 200
    E o retorno deve conter dados da turma

  @ignore
  Cenário: Validar listagem de turmas por códigos
    Dado que possuo acesso à API de turmas
    Quando realizo listagem de turmas por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  @ignore
  Cenário: Validar turmas programa por lista de códigos
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas programa por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  @ignore
  Cenário: Validar turmas regulares por lista de códigos
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas regulares por lista de códigos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  @ignore
  Cenário: Validar considerar inativos do aluno na turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de considera inativos do aluno na turma
    Então retorna o status 200
    E o retorno deve conter dados da turma considerando inativos

  @ignore
  Cenário: Validar matriculas do aluno na turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de matriculas do aluno na turma
    Então retorna o status 200
    E o retorno deve conter lista de matriculas

  @ignore
  Cenário: Validar alunos ativos por data de aula
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de alunos ativos por data de aula
    Então retorna o status 200
    E o retorno deve conter lista de alunos ativos

  @ignore
  Cenário: Validar calculo de frequencia da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de calculo de frequencia da turma
    Então retorna o status 200
    E o retorno deve conter calculo de frequencia

  @ignore
  Cenário: Validar considera inativos da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de considera inativos da turma
    Então retorna o status 200
    E o retorno deve conter dados considerando inativos

  @ignore
  Cenário: Validar data de matricula por ticks da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de data de matricula por ticks
    Então retorna o status 200
    E o retorno deve conter dados de matricula da turma 

  @ignore
  Cenário: Validar redis multplex da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de dados redis multplex da turma
    Então retorna o status 200
    E o retorno deve conter dados do redis multplex

  @ignore
  Cenário: Validar componentes curriculares do aluno da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de componentes curriculares do aluno da turma
    Então retorna o status 200
    E o retorno deve conter lista de componentes curriculares do aluno

  @ignore
  Cenário: Validar turmas regulares do aluno por ano letivo
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas regulares do aluno por ano letivo
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  @ignore
  Cenário: Validar turmas historicas gerais do professor
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas historicas gerais do professor
    Então retorna o status 200
    E o retorno deve conter lista de turmas historicas gerais

  @ignore
  Cenário: Validar erro 400 para aluno inválido em considera inativos na turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de considera inativos do aluno na turma com aluno inválido
    Então retorna o status 400

  @ignore
  Cenário: Validar erro 400 para turma inválida em matriculas do aluno
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de matriculas do aluno na turma com turma inválida
    Então retorna o status 400

  @ignore
  Cenário: Validar erro 400 para data de aula inválida
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de alunos ativos por data de aula com ticks inválidos
    Então retorna o status 400

  @ignore
  Cenário: Validar erro 400 para data de matrícula inválida
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de data de matricula por ticks inválidos
    Então retorna o status 400

  @ignore
  Cenário: Validar aluno inexistente em considera inativos na turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de considera inativos do aluno na turma com aluno inexistente
    Então retorna o status 204

  @ignore
  Cenário: Validar aluno inexistente em matriculas do aluno na turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de matriculas do aluno na turma com aluno inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar turma inexistente em alunos ativos por data de aula
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de alunos ativos por data de aula com turma inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar turma inexistente em calculo de frequencia da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de calculo de frequencia da turma com turma inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar turma inexistente em data de matricula por ticks
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de data de matricula por ticks da turma inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar turma inexistente em redis multplex
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de dados redis multplex da turma inexistente
    Então retorna o status 204

  @ignore
  Cenário: Validar aluno inexistente em componentes curriculares da turma
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de componentes curriculares do aluno da turma com aluno inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar aluno inexistente em turmas regulares do aluno por ano letivo
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas regulares do aluno por ano letivo com aluno inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar professor inexistente em turmas históricas gerais
    Dado que possuo acesso à API de turmas
    Quando realizo consulta de turmas historicas gerais do professor inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia
