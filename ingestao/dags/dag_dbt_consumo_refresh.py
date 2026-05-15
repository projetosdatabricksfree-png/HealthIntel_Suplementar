from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_ENV = (
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)
REGISTRAR_REFRESH = r"""
PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from uuid import uuid4
from sqlalchemy import text
from ingestao.app.carregar_postgres import SessionLocal

async def main():
    async with SessionLocal() as session:
        query_job = \"select to_regclass('plataforma.job') is not null\"
        existe_job = await session.scalar(text(query_job))
        if existe_job:
            await session.execute(
                text(\"\"\"
                insert into plataforma.job (
                    id, dag_id, nome_job, fonte_ans, status, iniciado_em, finalizado_em,
                    registro_processado, registro_com_falha, mensagem_erro
                ) values (
                    :id, 'dag_dbt_consumo_refresh', 'refresh_consumo_ans', 'consumo_ans',
                    'sucesso', now(), now(), 0, 0, null
                )
                \"\"\"),
                {'id': str(uuid4())},
            )
        else:
            await session.execute(
                text(\"\"\"
                create table if not exists plataforma.refresh_consumo (
                    id uuid primary key,
                    dataset text not null,
                    nome_job text not null,
                    status text not null,
                    iniciado_em timestamptz not null,
                    concluido_em timestamptz,
                    comando text,
                    mensagem_erro text,
                    linhas_afetadas bigint
                )
                \"\"\")
            )
            await session.execute(
                text(\"\"\"
                insert into plataforma.refresh_consumo (
                    id, dataset, nome_job, status, iniciado_em, concluido_em, comando
                ) values (
                    :id, 'consumo_ans', 'dag_dbt_consumo_refresh', 'sucesso',
                    now(), now(), 'dbt consumo refresh'
                )
                \"\"\"),
                {'id': str(uuid4())},
            )
        await session.commit()

asyncio.run(main())
"
"""


with DAG(
    dag_id="dag_dbt_consumo_refresh",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "dbt", "consumo_ans"],
) as dag:
    run_marts = BashOperator(
        task_id="dbt_run_marts",
        cwd="/workspace/healthintel_dbt",
        bash_command=f"{DBT_ENV} dbt run --select +tag:mart",
    )
    run_consumo = BashOperator(
        task_id="dbt_run_consumo",
        cwd="/workspace/healthintel_dbt",
        bash_command=f"{DBT_ENV} dbt run --select tag:consumo",
    )
    test_consumo = BashOperator(
        task_id="dbt_test_consumo",
        cwd="/workspace/healthintel_dbt",
        bash_command=f"{DBT_ENV} dbt test --select tag:consumo",
    )
    registrar = BashOperator(
        task_id="registrar_refresh_consumo",
        cwd="/workspace",
        bash_command=REGISTRAR_REFRESH,
    )

    run_marts >> run_consumo >> test_consumo >> registrar
