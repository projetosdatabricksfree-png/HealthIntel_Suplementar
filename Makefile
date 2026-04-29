SHELL := /bin/bash
COMPOSE := docker compose -f infra/docker-compose.yml
COMPOSE_HML := docker compose --env-file .env.hml -f infra/docker-compose.yml -f infra/docker-compose.hml.yml
DBT_ENV := DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target
DBT_BIN := ../.venv/bin/dbt
SQLFLUFF_BIN := ../.venv/bin/sqlfluff
RUFF_BIN ?= .venv/bin/ruff

.PHONY: up down logs ps compose-config compose-config-hml up-hml down-hml api-dev layout-dev dbt-deps dbt-compile dbt-build dbt-test dbt-build-premium dbt-test-premium dbt-seed demo-data demo-data-regulatorio demo-data-idss demo-data-rede demo-data-cnes demo-data-tiss demo-data-sib demo-data-cadop bootstrap-regulatorio-layouts bootstrap-rede-layouts bootstrap-cnes-layouts bootstrap-tiss-layouts bootstrap-sib-layouts bootstrap-cadop-layouts billing-close lint sql-lint test ci-local smoke smoke-rede smoke-cnes smoke-tiss smoke-prata smoke-premium smoke-sib smoke-janela-carga-sib smoke-versao-vigente-tuss smoke-historico-sob-demanda smoke-cadop smoke-pgbackrest smoke-consumo consumo-refresh elt-discover elt-extract elt-load elt-all elt-status elt-transform-all elt-validate-all load-test airflow-setup dag-test dag-test-all seed-dados-completos dbt-seed-ref hardgate-sem-ano-hardcoded-janelacarga

PYTHON ?= .venv/bin/python
PYTEST_BIN := .venv/bin/pytest
ELT_ESCOPO ?= sector_core
ELT_FAMILIAS ?=
ELT_LIMITE ?= 100
ELT_MAX_DEPTH ?= 5

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

compose-config-hml:
	$(COMPOSE_HML) config > /tmp/healthintel-compose-hml.rendered.yml

up-hml:
	$(COMPOSE_HML) up -d --build

down-hml:
	$(COMPOSE_HML) down

api-dev:
	uvicorn api.app.main:app --reload --host 0.0.0.0 --port 8000

layout-dev:
	uvicorn mongo_layout_service.app.main:app --reload --host 0.0.0.0 --port 8001

dbt-deps:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) deps

dbt-compile:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) compile

dbt-build:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) build

dbt-test:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) test

dbt-build-premium:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) build --select tag:quality tag:mdm tag:mdm_privado tag:consumo_premium tag:premium

dbt-test-premium:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) test --select tag:quality tag:mdm tag:mdm_privado tag:consumo_premium tag:premium

dbt-seed:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) seed

demo-data:
	$(PYTHON) scripts/seed_demo_core.py
	$(PYTHON) scripts/seed_demo_regulatorio.py
	$(PYTHON) scripts/seed_demo_idss.py

demo-data-regulatorio:
	$(PYTHON) scripts/seed_demo_regulatorio.py

demo-data-idss:
	$(PYTHON) scripts/seed_demo_idss.py

demo-data-rede:
	$(PYTHON) scripts/bootstrap_layout_registry_rede.py
	$(PYTHON) scripts/seed_demo_rede.py

demo-data-cnes:
	$(PYTHON) scripts/bootstrap_layout_registry_cnes.py
	$(PYTHON) scripts/seed_demo_cnes.py

demo-data-tiss:
	$(PYTHON) scripts/bootstrap_layout_registry_tiss.py
	$(PYTHON) scripts/seed_demo_tiss.py

demo-data-sib:
	$(PYTHON) scripts/seed_demo_sib.py

demo-data-cadop:
	$(PYTHON) scripts/seed_demo_cadop.py

bootstrap-regulatorio-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_regulatorio.py

bootstrap-rede-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_rede.py

bootstrap-cnes-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_cnes.py

bootstrap-tiss-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_tiss.py

bootstrap-sib-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_sib.py

bootstrap-cadop-layouts:
	$(PYTHON) scripts/bootstrap_layout_registry_cadop.py

billing-close:
	$(PYTHON) scripts/fechar_ciclo_billing.py --referencia $(REF)

lint:
	$(RUFF_BIN) check .

sql-lint:
	cd healthintel_dbt && $(DBT_ENV) $(SQLFLUFF_BIN) lint models tests

smoke:
	$(PYTHON) scripts/smoke_piloto.py

smoke-rede:
	$(PYTHON) scripts/smoke_rede.py

smoke-cnes:
	$(PYTHON) scripts/seed_demo_cnes.py
	$(PYTHON) scripts/smoke_cnes.py

