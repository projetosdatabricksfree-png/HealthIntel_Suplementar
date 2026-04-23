SHELL := /bin/bash
COMPOSE := docker compose -f infra/docker-compose.yml
DBT_ENV := DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target

.PHONY: up down logs ps compose-config api-dev layout-dev dbt-deps dbt-compile dbt-build dbt-test dbt-seed demo-data demo-data-regulatorio demo-data-idss demo-data-rede bootstrap-regulatorio-layouts bootstrap-rede-layouts billing-close lint sql-lint test ci-local smoke smoke-rede load-test airflow-setup dag-test dag-test-all seed-dados-completos

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

dbt-seed:
	cd healthintel_dbt && $(DBT_ENV) dbt seed

demo-data:
	python scripts/seed_demo_core.py
	python scripts/seed_demo_regulatorio.py
	python scripts/seed_demo_idss.py

demo-data-regulatorio:
	python scripts/seed_demo_regulatorio.py

demo-data-idss:
	python scripts/seed_demo_idss.py

demo-data-rede:
	python scripts/bootstrap_layout_registry_rede.py
	python scripts/seed_demo_rede.py

bootstrap-regulatorio-layouts:
	python scripts/bootstrap_layout_registry_regulatorio.py

bootstrap-rede-layouts:
	python scripts/bootstrap_layout_registry_rede.py

billing-close:
	python scripts/fechar_ciclo_billing.py --referencia $(REF)

lint:
	ruff check .

sql-lint:
	$(DBT_ENV) sqlfluff lint healthintel_dbt/models healthintel_dbt/tests

smoke:
	python scripts/smoke_piloto.py

smoke-rede:
	python scripts/smoke_rede.py

load-test:
	bash scripts/run_load_test.sh

ci-local: compose-config lint sql-lint test
	cd healthintel_dbt && $(DBT_ENV) dbt deps && $(DBT_ENV) dbt compile

test:
	pytest

airflow-setup:
	$(COMPOSE) exec airflow-scheduler airflow connections add postgres_default \
		--conn-type postgres --conn-host postgres --conn-login healthintel \
		--conn-password healthintel --conn-schema healthintel --conn-port 5432 || true
	$(COMPOSE) exec airflow-scheduler airflow connections add mongo_default \
		--conn-type mongo --conn-host mongo --conn-login healthintel \
		--conn-password healthintel --conn-schema healthintel_layout --conn-port 27017 || true

dag-test:
	@if [ -z "$(DAG)" ]; then echo "Usage: make dag-test DAG=dag_name"; exit 1; fi
	$(COMPOSE) exec airflow-scheduler airflow dags test $(DAG) 2026-04-22

seed-dados-completos:
	python scripts/seed_dados_completos.py

dag-test-all:
	@echo "=== dag_criar_particao_mensal ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_criar_particao_mensal 2026-04-22
	@echo "=== dag_registrar_versao ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_registrar_versao 2026-04-22
	@echo "=== dag_dbt_freshness ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_dbt_freshness 2026-04-22
	@echo "=== dag_anual_idss ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_anual_idss 2026-04-22
	@echo "=== dag_mestre_mensal ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_mestre_mensal 2026-04-22
	@echo "=== dag_ingest_diops ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_diops 2026-04-22
	@echo "=== dag_ingest_fip ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_fip 2026-04-22
	@echo "=== dag_ingest_glosa ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_glosa 2026-04-22
	@echo "=== dag_ingest_igr ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_igr 2026-04-22
	@echo "=== dag_ingest_nip ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_nip 2026-04-22
	@echo "=== dag_ingest_portabilidade ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_portabilidade 2026-04-22
	@echo "=== dag_ingest_prudencial ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_prudencial 2026-04-22
	@echo "=== dag_ingest_rede_assistencial ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_rede_assistencial 2026-04-22
	@echo "=== dag_ingest_regime_especial ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_regime_especial 2026-04-22
	@echo "=== dag_ingest_rn623 ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_rn623 2026-04-22
	@echo "=== dag_ingest_taxa_resolutividade ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_taxa_resolutividade 2026-04-22
	@echo "=== dag_ingest_vda ===" && $(COMPOSE) exec airflow-scheduler airflow dags test dag_ingest_vda 2026-04-22
