from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_cadop",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "cadop"],
) as dag:
    ingerir_cadop = BashOperator(
        task_id="ingerir_cadop",
        cwd="/workspace",
        bash_command=r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from ingestao.app.ingestao_real import executar_ingestao_cadop

competencia_conf = '{{ dag_run.conf.get("competencia", "") }}'
competencia = competencia_conf or '{{ ds_nodash[:6] }}'
asyncio.run(executar_ingestao_cadop(competencia))
"
        """,
    )
