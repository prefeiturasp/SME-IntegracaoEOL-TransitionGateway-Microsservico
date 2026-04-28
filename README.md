# SME-IntegracaoEOL-TransitionGateway-Microsservico

Microsserviço que expõe endpoints compatíveis com o sistema legado EOL e repassa as requisições para os microsserviços de domínio via proxy sidecar.

## Requisitos

- Python 3.12+
- Docker e Docker Compose

## Configuração do ambiente

Copie o arquivo de exemplo e ajuste os valores:

```bash
cp .env.example .env
```

Variáveis obrigatórias:

| Variável | Descrição |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta do Django |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais do banco |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Localização do banco |
| `API_KEY` | Chave usada para autenticar requisições de entrada |
| `API_KEY_HEADER` | Nome do header que carrega a chave (padrão: `X-API-Key`) |
| `SIDECAR_INSTITUCIONAL_URL` | URL do sidecar do domínio institucional |
| `SIDECAR_PROFESSORES_URL` | URL do sidecar do domínio professores |
| `SIDECAR_ALUNOS_URL` | URL do sidecar do domínio alunos |
| `SIDECAR_PEDAGOGICO_URL` | URL do sidecar do domínio pedagógico |
| `SIDECAR_PROGRAMAS_URL` | URL do sidecar do domínio programas |

## Rodando em desenvolvimento

```bash
docker compose -f docker-compose-dev.yml up --build
```

O servidor sobe em `http://localhost:8000` com hot-reload e debugpy escutando na porta `5678`.

Para aplicar as migrations manualmente:

```bash
docker compose -f docker-compose-dev.yml exec web bash scripts/executar_migrations.sh
```

## Rodando em produção

```bash
docker compose up --build
```

## Endpoints

Todos os endpoints exigem autenticação via header `API_KEY_HEADER`, exceto os de health.

### Health

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/gateway/health/` | Agrega o status de todos os sidecars |
| GET | `/api/v1/institucional/health/` | Health do sidecar institucional |
| GET | `/api/v1/professores/health/` | Health do sidecar professores |
| GET | `/api/v1/alunos/health/` | Health do sidecar alunos |
| GET | `/api/v1/pedagogico/health/` | Health do sidecar pedagógico |
| GET | `/api/v1/programas/health/` | Health do sidecar programas |

### Proxy EOL

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/v1/eol/institucional/<path>` | Proxy para o sidecar institucional |
| GET/POST | `/api/v1/eol/professores/<path>` | Proxy para o sidecar professores |
| GET/POST | `/api/v1/eol/alunos/<path>` | Proxy para o sidecar alunos |
| GET/POST | `/api/v1/eol/pedagogico/<path>` | Proxy para o sidecar pedagógico |
| GET/POST | `/api/v1/eol/programas/<path>` | Proxy para o sidecar programas |

### Documentação

| Rota | Descrição |
|---|---|
| `/api/v1/docs/` | Swagger UI (sem autenticação) |
| `/api/v1/schema/` | OpenAPI schema (sem autenticação) |

## Arquitetura

O sistema legado EOL é consumido por outros sistemas via endpoints conhecidos. Para permitir a substituição gradual do EOL por microsserviços novos sem quebrar esses consumidores, o Transition Gateway entra como intermediário:

```
Consumidor  →  Transition Gateway  →  Microsserviço novo (sidecar)
```

O consumidor continua chamando os mesmos endpoints. O gateway recebe, repassa para o microsserviço novo responsável por aquele domínio, e devolve a resposta.

### O que é o "sidecar"

Sidecar é um projeto separado — um por domínio (institucional, professores, alunos, pedagógico, programas). O Transition Gateway conhece apenas o endereço de cada um via `SIDECAR_<DOMINIO>_URL`. O que roda nesse endereço é responsabilidade da equipe de cada domínio.

## Resiliência

O cliente HTTP base (`SidecarClient`) aplica por domínio:

- **Circuit breaker** — abre após `GATEWAY_CIRCUIT_BREAKER_FAIL_MAX` falhas consecutivas e fecha após `GATEWAY_CIRCUIT_BREAKER_RESET_TIMEOUT` segundos
- **Retry com backoff exponencial** — até `GATEWAY_RETRY_MAX_ATTEMPTS` tentativas
- **Timeout** — `GATEWAY_TIMEOUT_SECONDS` segundos por requisição

Cada domínio possui sua própria instância de `SidecarClient`, criada uma única vez no carregamento do módulo (`libs/gateway_client.py` de cada app). O estado do circuit breaker é acumulado entre requisições durante toda a vida do processo, garantindo que falhas de um domínio não afetem os demais.

## Estrutura

```
apps/
  core/
    api/serializers.py          # HealthStatusSerializer
    libs/gateway_client.py      # SidecarClient base
  controle_gateway/
    api/authentication.py       # ApiKeyAuthentication
    api/views.py                # GatewayHealthView
  institucional/
  professores/
  alunos/
  pedagogico/
  programas/
    (cada domínio: api/views.py, api/urls.py, libs/gateway_client.py, tests/)
config/
  settings.py
  urls.py
requirements/
  base.txt
  local.txt
```

## Desenvolvimento

```bash
# Lint e formatação
ruff check .
black .

# Type checking
mypy .

# Testes
pytest
```
