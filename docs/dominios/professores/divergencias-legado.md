# Divergencias entre endpoints do legado e do novo EOL

Este documento registra diferenças identificadas entre o comportamento dos
endpoints legados e as respostas retornadas pelo novo EOL.

## `professores/escolas/<str:codigo_eol_escola>/turmas/anos_letivos/<int:ano_letivo>/`

No novo EOL, este endpoint evita a apresentacao de registros repetidos quando
eles possuem os mesmos dados.

No legado, a resposta podia trazer mais de uma ocorrencia equivalente para a
mesma turma/professor. No novo comportamento, esses registros duplicados sao
consolidados na resposta, mantendo apenas uma ocorrencia para cada conjunto de
dados igual.

## `GET /api/funcionarios/{login}/perfis/{idPerfil}/turmas`

Retorna a abrangencia de turmas do funcionario no perfil informado, no formato
legado (hierarquia DRE -> UE -> turma em camelCase). Sem conteudo, responde 204.

Para o perfil de professor, a abrangencia e complementada com uma lista fixa de
cargos, porque o novo EOL nao devolve a abrangencia completa desse perfil. E o
unico ponto dessas rotas em que o gateway agrega conhecimento de dominio, e
segue candidato a migrar para o dominio de professores.

## `POST /api/funcionarios/turmas`

Recebe uma lista de codigos de UE e retorna a abrangencia de turmas dessas
unidades, agrupada em DRE -> UE -> turma no formato legado. Sem conteudo,
responde 204.

## `POST /api/funcionarios/BuscarTurmasElegiveis`

Recebe RF, turma e componente curricular no contrato legado e retorna as turmas
elegiveis para copia, cada uma com nome e codigo (`nomeTurma`, `codTurma`).
Quando nao ha turmas elegiveis, responde 204.

## `POST /api/funcionarios`

Recebe filtros de busca e retorna os funcionarios no contrato legado (`codigoRf`,
`nomeServidor`, `login`, `funcaoExterno`, etc.). Sem resultados, responde 404;
quando a fonte retorna vazio, responde 204.
