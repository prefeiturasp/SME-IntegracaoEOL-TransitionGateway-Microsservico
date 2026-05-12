COMPOSE      = docker compose -f docker-compose-dev.yml
EXEC         = $(COMPOSE) exec gateway
RUN          = $(COMPOSE) run --rm gateway
PYTEST_ARGS ?= --cov=apps --cov-report=term-missing --cov-fail-under=80

.PHONY: run build stop \
        test test-core test-pedagogico test-professores test-institucional \
        lint coverage schema help

help:
	@echo "Targets disponíveis:"
	@echo ""
	@echo "  Ambiente:"
	@echo "    make run              — sobe o gateway em modo dev (porta 8002)"
	@echo "    make build            — rebuild da imagem dev"
	@echo "    make stop             — para e remove containers"
	@echo ""
	@echo "  Testes (suite completa):"
	@echo "    make test             — todos os apps com cobertura ≥80%"
	@echo ""
	@echo "  Testes por app:"
	@echo "    make test-core        — apenas apps.core"
	@echo "    make test-pedagogico  — apenas apps.pedagogico"
	@echo "    make test-professores — apenas apps.professores"
	@echo "    make test-institucional — apenas apps.institucional"
	@echo ""
	@echo "  Qualidade:"
	@echo "    make lint             — ruff + black + isort + mypy"
	@echo "    make coverage         — relatório HTML em docs/_cov/"
	@echo "    make schema           — gera schema OpenAPI em schema.yml"

# ---------------------------------------------------------------------------
# Ambiente
# ---------------------------------------------------------------------------

run:
	$(COMPOSE) up

build:
	$(COMPOSE) up --build

stop:
	$(COMPOSE) down

# ---------------------------------------------------------------------------
# Testes — suite completa
# ---------------------------------------------------------------------------

test:
	$(RUN) python -m pytest $(PYTEST_ARGS) -v

# ---------------------------------------------------------------------------
# Testes por app — sem cálculo de cobertura global, foco no app isolado
# ---------------------------------------------------------------------------

test-core:
	$(RUN) python -m pytest apps/core/tests/ \
		--cov=apps.core --cov-report=term-missing -v

test-pedagogico:
	$(RUN) python -m pytest apps/pedagogico/tests/ \
		--cov=apps.pedagogico --cov-report=term-missing -v

test-professores:
	$(RUN) python -m pytest apps/professores/tests/ \
		--cov=apps.professores --cov-report=term-missing -v

test-institucional:
	$(RUN) python -m pytest apps/institucional/tests/ \
		--cov=apps.institucional --cov-report=term-missing -v

# ---------------------------------------------------------------------------
# Qualidade
# ---------------------------------------------------------------------------

lint:
	$(EXEC) bash -c "\
		ruff check . && \
		black --check . && \
		isort --check-only . && \
		mypy apps config"

coverage:
	$(RUN) python -m pytest $(PYTEST_ARGS) \
		--cov-report=html:docs/_cov
	@echo "Relatório gerado em docs/_cov/index.html"

schema:
	$(EXEC) python manage.py spectacular --file schema.yml
	@echo "Schema gerado em schema.yml"
