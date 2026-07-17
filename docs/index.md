# SME-IntegracaoEOL Transition Gateway

O Transition Gateway mantém a compatibilidade com os contratos legados da API
EOL e encaminha as chamadas para os microserviços de domínio correspondentes.

Ele atua como camada de transição: preserva caminhos, parâmetros e formatos
esperados pelos consumidores legados, enquanto traduz essas chamadas para os
serviços internos responsáveis por cada domínio.

O gateway não concentra regra de negócio. Sua responsabilidade principal é
rotear, adaptar contratos e padronizar aspectos transversais como autenticação,
observabilidade e propagação de contexto.

Esta documentação combina páginas técnicas mantidas pela equipe com docstrings
publicadas automaticamente pelo Sphinx.

```{toctree}
:maxdepth: 2
:caption: Páginas técnicas

dominios/professores/divergencias-legado
```

```{toctree}
:maxdepth: 2
:caption: Referência de código

api
```
