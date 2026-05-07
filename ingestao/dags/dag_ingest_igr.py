from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"
DBT_ENV = (
    "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace "
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)
DBT_BIN = "python -m dbt.cli.main"
DBT_EXCLUDE = "tag:tiss tag:premium tag:consumo_premium assert_mdm_operadora_cobertura_minima"
DBT_SELECT = (
    "stg_igr api_bronze_igr api_prata_igr "
    "stg_rn623_lista int_regulatorio_operadora_trimestre "
    "fat_monitoramento_regulatorio_trimestral api_regulatorio_operadora_trimestral"
)


def registrar_job_command(dag_id: str, dataset: str, tipo: str) -> str:
    return f"""{PYTHON_ENV} python - <<'PY'
import asyncio
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def registrar() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                "INSERT INTO plataforma.job "
                "(id, dag_id, nome_job, fonte_ans, status, iniciado_em, finalizado_em, "
                "registro_processado, registro_com_falha, camada) "
                "VALUES (:id, :dag_id, :nome_job, :fonte_ans, 'sucesso', "
                "now() - interval '1 second', now(), 0, 0, :camada)"
            ),
            {{
                "id": str(uuid4()),
                "dag_id": "{dag_id}",
                "nome_job": "{tipo}",
                "fonte_ans": "{dataset}",
                "camada": "airflow",
            }},
        )
        await session.commit()


asyncio.run(registrar())
PY"""

with DAG(
    dag_id="dag_ingest_igr",
    start_date=datetime(2026, 1, 1),
    schedule="0 5 15 */3 *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
    tags=["healthintel", "regulatorio", "igr", "core_ans"],
) as dag:
    extrair_igr = BashOperator(
        task_id="extrair_igr",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_extract_ans.py "
            "--escopo sector_core --familias igr --limite 10"
        ),
    )

    carregar_igr = BashOperator(
        task_id="carregar_igr",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/elt_load_ans.py "
            "--escopo sector_core --familias igr --limite 10"
        ),
    )

    materializar_igr_tipado = BashOperator(
        task_id="materializar_igr_tipado",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/materializar_regulatorio_generico.py "
            "--datasets igr"
        ),
    )

    staging_igr = BashOperator(
        task_id="staging_igr",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} {DBT_BIN} build "
            f"--select {DBT_SELECT} "
            f"--exclude {DBT_EXCLUDE}"
        ),
    )

    registrar_job = BashOperator(
        task_id="registrar_job",
        cwd="/workspace",
        bash_command=registrar_job_command(
            "dag_ingest_igr",
            "igr",
            "ingestao_trimestral_igr",
        ),
    )

    extrair_igr >> carregar_igr >> materializar_igr_tipado >> staging_igr >> registrar_job
