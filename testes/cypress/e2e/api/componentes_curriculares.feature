# language: pt
Funcionalidade: Território do Saber - Componentes Curriculares
  
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

  Cenario: Validar grade curricular do ano letivo de 2026
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta a grade curricular do ano letivo de 2026
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E a grade curricular deve conter dados do componente e da serie

  Cenario: Validar componentes de regencia do ano de turma 1
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes de regencia do ano de turma 1
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes de regencia devem conter o ano da turma

  Cenario: Validar componentes do funcionario no perfil informado
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes do funcionario 7907206 no perfil 1
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia

  Cenario: Validar componentes da turma sem planejamento
    Dado que possuo acesso à API de componentes curriculares
    Quando realizo consulta aos componentes da turma 2855275 sem planejamento
    Então retorna o status 200
    E o retorno deve conter uma lista de componentes curriculares
    E os componentes detalhados devem conter codigo e regencia
