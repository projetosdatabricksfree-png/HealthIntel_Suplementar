from __future__ import annotations

import asyncio
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestao.app.ingestao_real import executar_ingestao_cadop


def _executar(**context) -> dict:
    competencia = context["dag_run"].conf.get("competencia") if context.get("dag_run") else None
    competencia = competencia or context["ds"].replace("-", "")[:6]
    return asyncio.run(executar_ingestao_cadop(competencia))


with DAG(
    dag_id="dag_ingest_cadop",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "cadop"],
) as dag:
    ingerir_cadop = PythonOperator(task_id="ingerir_cadop", python_callable=_executar)
