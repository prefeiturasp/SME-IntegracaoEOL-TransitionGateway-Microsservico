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

O Gateway expõe os contratos legados e os traduz para os microserviços de
domínio. Ele não contém regra de negócio nem lógica de resiliência: essas
responsabilidades pertencem ao sidecar de cada domínio.

Cada sidecar é um processo Django independente que aplica retry com backoff exponencial,
circuit breaker e propagação de contexto de rastreamento antes de encaminhar a requisição
ao microserviço correspondente. Os sidecars residem em repositórios próprios.

## Estrutura do repositório

```
.
├── apps/
│   ├── core/           # cliente HTTP, resiliência (lib dos sidecars), middleware
│   └── pedagogico/     # adaptação dos contratos do domínio pedagógico
│   └── professores/     # adaptação dos contratos do domínio professores
│   └── programasedu/   # adaptação dos contratos de programas educacionais
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

## Domínios Atendidos

### Pedagógico

Preserva contratos legados relacionados a componentes curriculares, turmas,
grade curricular, regência, planejamento e agrupamentos pedagógicos. A regra de
composição desses dados permanece no domínio pedagógico; o gateway adapta nomes,
formatos e parâmetros esperados pelos consumidores legados.

### Professores

Preserva contratos legados relacionados a professores, funcionários, vínculos
com unidades, cargos, perfis, supervisores e turmas atribuídas. Alguns fluxos
orquestram mais de um domínio para montar o contrato final, mantendo no gateway
apenas a adaptação entre formatos.

### Programas Educacionais

Preserva contratos legados relacionados a turmas e alunos de programas
educacionais. As decisões de elegibilidade e composição dos dados permanecem
nos microserviços responsáveis.

Para detalhes de rotas, parâmetros, métodos HTTP e exemplos de resposta,
consulte o Swagger da aplicação. Essa é a fonte mantida para o contrato
operacional da API.

## Requisitos

- Python 3.12+
- Docker e Docker Compose

## Instalação para desenvolvimento

Crie um ambiente virtual e instale as dependências locais:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
```

Instale os hooks do `pre-commit` antes de criar o primeiro commit:

```bash
pre-commit install
pre-commit run --all-files
```

O `pre-commit install` é obrigatório no setup local. Depois de instalado, os
formatadores e validadores são executados automaticamente em cada commit,
evitando o envio de código fora do padrão do projeto.

## Configuração do ambiente

```bash
cp .env.example .env
make build
make run
```

**Geral**

| Variável | Padrão | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | Chave secreta do Django |
| `DJANGO_DEBUG` | `1` | Ativa o modo debug (`0` em produção) |
| `DJANGO_ALLOWED_HOSTS` | `*` | Hosts permitidos, separados por vírgula |
| `API_KEY` | — | Chave usada para autenticar requisições de entrada |
| `API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação de entrada |
| `GATEWAY_TIMEOUT_SECONDS` | `10` | Timeout das chamadas do gateway aos sidecars |
| `PORT_WEB` | `8002` (dev) / `8000` (prod) | Porta exposta pelo container |

**Sidecars**

| Variável | Padrão | Descrição |
|---|---|---|
| `SIDECAR_PEDAGOGICO_URL` | `http://localhost:9004` | URL do sidecar pedagógico |
| `SIDECAR_PEDAGOGICO_API_KEY` | — | API Key enviada ao sidecar pedagógico |
| `SIDECAR_PEDAGOGICO_API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação para o sidecar pedagógico |
| `SIDECAR_PROFESSORES_URL` | `http://localhost:9005` | URL do sidecar professores |
| `SIDECAR_PROFESSORES_API_KEY` | — | API Key enviada ao sidecar professores |
| `SIDECAR_PROFESSORES_API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação para o sidecar professores |
| `SIDECAR_PROGRAMASEDU_URL` | `http://localhost:9006` | URL do sidecar de programas educacionais |
| `SIDECAR_PROGRAMASEDU_API_KEY` | — | API Key enviada ao sidecar de programas educacionais |
| `SIDECAR_PROGRAMASEDU_API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação para o sidecar de programas educacionais |

**Elastic APM**

| Variável | Padrão | Descrição |
|---|---|---|
| `ELASTIC_APM_SERVICE_NAME` | `transition-gateway` | Nome do serviço no APM |
| `ELASTIC_APM_SERVER_URL` | `http://localhost:8200` | URL do servidor APM |
| `ELASTIC_APM_SECRET_TOKEN` | — | Token de autenticação do APM |
| `ELASTIC_APM_ENVIRONMENT` | `local` | Ambiente (`local`, `staging`, `production`) |
| `ELASTIC_APM_ENABLED` | `1` | Ativa (`1`) ou desativa (`0`) o agente APM |

