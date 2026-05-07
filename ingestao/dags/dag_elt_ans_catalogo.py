from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"
DBT_ENV = (
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)

with DAG(
    dag_id="dag_elt_ans_catalogo",
    start_date=datetime(2026, 1, 1),
    # 0 7 * * * UTC = 04:00 BRT diario (Core); historico via trigger manual com params.escopo
    # HARDGATE: habilitar na VPS somente apos §15.1 (NIP/IGR/IDSS) e §15.2 (layouts Mongo confirmados)
    schedule="0 7 * * *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
    params={
        "escopo": "sector_core",
        "familias": "",
        "limite": 100,
        "max_depth": 5,
    },
    tags=["healthintel", "ans", "elt", "catalogo"],
) as dag:
    discover_sources = BashOperator(
        task_id="discover_sources",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_discover_ans.py "
            "--escopo '{{ params.escopo }}' --max-depth '{{ params.max_depth }}'"
        ),
    )

    extract_sources = BashOperator(
        task_id="extract_sources",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_extract_ans.py "
            "--escopo '{{ params.escopo }}' "
            "--familias '{{ params.familias }}' "
            "--limite '{{ params.limite }}'"
        ),
    )

    load_sources = BashOperator(
        task_id="load_sources",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_load_ans.py "
            "--escopo '{{ params.escopo }}' "
            "--familias '{{ params.familias }}' "
            "--limite '{{ params.limite }}'"
        ),
    )

    dbt_run_staging_generico = BashOperator(
        task_id="dbt_run_staging_generico",
        cwd="/workspace/healthintel_dbt",
        bash_command=f"{DBT_ENV} dbt build --select staging.generico",
    )

    register_summary = BashOperator(
        task_id="register_summary",
        cwd="/workspace",
        bash_command=f"{PYTHON_ENV} python scripts/elt_status_ans.py",
    )

    (
        discover_sources
        >> extract_sources
        >> load_sources
        >> dbt_run_staging_generico
        >> register_summary
    )
