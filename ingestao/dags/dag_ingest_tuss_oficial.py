from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_tuss_oficial",
    start_date=datetime(2026, 1, 1),
    schedule="@yearly",
    catchup=False,
    tags=["healthintel", "tuss_oficial", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_tuss_oficial = BashOperator(
        task_id="ingerir_tuss_oficial",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_tuss_oficial"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_tuss_oficial",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_tuss_terminologia_oficial "
            "api_tuss_procedimento_vigente "
            "consumo_tuss_procedimento_vigente"
        ),
    )

    ingerir_tuss_oficial >> dbt_transform