smoke-tiss:
	$(PYTHON) scripts/seed_demo_rede.py
	$(PYTHON) scripts/seed_demo_tiss.py
	$(PYTHON) scripts/smoke_tiss.py

smoke-prata:
	$(PYTHON) scripts/smoke_prata.py

smoke-premium:
	$(PYTHON) scripts/smoke_premium.py

smoke-sib:
	$(PYTHON) scripts/smoke_sib.py

smoke-janela-carga-sib:
	$(PYTHON) scripts/smoke_janela_carga_sib.py

smoke-versao-vigente-tuss:
	$(PYTHON) scripts/smoke_versao_vigente_tuss.py

smoke-historico-sob-demanda:
	$(PYTHON) scripts/smoke_historico_sob_demanda.py

smoke-cadop:
	$(PYTHON) scripts/smoke_cadop.py

smoke-pgbackrest:
	bash scripts/backup/smoke_pgbackrest.sh

consumo-refresh:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) run --select tag:mart tag:consumo
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) test --select tag:consumo

smoke-consumo:
	$(PYTHON) scripts/smoke_consumo.py

elt-discover:
	PYTHONPATH=$(PWD) $(PYTHON) scripts/elt_discover_ans.py --escopo $(ELT_ESCOPO) --max-depth $(ELT_MAX_DEPTH)

elt-extract:
	PYTHONPATH=$(PWD) $(PYTHON) scripts/elt_extract_ans.py --escopo $(ELT_ESCOPO) --familias "$(ELT_FAMILIAS)" --limite $(ELT_LIMITE)

elt-load:
	PYTHONPATH=$(PWD) $(PYTHON) scripts/elt_load_ans.py --escopo $(ELT_ESCOPO) --familias "$(ELT_FAMILIAS)" --limite $(ELT_LIMITE)

elt-all:
	PYTHONPATH=$(PWD) $(PYTHON) scripts/elt_all_ans.py --escopo $(ELT_ESCOPO) --familias "$(ELT_FAMILIAS)" --limite $(ELT_LIMITE) --max-depth $(ELT_MAX_DEPTH)

elt-status:
	PYTHONPATH=$(PWD) $(PYTHON) scripts/elt_status_ans.py

elt-transform-all:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) build --select tag:staging tag:prata tag:mart tag:consumo

elt-validate-all:
	$(RUFF_BIN) check ingestao scripts healthintel_dbt
	$(PYTEST_BIN) ingestao/tests/test_elt_discovery.py -v
	$(PYTEST_BIN) ingestao/tests/test_elt_catalogo.py -v
	$(PYTEST_BIN) ingestao/tests/test_elt_loaders.py -v
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) compile --select tag:staging

load-test:
	bash scripts/run_load_test.sh

ci-local: compose-config lint sql-lint test
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) deps && $(DBT_ENV) $(DBT_BIN) compile

test:
	$(PYTEST_BIN)

airflow-setup:
	$(COMPOSE) exec airflow-scheduler airflow connections add postgres_default \
		--conn-type postgres --conn-host postgres --conn-login healthintel \
		--conn-password healthintel --conn-schema healthintel --conn-port 5432 || true
	$(COMPOSE) exec airflow-scheduler airflow connections add mongo_default \
		--conn-type mongo --conn-host mongo --conn-login healthintel \
		--conn-password healthintel --conn-schema healthintel_layout --conn-port 27017 || true
	$(COMPOSE) exec airflow-scheduler airflow variables set ANS_ANOS_CARGA_HOT 2 || true

dag-test:
	@if [ -z "$(DAG)" ]; then echo "Usage: make dag-test DAG=dag_name"; exit 1; fi
	$(COMPOSE) exec airflow-scheduler airflow dags test $(DAG) 2026-04-22

seed-dados-completos:
	$(PYTHON) scripts/seed_dados_completos.py

dbt-seed-ref:
	cd healthintel_dbt && $(DBT_ENV) $(DBT_BIN) seed --select ref_tuss ref_rol_procedimento

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

dag-parse:
	$(COMPOSE) exec airflow-scheduler python -c 'from airflow.models import DagBag; d = DagBag(); print("Errors:", d.import_errors)'

dag-run-real-cadop:
	$(PYTHON) scripts/run_ingestao_real_cadop.py

dag-run-real-sib:
	$(PYTHON) scripts/run_ingestao_real_sib.py "$(UFS)" "$(COMPETENCIA)"

smoke-ingestao-real:
	$(PYTHON) scripts/smoke_ingestao_real.py

hardgate-sem-ano-hardcoded-janelacarga:
	bash tests/hardgates/assert_sem_ano_hardcoded_janela.sh
