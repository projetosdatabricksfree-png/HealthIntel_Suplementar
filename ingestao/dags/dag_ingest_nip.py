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
    dag_id="dag_ingest_nip",
    start_date=datetime(2026, 1, 1),
    schedule="0 5 16 */3 *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
    tags=["healthintel", "regulatorio", "nip", "core_ans"],
) as dag:
    extrair_nip = BashOperator(
        task_id="extrair_nip",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_extract_ans.py "
            "--escopo sector_core --familias nip --limite 10"
        ),
    )

    carregar_nip = BashOperator(
        task_id="carregar_nip",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_load_ans.py "
            "--escopo sector_core --familias nip --limite 10"
        ),
    )

    staging_nip = BashOperator(
        task_id="staging_nip",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build "
            "--select stg_nip_operadora_trimestral+ "
            "--exclude tag:tiss tag:premium tag:consumo_premium"
        ),
    )

    registrar_job = BashOperator(
        task_id="registrar_job",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python -c \""
            "import asyncio; from ingestao.app.carregar_postgres import SessionLocal; "
            "from sqlalchemy import text; "
            "async def _r(): "
            "  async with SessionLocal() as s: "
            "    await s.execute(text(\\\"INSERT INTO plataforma.job "
            "(dataset, status, tipo, iniciado_em, finalizado_em) "
            "VALUES ('nip', 'sucesso', 'ingestao_trimestral', now()-interval '1s', now())\\\"));"
            "    await s.commit(); "
            "asyncio.run(_r())\""
        ),
    )

    extrair_nip >> carregar_nip >> staging_nip >> registrar_job
