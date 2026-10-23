# language: pt
Funcionalidade: API - Componentes Curriculares
  
  Cenário: Validar agrupamentos correlacionados de território do saber por componente curricular
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta de agrupamentos correlacionados de território do saber para um componente curricular válido
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos correlacionados de território do saber

  Cenário: Validar retorno de agrupamentos correlacionados para código de componente curricular inválido
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta de agrupamentos correlacionados de território do saber para um componente curricular inválido
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos correlacionados de território do saber

  Cenário: Validar agrupamentos correlacionados de território do saber com códigos válidos
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo envio de agrupamentos correlacionados de território do saber com códigos válidos
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos correlacionados de território do saber

  Cenário: Validar agrupamentos correlacionados de território do saber com códigos inválidos
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo envio de agrupamentos correlacionados de território do saber com códigos inválidos
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos correlacionados de território do saber

  Cenário: Validar agrupamentos de território do saber com códigos válidos
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo envio de agrupamentos de território do saber com códigos válidos
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos de território do saber

  Cenário: Validar agrupamentos de território do saber com códigos inválidos
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo envio de agrupamentos de território do saber com códigos inválidos
    Então retorna o status 200
    E o retorno deve conter lista de agrupamentos de território do saber

  Cenario: Validar catalogo de componentes curriculares
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta ao catalogo de componentes curriculares
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes do catalogo devem conter codigo e descricao

  Cenario: Validar grade curricular do ano letivo
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta a grade curricular do ano letivo
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E a grade curricular deve conter dados do componente e da serie

  Cenario: Validar componentes de regencia do ano de turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de regencia do ano de turma 1
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes de regencia devem conter o ano da turma

  Cenario: Validar componentes do funcionario no perfil informado
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes do funcionario no perfil 1
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenario: Validar componentes da turma sem planejamento
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes da turma sem planejamento
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar dados de aula por turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos dados de aula da turma
    Então retorna o status 200
    E o retorno deve conter dados de aula da turma

  @ignore
  Cenário: Validar componentes do funcionario na turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes do funcionario na turma
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar componentes do funcionario na turma não encontrado
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes do funcionario na turma
    Então retorna o status 204

  @ignore
  Cenário: Validar componentes de planejamento da turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de planejamento da turma
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar componentes de planejamento da turma não encontrado
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de planejamento da turma
    Então retorna o status 204

  Cenário: Validar componente PAP da turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo validacao de componente PAP da turma
    Então retorna o status 200
    E o retorno da validacao PAP deve ser booleano

  Cenário: Validar componentes sem atribuicao da turma
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes sem atribuicao da turma
    Então retorna o status 200
    E o retorno deve conter os componentes sem atribuicao

  Cenário: Validar componentes sem atribuicao da turma com retorno vazio
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes sem atribuicao da turma com retorno vazio
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares vazia

  Cenário: Validar componentes de turmas regulares
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de turmas regulares
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar componentes de turmas programa da UE
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de turmas programa da UE
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar componentes da UE por anos escolares
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes da UE por anos escolares
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenário: Validar componentes das turmas da UE
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes das turmas da UE
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia
