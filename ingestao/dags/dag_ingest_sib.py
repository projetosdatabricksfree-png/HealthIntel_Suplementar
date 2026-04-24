from __future__ import annotations

import asyncio
import os
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestao.app.ingestao_real import executar_ingestao_sib_uf


def _executar(**context) -> list[dict]:
    competencia = context["dag_run"].conf.get("competencia") if context.get("dag_run") else None
    competencia = competencia or context["ds"].replace("-", "")[:6]
    ufs = os.getenv("ANS_SIB_UFS", "SP").split(",")
    return [
        asyncio.run(executar_ingestao_sib_uf(competencia, uf.strip()))
        for uf in ufs
        if uf.strip()
    ]


with DAG(
    dag_id="dag_ingest_sib",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "sib"],
) as dag:
    ingerir_sib = PythonOperator(task_id="ingerir_sib", python_callable=_executar)
