# SME-IntegracaoEOL-TransitionGateway-Microsservico

Gateway de transição entre os contratos legados do EOL e os novos microserviços de domínio.

## Arquitetura

```
Cliente externo
      │
      ▼
  Gateway (8000)        ← tradução de contrato legado → novo, sem regra de negócio
      │
      ▼
sidecar_<domínio>       ← retry, circuit breaker, propagação de X-Request-ID
      │
      ▼
MS de domínio           ← microserviço proprietário do domínio
```

O Gateway expõe os contratos legados (L1–L17) e os mapeia para os endpoints canônicos
dos microserviços de domínio. Ele não contém regra de negócio nem lógica de resiliência:
essas responsabilidades pertencem ao sidecar de cada domínio.

Cada sidecar é um processo Django independente que aplica retry com backoff exponencial,
circuit breaker e propagação de contexto de rastreamento antes de encaminhar a requisição
ao microserviço correspondente. Os sidecars residem em repositórios próprios.

## Estrutura do repositório

```
.
├── apps/
│   ├── core/           # cliente HTTP, resiliência (lib dos sidecars), middleware
│   └── pedagogico/     # domínio pedagógico: views, services, serializers
├── config/             # settings, urls, wsgi e autenticação do gateway
├── requirements/
│   ├── base.txt        # dependências de produção
│   └── local.txt       # base + ferramentas de desenvolvimento
└── manage.py
```

### apps/core

| Módulo | Responsabilidade |
|---|---|
| `http_client.py` | `ServiceClient` — cliente HTTP simples com timeout (usado pelo gateway) |
| `middleware.py` | Propagação de `X-Request-ID` e contexto de logging |
| `logging_context.py` | `ContextVar` para request ID e serviço |

## Domínio pedagógico

O gateway mapeia 17 rotas legadas para 15 endpoints canônicos do MS Pedagógico:

| Legado | Endpoint canônico |
|---|---|
| L1 Componentes do funcionário por turma com agrupamento | EP-1 `GET /funcionarios/{login}` |
| L2 Componentes do funcionário sem filtro de turma | EP-1 `GET /funcionarios/{login}` |
| L3 Componentes com planejamento de regência | EP-1 `GET /funcionarios/{login}?planejamento=true` |
| L4 Componentes de regência por ano de turma | EP-2 `GET /anos/{anoTurma}/regencia` |
| L5 Verificar componente PAP em turma | EP-3 `GET /turmas/{cod}/pap` |
| L6 Componentes por UE, modalidade, ano e anos escolares | EP-4 `GET /ues/{id}/modalidades/{mod}/anos/{ano}` |
| L7 Componentes de turmas programa por UE e modalidade | EP-5 `GET /ues/{id}/modalidades/{mod}/anos/{ano}/turmas-programa` |
| L8 Componentes por lista de turmas e UE | EP-6 `GET /ues/{id}/turmas` |
| L9 Componentes para planejamento por lista de turmas | EP-7 `GET /turmas` |
| L10 Componentes de turmas sem pós-processamento | EP-8 `GET /turmas/brutos` |
| L11 Catálogo de componentes curriculares | EP-9 `GET /` |
| L12 Dados de aula por turma (vigência de componentes) | EP-10 `GET /turmas/vigencia` |
| L13 Agrupamentos correlacionados de Território do Saber | EP-13 `GET /{cod}/territorio-saber/agrupamentos-correlacionados` |
| L14 Agrupamentos correlacionados em lote | EP-14 `POST /territorio-saber/agrupamentos-correlacionados` |
| L15 Agrupamentos de Território do Saber por IDs | EP-15 `POST /territorio-saber/agrupamentos` |
| L16 Grade curricular por ano letivo | EP-11 `GET /grade-curricular/{anoLetivo}` |
| L17 Componentes sem atribuição em uma turma | EP-12 `GET /turmas/{cod}/sem-atribuicao` |

## Requisitos

- Python 3.12+
- Docker e Docker Compose

## Configuração do ambiente

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | Chave secreta do Django |
| `API_KEY` | — | Chave usada para autenticar requisições de entrada |
| `API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação |
| `SIDECAR_PEDAGOGICO_URL` | `http://localhost:9004` | URL do sidecar pedagógico |
| `GATEWAY_TIMEOUT_SECONDS` | `10` | Timeout das chamadas do gateway aos sidecars |

## Execução local

```bash
docker compose -f docker-compose-dev.yml up --build
```

Sobe o `gateway` na porta `8000`. O sidecar de cada domínio deve ser iniciado
a partir do seu próprio repositório e conectado via rede Docker compartilhada.

## Testes

```bash
docker compose -f docker-compose-dev.yml run --rm gateway \
  python -m coverage run manage.py test --no-input --settings=config.settings
```

Para ver o relatório de cobertura após a execução:

```bash
docker compose -f docker-compose-dev.yml run --rm gateway \
  python -m coverage report
```

## Endpoints

Consulte o Swagger em `/api/v1/docs/` para a lista completa de rotas com parâmetros e exemplos de resposta.