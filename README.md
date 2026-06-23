# SME-IntegracaoEOL-TransitionGateway-Microsservico

Gateway de transição entre os contratos legados do EOL e os novos microserviços de domínio.

## Arquitetura

```
Cliente externo
      │
      ▼
  Gateway (8000)        ← tradução de contrato e início do trace distribuído
      │
      ▼
sidecar_<domínio>       ← continua traceparent e aplica resiliência
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

| Módulo           | Responsabilidade                                        |
| ---------------- | ------------------------------------------------------- |
| `http_client.py` | `ServiceClient` baseado no cliente instrumentado do SDK |
| `apps.py`        | Inicialização do runtime do SDK no boot do Django       |

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

| Variável               | Padrão                       | Descrição                                          |
| ---------------------- | ---------------------------- | -------------------------------------------------- |
| `DJANGO_SECRET_KEY`    | —                            | Chave secreta do Django                            |
| `DJANGO_DEBUG`         | `1`                          | Ativa o modo debug (`0` em produção)               |
| `DJANGO_ALLOWED_HOSTS` | `*`                          | Hosts permitidos, separados por vírgula            |
| `API_KEY`              | —                            | Chave usada para autenticar requisições de entrada |
| `API_KEY_HEADER`       | `X-API-Key`                  | Nome do header de autenticação de entrada          |
| `PORT_WEB`             | `8002` (dev) / `8000` (prod) | Porta exposta pelo container                       |

**Sidecars**

| Variável                              | Padrão                  | Descrição                                                               |
| ------------------------------------- | ----------------------- | ----------------------------------------------------------------------- |
| `SIDECAR_PEDAGOGICO_URL`              | `http://localhost:9004` | URL do sidecar pedagógico                                               |
| `SIDECAR_PEDAGOGICO_API_KEY`          | —                       | API Key enviada ao sidecar pedagógico                                   |
| `SIDECAR_PEDAGOGICO_API_KEY_HEADER`   | `X-API-Key`             | Nome do header de autenticação para o sidecar pedagógico                |
| `SIDECAR_PROFESSORES_URL`             | `http://localhost:9005` | URL do sidecar professores                                              |
| `SIDECAR_PROFESSORES_API_KEY`         | —                       | API Key enviada ao sidecar professores                                  |
| `SIDECAR_PROFESSORES_API_KEY_HEADER`  | `X-API-Key`             | Nome do header de autenticação para o sidecar professores               |
| `SIDECAR_PROGRAMASEDU_URL`            | `http://localhost:9006` | URL do sidecar de programas educacionais                                |
| `SIDECAR_PROGRAMASEDU_API_KEY`        | —                       | API Key enviada ao sidecar de programas educacionais                    |
| `SIDECAR_PROGRAMASEDU_API_KEY_HEADER` | `X-API-Key`             | Nome do header de autenticação para o sidecar de programas educacionais |

**SME Sidecar SDK**

