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
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno por código
    Então retorna o status 200
    E o retorno deve conter informações das turmas do aluno

  Cenário: Validar turmas PAP por ano letivo e escola
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas PAP por ano letivo e escola
    Então retorna o status 200
    E o retorno deve conter lista de turmas PAP

  Cenário: Validar componentes de turmas de programa do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de componentes das turmas de programa do aluno
    Então retorna o status 200
    E o retorno deve conter componentes das turmas de programa

  Cenário: Validar verificação de alunos em turmas PAP
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de verificação de alunos em turmas PAP
    Então retorna o status 200

  Cenário: Validar turmas PAP por ano letivo e escola
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas PAP por ano letivo e escola
    Então retorna o status 200
    E o retorno deve conter lista de turmas PAP

  Cenário: Validar componentes de turmas de programa do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de componentes das turmas de programa do aluno
    Então retorna o status 200
    E o retorno deve conter componentes das turmas de programa

  Cenário: Validar quantidade de alunos matriculados por ano letivo
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de quantidade de alunos matriculados no ano letivo 2026
    Então retorna o status 200
    E o retorno deve conter a quantidade de alunos matriculados

  Cenário: Validar lista de alunos matriculados por ano letivo filtrando por componente curricular
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos matriculados no ano letivo 2026 filtrando por componente curricular
    Então retorna o status 200
    E o retorno deve conter lista de alunos matriculados

  Cenário: Validar consulta de alunos por ano letivo e código do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos no ano letivo 2026 pelo código do aluno
    Então retorna o status 200
    E o retorno deve conter lista de alunos

  Cenário: Validar erro ao consultar dados de acompanhamento escolar sem informar filtros
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar sem informar filtros
    Então retorna o status 601
    E a mensagem de retorno deve ser "Nenhum filtro foi especificado para busca de dados dos alunos para acompanhamento do estudante"

  Cenário: Validar dados de acompanhamento escolar por código do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar pelo código do aluno
    Então retorna o status 200
    E o retorno deve conter lista de dados de acompanhamento escolar

  Cenário: Validar retorno vazio de dados de acompanhamento escolar para código de aluno inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar pelo código do aluno inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar dados de acompanhamento escolar por código da DRE
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar pelo código da DRE
    Então retorna o status 200
    E o retorno deve conter lista de dados de acompanhamento escolar

  Cenário: Validar dados de acompanhamento escolar por código da UE
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar pelo código da UE
    Então retorna o status 200
    E o retorno deve conter lista de dados de acompanhamento escolar

  Cenário: Validar dados de acompanhamento escolar por CPF do responsável
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de dados de acompanhamento escolar pelo CPF do responsável
    Então retorna o status 200
    E o retorno deve conter lista de dados de acompanhamento escolar

  Cenário: Validar lista de responsáveis por código da UE
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsáveis pelo código da UE
    Então retorna o status 200
    E o retorno deve conter lista de responsáveis

  Cenário: Validar retorno vazio de responsáveis para código de UE inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsáveis pelo código da UE inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar lista de responsáveis por código da DRE
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsáveis pelo código da DRE
    Então retorna o status 200
    E o retorno deve conter lista de responsáveis

  Cenário: Validar retorno vazio de responsáveis para código de DRE inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsáveis pelo código da DRE inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar retorno de responsável resumido não encontrado
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsável resumido com CPF não encontrado
    Então retorna o status 204

  Cenário: Validar dados de responsável resumido por CPF válido
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsável resumido com CPF válido
    Então retorna o status 200
    E o retorno deve conter os dados do responsável

  Cenário: Validar erro ao consultar responsável resumido com CPF inválido
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de responsável resumido com CPF inválido
    Então retorna o status 400

  Cenário: Validar alunos ativos da turma
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos ativos da turma
    Então retorna o status 200
    E o retorno deve conter lista de alunos ativos da turma

  Cenário: Validar retorno vazio de alunos ativos da turma para código de turma inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos ativos da turma pelo código da turma inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar alunos ativos da turma por período
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos ativos da turma até a data de referência
    Então retorna o status 200
    E o retorno deve conter lista de alunos ativos da turma

  Cenário: Validar retorno vazio de alunos ativos da turma até data de referência para código da turma inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos ativos da turma até a data de referência pelo código da turma inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar erro ao consultar alunos ativos da turma com data de referência fim inválida
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de alunos ativos da turma com data de referência fim inválida
    Então retorna o status 400
    E a mensagem de retorno deve ser "Parâmetro 'data_referencia_fim' deve ser uma data ISO 8601 válida: recebido '2026-01-32'."

  Cenário: Validar turmas do aluno por código da UE e ano letivo válidos
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno por código da UE e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas do aluno

  Cenário: Validar turmas do aluno por código da UE, ano letivo válidos e nome do aluno
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno por código da UE, ano letivo válidos e nome do aluno
    Então retorna o status 200
    E o retorno deve conter lista de turmas do aluno

  Cenário: Validar erro ao consultar turmas do aluno com código de UE inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno com código de UE inexistente
    Então retorna o status 404
    E a mensagem de retorno deve ser "Não foram encontradas turmas para o aluno."

  Cenário: Validar erro ao consultar turmas do aluno com ano letivo inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno com ano letivo inexistente
    Então retorna o status 404
    E a mensagem de retorno deve ser "Não foram encontradas turmas para o aluno."

  Cenário: Validar erro ao consultar turmas do aluno com nome de aluno inexistente
    Dado que possuo acesso à API de alunos
    Quando realizo consulta de turmas do aluno com nome de aluno inexistente
    Então retorna o status 404
    E a mensagem de retorno deve ser "Não foram encontradas turmas para o aluno."