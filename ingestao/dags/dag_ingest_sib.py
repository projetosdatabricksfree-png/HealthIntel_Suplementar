from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_sib",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "sib"],
) as dag:
    ingerir_sib = BashOperator(
        task_id="ingerir_sib",
        cwd="/workspace",
        bash_command=r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
import os
from ingestao.app.ingestao_real import executar_ingestao_sib_uf

async def main():
    competencia_conf = '{{ dag_run.conf.get("competencia", "") }}'
    competencia = competencia_conf or '{{ ds_nodash[:6] }}'
    ufs = [uf.strip() for uf in os.getenv('ANS_SIB_UFS', 'SP').split(',') if uf.strip()]
    for uf in ufs:
        await executar_ingestao_sib_uf(competencia, uf)

asyncio.run(main())
"
        """,
    )