**RabbitMQ (logging)**

| Variável | Padrão | Descrição |
|---|---|---|
| `ENABLE_RABBITMQ_LOGGING` | `0` | Ativa (`1`) o envio de logs ao RabbitMQ |
| `RABBITMQ_HOST` | — | Host do RabbitMQ |
| `RABBITMQ_VIRTUAL_HOST` | `/` | Virtual host do RabbitMQ |
| `RABBITMQ_LOG_QUEUE` | — | Nome da fila de destino dos logs |
| `RABBITMQ_LOG_LEVEL` | `INFO` | Nível mínimo de log enviado ao RabbitMQ |
| `RABBITMQ_USERNAME` | — | Usuário do RabbitMQ |
| `RABBITMQ_PASSWORD` | — | Senha do RabbitMQ |

## Observabilidade

### Formato dos logs

Todos os logs são emitidos em JSON estruturado. Cada registro inclui os seguintes campos:

| Campo | Descrição |
|---|---|
| `timestamp` | Data e hora do evento |
| `level` | Nível do log (`INFO`, `WARNING`, `ERROR`) |
| `logger` | Nome do módulo que gerou o log |
| `message` | Mensagem descritiva da requisição atendida |
| `request_id` | UUID da requisição, propagado via header `X-Request-ID` |
| `service` | Nome do serviço (`transitiongateway`) |
| `transaction_id` | ID da transação APM (correlação com traces) |
| `trace_id` | ID do trace APM (correlação fim a fim) |

O middleware `LoggingContextMiddleware` emite um registro por requisição HTTP com método, path, status code e duração em milissegundos.

### Pipeline de logs

```
Aplicação
   │
   ├── stdout (sempre)
   │     JSON estruturado lido pelo runtime do container
   │
   └── RabbitMQ (quando ENABLE_RABBITMQ_LOGGING=1)
         │
         └── Consumer (Logstash)
               │
               └── Elasticsearch → Kibana (Logs)
```

Para ver logs no Kibana, `ENABLE_RABBITMQ_LOGGING` deve estar ativo e o consumer Logstash precisa estar configurado para ler da fila `RABBITMQ_LOG_QUEUE` e indexar no Elasticsearch.

### Rastreamento APM (Elastic APM)

O agente APM (`elasticapm.contrib.django`) instrumenta automaticamente cada requisição Django, criando transações e spans visíveis em **Kibana → Observability → APM**.

Os campos `transaction_id` e `trace_id` presentes em cada log permitem correlacionar um registro de log com a transação APM correspondente diretamente na interface do Kibana.

## Atalhos Make

Use `make help` para listar todos os comandos disponíveis. Os principais:

**Ambiente**

| Comando | Descrição |
|---|---|
| `make run` | Sobe o gateway em modo dev (porta 8002) |
| `make build` | Rebuild da imagem dev |
| `make stop` | Para e remove containers |

**Testes**

| Comando | Descrição |
|---|---|
| `make test` | Suite completa com cobertura ≥ 80% |
| `make test-core` | Apenas `apps.core` |
| `make test-pedagogico` | Apenas `apps.pedagogico` |
| `make test-professores` | Apenas `apps.professores` |
| `make test-institucional` | Apenas `apps.institucional` |

**Qualidade**

| Comando | Descrição |
|---|---|
| `make lint` | ruff + black + isort + mypy |
| `make coverage` | Relatório HTML em `docs/_cov/` |
| `make schema` | Gera schema OpenAPI em `schema.yml` |
| `make docs` | Gera documentação Sphinx em `docs/_build/html/` |

## Endpoints

Consulte o Swagger da aplicação para a lista completa de rotas com parâmetros e exemplos de resposta.
