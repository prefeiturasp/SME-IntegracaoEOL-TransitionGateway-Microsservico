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

  Cenário: Validar dados Sigpae do funcionário com RF válido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de dados Sigpae do funcionário com RF válido
    Então retorna o status 200
    E o retorno deve conter dados Sigpae do funcionário

  Cenário: Validar erro ao consultar dados Sigpae do funcionário com RF inexistente
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de dados Sigpae do funcionário com RF inexistente
    Então retorna o status 601
    E a mensagem de retorno deve ser "Sem informações na base de dados para o Código Rf informado"

  Cenário: Validar atribuição do funcionário por cargo com RF e código do cargo válidos
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de atribuição do funcionário por cargo com RF e código do cargo válidos
    Então retorna o status 200
    E o retorno deve conter lista de atribuições do funcionário por cargo

  Cenário: Validar retorno vazio de atribuição do funcionário por cargo com RF e código do cargo inexistentes
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de atribuição do funcionário por cargo com RF e código do cargo inexistentes
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar erro ao consultar atribuição do funcionário por cargo com formato de código do cargo inválido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de atribuição do funcionário por cargo com formato de código do cargo inválido
    Então retorna o status 400

  Cenário: Validar cargos do funcionário com RF válido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de cargos do funcionário com RF válido
    Então retorna o status 200
    E o retorno deve conter lista de cargos do funcionário

  Cenário: Validar retorno vazio de cargos do funcionário com RF inexistente
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de cargos do funcionário com RF inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar funcionários por código do cargo válido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionários por código do cargo válido
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por cargo

  Cenário: Validar retorno vazio de funcionários por código do cargo inexistente
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionários por código do cargo inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  @ignore
  Cenário: Validar erro ao consultar funcionários por código do cargo com formato inválido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionários por código do cargo com formato inválido
    Então retorna o status 400

  Cenário: Validar funcionário externo com CPF válido
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionário externo com CPF válido
    Então retorna o status 200
    E o retorno deve conter dados do funcionário externo

  Cenário: Validar retorno vazio de funcionário externo com CPF inexistente
    Dado que possuo acesso à API de funcionários
    Quando realizo consulta de funcionário externo com CPF inexistente
    Então retorna o status 204