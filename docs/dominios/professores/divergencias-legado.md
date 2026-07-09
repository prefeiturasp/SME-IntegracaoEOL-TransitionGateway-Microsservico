# Divergencias entre contratos do legado e do novo EOL

Este documento registra diferenças identificadas entre o comportamento dos
contratos legados e as respostas retornadas pelo novo EOL.

## Turmas por escola e ano letivo

No novo EOL, registros equivalentes de turma e professor sao consolidados na
resposta.

No legado, a resposta podia trazer mais de uma ocorrencia para o mesmo conjunto
de dados. O novo comportamento preserva a informacao funcional e evita repeticao
sem significado para o consumidor.

## Abrangencia de turmas do funcionario

Os dados de abrangencia que o legado obtem da identidade ainda nao tem
integracao completa no novo fluxo. Enquanto essa dependencia externa nao estiver
disponivel, o gateway aceita informacoes auxiliares para exercer os mesmos
recortes de perfil.

Sem esses dados, o retorno nao representa todo o vinculo que o legado resolve
pela identidade.

## Abrangencia SME

Perfis com visao de rede dependem de uma massa ampla de turmas atribuidas. O
contrato funcional e mantido, mas o volume completo exige acompanhamento de
tempo de resposta antes da liberacao irrestrita.
