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
│   └── professores/     # domínio professores: views, services, serializers
│   └── programasedu/   # domínio programas educacionais: views, services, serializers
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


## Domínio professores

O gateway mapeia 4 rotas legadas cobertas pelo MS-Professores:

| Legado | Endpoint canônico |
|---|---|
| L1 Retorna booleano indicando se o funcionário está ativo | EP-1 `GET /acessos/funcionario-ativo/{registro_funcional}/` |
| L2 Retorna nome e CPF do servidor | EP-2 `GET /funcionarios/nome-servidor/{registro_funcional}/` |
| L3 Retorna booleano indicando se o professor é válido | EP-3 `GET /professores/{codigo_rf}/validade/` |
| L4 Retorna o nome do professor correspondente ao RF informado | EP-4 `GET /professores/{rf_professor}/` |

## Domínio programas educacionais

O gateway mapeia 4 rotas legadas para os endpoints canônicos EP-02 a EP-05 do MS-ProgramasEdu. Os paths legados replicam o contrato do `AlunoController` do `SME-Pedagogico-API`, sob o prefixo `/api/alunos/`.

| Legado | Endpoint canônico |
|---|---|
| L1 Turmas PAP por ano letivo e UE | EP-02 `GET /alunos/turmas-pap/{anoLetivo}/ues/{codigoEscola}` |
| L2 Verificar quais alunos pertencem a turmas PAP | EP-03 `GET /alunos/alunos-pap/{anoLetivo}` |
| L3 Alunos PAP do ano corrente | EP-04 `GET /alunos/pap/ano-corrente` |
| L4 Alunos PAP por ano letivo | EP-05 `GET /alunos/pap/ano-letivo/{anoLetivo}` |

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
| `message` | Mensagem descritiva (ex.: `GET /api/v1/... 200 43ms`) |
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

Consulte o Swagger em `/api/v1/docs/` para a lista completa de rotas com parâmetros e exemplos de resposta.
