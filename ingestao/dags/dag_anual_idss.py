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

# Modelos dependentes do IDSS para recalculo do score regulatorio
_DBT_RECALCULO = (
    "+fat_score_regulatorio_mensal "
    "+api_score_operadora_mensal "
    "+api_ranking_score"
)
_DBT_EXCLUDE = "tag:tiss tag:premium tag:consumo_premium"

with DAG(
    dag_id="dag_anual_idss",
    start_date=datetime(2026, 1, 1),
    # Anual: primeiro dia util de marco (IDSS publicado pela ANS em fevereiro/marco)
    schedule="0 6 1 3 *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=15),
    },
    params={
        "ano_referencia": "",
    },
    tags=["healthintel", "idss", "anual", "core_ans"],
) as dag:
    extrair_idss = BashOperator(
        task_id="extrair_idss",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_extract_ans.py "
            "--escopo sector_core --familias idss --limite 10"
        ),
    )

    carregar_idss = BashOperator(
        task_id="carregar_idss",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_load_ans.py "
            "--escopo sector_core --familias idss --limite 10"
        ),
    )

    staging_idss = BashOperator(
        task_id="staging_idss",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build "
            "--select stg_idss_operadora+ int_idss_enriquecido "
            f"--exclude {_DBT_EXCLUDE}"
        ),
    )

    recalculo_score = BashOperator(
        task_id="recalculo_score_regulatorio",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build "
            f"--select {_DBT_RECALCULO} "
            f"--exclude {_DBT_EXCLUDE}"
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
            "VALUES ('idss', 'sucesso', 'ingestao_anual', now()-interval '1s', now())\\\"));"
            "    await s.commit(); "
            "asyncio.run(_r())\""
        ),
    )

    (
        extrair_idss
        >> carregar_idss
        >> staging_idss
        >> recalculo_score
        >> registrar_job
    )
