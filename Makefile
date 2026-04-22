SHELL := /bin/bash
COMPOSE := docker compose -f infra/docker-compose.yml
DBT_ENV := DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target

.PHONY: up down logs ps compose-config api-dev layout-dev dbt-deps dbt-compile dbt-build dbt-test demo-data demo-data-regulatorio bootstrap-regulatorio-layouts billing-close lint sql-lint test ci-local smoke load-test

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

compose-config:
	$(COMPOSE) config > /tmp/healthintel-compose.rendered.yml

api-dev:
	uvicorn api.app.main:app --reload --host 0.0.0.0 --port 8000

layout-dev:
	uvicorn mongo_layout_service.app.main:app --reload --host 0.0.0.0 --port 8001

dbt-deps:
	cd healthintel_dbt && $(DBT_ENV) dbt deps

dbt-compile:
	cd healthintel_dbt && $(DBT_ENV) dbt compile

dbt-build:
	cd healthintel_dbt && $(DBT_ENV) dbt build

dbt-test:
	cd healthintel_dbt && $(DBT_ENV) dbt test

demo-data:
	python scripts/seed_demo_core.py
	python scripts/seed_demo_regulatorio.py

demo-data-regulatorio:
	python scripts/seed_demo_regulatorio.py

bootstrap-regulatorio-layouts:
	python scripts/bootstrap_layout_registry_regulatorio.py

billing-close:
	python scripts/fechar_ciclo_billing.py --referencia $(REF)

lint:
	ruff check .

sql-lint:
	$(DBT_ENV) sqlfluff lint healthintel_dbt/models healthintel_dbt/tests

smoke:
	python scripts/smoke_piloto.py

load-test:
	bash scripts/run_load_test.sh

ci-local: compose-config lint sql-lint test
	cd healthintel_dbt && $(DBT_ENV) dbt deps && $(DBT_ENV) dbt compile

test:
	pytest
