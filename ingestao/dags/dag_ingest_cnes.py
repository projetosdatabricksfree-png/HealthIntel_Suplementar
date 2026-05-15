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

_DBT_SELECTORS = "tag:cnes"

with DAG(
    dag_id="dag_ingest_cnes",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 15 * *",
    catchup=False,
    is_paused_upon_creation=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "retry_exponential_backoff": True,
    },
    params={
        "competencia": "",
    },
    tags=["healthintel", "cnes", "estabelecimento", "datasus"],
) as dag:
    bootstrap_layout_cnes = BashOperator(
        task_id="bootstrap_layout_cnes",
        cwd="/workspace",
        bash_command=f"{PYTHON_ENV} python scripts/bootstrap_layout_registry_cnes.py",
    )

    ingerir_cnes = BashOperator(
        task_id="ingerir_cnes",
        cwd="/workspace",
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
from ingestao.app.ingestao_real import executar_ingestao_cnes

competencia_conf = '{{{{ dag_run.conf.get("competencia", "") }}}}'
competencia = competencia_conf or '{{{{ ds_nodash[:6] }}}}'

resultado = asyncio.run(executar_ingestao_cnes(competencia))
print(resultado)
"
        """,
    )

    rebuild_serving_cnes = BashOperator(
        task_id="rebuild_serving_cnes",
        cwd="/workspace/healthintel_dbt",
        bash_command=f"{DBT_ENV} dbt build --select {_DBT_SELECTORS}",
    )

    bootstrap_layout_cnes >> ingerir_cnes >> rebuild_serving_cnes
