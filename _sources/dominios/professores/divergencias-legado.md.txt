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

## Abrangencia

Os dados de abrangencia que o legado obtem da identidade ainda nao tem
integracao completa no novo fluxo. Enquanto essa dependencia externa nao estiver
disponivel, o gateway aceita informacoes auxiliares para exercer os mesmos
recortes de perfil.

Sem esses dados, o retorno nao representa todo o vinculo que o legado resolve
pela identidade.

## Professores por escola e ano

Em algumas escolas, a origem pode conter mais de uma atribuicao ativa para a
mesma turma e componente. O legado nao define um desempate completo entre essas
atribuicoes antes de montar o retorno e, por isso, a escolha observada pode
depender do cache ou da execucao da consulta.

O novo EOL consome uma visao materializada que estabiliza essa escolha. Assim,
as quantidades tendem a permanecer alinhadas, mas pode haver divergencia de RF
em cenarios de empate na origem.
