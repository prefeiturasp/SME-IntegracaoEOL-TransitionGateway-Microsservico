# language: pt

Funcionalidade: API - Escolas

  Cenário: Validar detalhe de uma escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de detalhe da escola
    Então retorna o status 200
    E o retorno deve conter dados de uma escola

  Cenário: Validar detalhe de uma escola não encontrada
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de detalhe da escola não encontrada
    Então retorna o status 404

  Cenário: Validar dados completos de uma escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de dados completos da escola
    Então retorna o status 200
    E o retorno deve conter dados completos da escola

  Cenário: Validar dados completos de uma escola não encontrada
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de dados completos da escola não encontrada
    Então retorna o status 404

  Cenário: Validar tipos de escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de tipos de escola
    Então retorna o status 200
    E o retorno deve conter lista de tipos de escola

  Cenário: Validar funcionários da escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários da escola
    Então retorna o status 200
    E o retorno deve conter lista de funcionários da escola

  Cenário: Validar funcionários da escola sem resultados
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários da escola não encontrada
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar equipamentos das escolas
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de equipamentos das escolas
    Então retorna o status 200
    E o retorno deve conter lista de equipamentos das escolas

  Cenário: Validar unidade por código EOL
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de unidade EOL da escola
    Então retorna o status 200
    E o retorno deve conter dados da unidade pelo código EOL

  Cenário: Validar sincronizações institucionais da escola
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de sincronizações institucionais da escola
    Então retorna o status 200
    E o retorno deve conter lista de sincronizações institucionais

  Cenário: Validar unidades parceiras
    Dado que possuo acesso à API de escolas
    Quando realizo requisição de unidades parceiras
    Então retorna o status 200
    E o retorno deve conter lista de unidades parceiras

  Cenário: Validar todas as unidades
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de todas as unidades
    Então retorna o status 200
    E o retorno deve conter lista de unidades

  Cenário: Validar tipos de unidade de educação
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de tipos de unidade de educação
    Então retorna o status 200
    E o retorno deve conter lista de tipos de unidades educacionais

  Cenário: Validar dados de escola por código UE válido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de escola pelo código UE válido
    Então retorna o status 200
    E o retorno deve conter dados da escola

  Cenário: Validar retorno vazio de escola para código UE inexistente
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de escola pelo código UE inexistente
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar subprefeituras por código UE válido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de subprefeituras pelo código UE válido
    Então retorna o status 200
    E o retorno deve conter dados de subprefeituras

  Cenário: Validar erro ao consultar subprefeituras com código UE inexistente
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de subprefeituras pelo código UE inexistente
    Então retorna o status 404

  Cenário: Validar funcionários por cargo com código UE e código cargo válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por cargo com código UE e código cargo válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por cargo

  Cenário: Validar retorno vazio de funcionários por cargo com código UE e código cargo inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por cargo com código UE e código cargo inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar funcionários por cargos com código UE e código DRE válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por cargos com código UE e código DRE válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por cargos

  Cenário: Validar retorno vazio de funcionários por cargos com código UE e código DRE inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por cargos com código UE e código DRE inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar funcionários por funções atividades com código UE e código DRE válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por funções atividades com código UE e código DRE válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por funções atividades

  Cenário: Validar retorno vazio de funcionários por funções atividades com código UE e código DRE inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por funções atividades com código UE e código DRE inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar funcionários por função atividade com código UE e código função atividade válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por função atividade com código UE e código função atividade válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por função atividade

  Cenário: Validar retorno vazio de funcionários por função atividade com código UE e código função atividade inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por função atividade com código UE e código função atividade inválidos
    Então retorna o status 204

  Cenário: Validar funcionários por funções externas com código UE, código função externa e código DRE válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por funções externas com código UE, código função externa e código DRE válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por funções externas

  Cenário: Validar retorno vazio de funcionários por funções externas com código UE, código função externa e código DRE inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por funções externas com código UE, código função externa e código DRE inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar funcionários por função externa com código UE e código função externa válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por função externa com código UE e código função externa válidos
    Então retorna o status 200
    E o retorno deve conter lista de funcionários por função externa

  Cenário: Validar retorno vazio de funcionários por função externa com código UE e código função externa inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de funcionários por função externa com código UE e código função externa inválidos
    Então retorna o status 204

  Cenário: Validar quantidade de matrículas por código UE válido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de matrículas pelo código UE válido
    Então retorna o status 200
    E o retorno deve conter dados de quantidade de matrículas

  Cenário: Validar erro ao consultar quantidade de matrículas com código UE inválido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de matrículas pelo código UE inválido
    Então retorna o status 404
    E a mensagem de retorno deve ser "Não foram encontradas turmas para o aluno."

  Cenário: Validar quantidade de matrículas por código DRE válido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de matrículas pelo código DRE válido
    Então retorna o status 200
    E o retorno deve conter dados de quantidade de matrículas por DRE

  Cenário: Validar retorno vazio de quantidade de matrículas com código DRE inválido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de matrículas pelo código DRE inválido
    Então retorna o status 204

  Cenário: Validar quantidade de alunos por código UE válido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de alunos pelo código UE válido
    Então retorna o status 200
    E o retorno deve conter dados de quantidade de alunos

  Cenário: Validar retorno vazio de quantidade de alunos com código UE inválido
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de quantidade de alunos pelo código UE inválido
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar matrículas do aluno por código UE e código aluno válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de matrículas do aluno pelo código UE e código aluno válidos
    Então retorna o status 200
    E o retorno deve conter lista de matrículas do aluno

  Cenário: Validar retorno vazio de matrículas do aluno com código UE e código aluno inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de matrículas do aluno pelo código UE e código aluno inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

    Cenário: Validar modalidades de ensino
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de modalidades de ensino
    Então retorna o status 200
    E o retorno deve conter lista de modalidades de ensino

  Cenário: Validar salas por código UE, tipo de sala e ano letivo válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de salas pelo código UE, tipo de sala e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter dados de salas

  Cenário: Validar erro ao consultar salas com código UE, tipo de sala e ano letivo inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de salas pelo código UE, tipo de sala e ano letivo inválidos
    Então retorna o status 404
    E a mensagem deve ser "Não foram encontradas turmas para a UE 9999999, tipo de sala 9999999 e ano letivo 9999"

  Cenário: Validar turmas por código UE e ano letivo válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de turmas pelo código UE e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas

  Cenário: Validar retorno vazio de turmas com código UE e ano letivo inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de turmas pelo código UE e ano letivo inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia

  Cenário: Validar turmas de sondagem por código UE e ano letivo válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de turmas de sondagem pelo código UE e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter lista de turmas de sondagem

  Cenário: Validar erro ao consultar turmas de sondagem com código UE e ano letivo inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de turmas de sondagem pelo código UE e ano letivo inválidos
    Então retorna o status 404
    E a mensagem de retorno deve ser "Não foram encontradas turmas de sondagem."

  Cenário: Validar professores por código UE e ano letivo válidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de professores pelo código UE e ano letivo válidos
    Então retorna o status 200
    E o retorno deve conter lista de professores

  Cenário: Validar retorno vazio de professores com código UE e ano letivo inválidos
    Dado que possuo acesso à API de escolas
    Quando realizo consulta de professores pelo código UE e ano letivo inválidos
    Então retorna o status 200
    E o retorno deve ser uma lista vazia    