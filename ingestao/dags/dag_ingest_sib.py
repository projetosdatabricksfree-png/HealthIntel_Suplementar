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
        task_id="ingerir_sib_operadora_streaming",
        cwd="/workspace",
        bash_command=r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from ingestao.app.ingestao_real import executar_ingestao_sib_uf_streaming

competencia_conf = '{{ dag_run.conf.get("competencia", "") }}'
competencia = competencia_conf or '{{ ds_nodash[:6] }}'
ufs_conf = '{{ dag_run.conf.get("ufs", "SP") }}'
ufs = [uf.strip().upper() for uf in ufs_conf.split(',') if uf.strip()]

async def main():
    resultados = []
    for uf in ufs:
        resultados.append(await executar_ingestao_sib_uf_streaming(competencia, uf))
    print(resultados)

asyncio.run(main())
"
        """,
    )