| Variável                          | Padrão                  | Descrição                                       |
| --------------------------------- | ----------------------- | ----------------------------------------------- |
| `SME_SERVICE_NAME`                | `transition-gateway`    | Nome do serviço nos logs e traces               |
| `SME_SERVICE_VERSION`             | `unknown`               | Versão publicada na telemetria                  |
| `SME_ENVIRONMENT`                 | `dev`                   | Ambiente de execução                            |
| `SME_TIMEOUT_SECONDS`             | `10`                    | Timeout das chamadas aos sidecars               |
| `SME_LOG_LEVEL`                   | `ERROR`                 | Nível mínimo dos logs                           |
| `SME_LOG_FORMAT`                  | `json`                  | Formato `json` ou `console`                     |
| `SME_CORRELATION_ID_HEADER`       | `X-Request-ID`          | Header de correlação                            |
| `SME_OTEL_ENABLED`                | `false`                 | Ativa tracing OpenTelemetry                     |
| `SME_OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | URL OTLP gRPC configurada diretamente no `.env` |
| `SME_OTEL_EXPORTER_OTLP_HEADERS`  | —                       | Headers do exporter em `chave=valor`            |
| `SME_OTEL_EXPORTER_OTLP_INSECURE` | `true`                  | Desabilita TLS no transporte OTLP               |
| `SME_RABBITMQ_URL`                | —                       | URL AMQP para transporte opcional de logs       |
| `SME_LOG_RABBITMQ_QUEUE`          | —                       | Fila RabbitMQ de logs                           |

## Observabilidade

### Formato dos logs

Todos os logs são emitidos em JSON estruturado. Cada registro inclui os seguintes campos:

| Campo        | Descrição                                                  |
| ------------ | ---------------------------------------------------------- |
| `timestamp`  | Data e hora do evento                                      |
| `level`      | Nível do log (`INFO`, `WARNING`, `ERROR`)                  |
| `logger`     | Nome do módulo que gerou o log                             |
| `message`    | Mensagem descritiva da requisição atendida                 |
| `event`      | Nome do evento estruturado (ex.: `http_request_completed`) |
| `request_id` | UUID da requisição, propagado via header `X-Request-ID`    |
| `service`    | Nome do serviço (`transitiongateway`)                      |
| `span_id`    | ID da operação atual                                       |
| `trace_id`   | ID do trace distribuído fim a fim                          |

O `ObservabilityMiddleware` do SDK emite um evento por requisição HTTP
com método, path, status code e duração em milissegundos.

### Pipeline de logs

```
Aplicação
   │
   ├── stdout (sempre)
   │     JSON estruturado lido pelo runtime do container
   │
   └── RabbitMQ (quando SME_LOG_RABBITMQ_QUEUE está configurada)
         │
         └── Consumer (Logstash)
               │
               └── Elasticsearch → Kibana (Logs)
```

Para ver logs no Kibana via RabbitMQ, configure `SME_RABBITMQ_URL` e
`SME_LOG_RABBITMQ_QUEUE`. O consumer Logstash deve ler essa fila e
indexar os eventos no Elasticsearch.

### Rastreamento distribuído

O SME Sidecar SDK cria um span `django.request` na entrada do gateway e
instrumenta o cliente HTTPX. As chamadas aos sidecars recebem
automaticamente `traceparent`, preservando um único trace desde o gateway
até os serviços de domínio. Os spans são enviados por OTLP ao Elastic APM
ou a um OpenTelemetry Collector.

Os campos `trace_id` e `span_id` presentes em cada log permitem abrir o
trace correspondente diretamente na interface de observabilidade.

## Atalhos Make

Use `make help` para listar todos os comandos disponíveis. Os principais:

**Ambiente**

| Comando      | Descrição                               |
| ------------ | --------------------------------------- |
| `make run`   | Sobe o gateway em modo dev (porta 8002) |
| `make build` | Rebuild da imagem dev                   |
| `make stop`  | Para e remove containers                |

**Testes**

| Comando                   | Descrição                          |
| ------------------------- | ---------------------------------- |
| `make test`               | Suite completa com cobertura ≥ 80% |
| `make test-core`          | Apenas `apps.core`                 |
| `make test-pedagogico`    | Apenas `apps.pedagogico`           |
| `make test-professores`   | Apenas `apps.professores`          |
| `make test-institucional` | Apenas `apps.institucional`        |

**Qualidade**

| Comando         | Descrição                                       |
| --------------- | ----------------------------------------------- |
| `make lint`     | ruff + black + isort + mypy                     |
| `make coverage` | Relatório HTML em `docs/_cov/`                  |
| `make schema`   | Gera schema OpenAPI em `schema.yml`             |
| `make docs`     | Gera documentação Sphinx em `docs/_build/html/` |

## Endpoints

Consulte o Swagger da aplicação para a lista completa de rotas com parâmetros e exemplos de resposta.
