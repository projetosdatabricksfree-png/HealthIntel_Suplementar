from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_sip_delta",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "sip", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_sip_mapa_assistencial = BashOperator(
        task_id="ingerir_sip_mapa_assistencial",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_sip_mapa_assistencial"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_sip",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_sip_mapa_assistencial "
            "api_sip_assistencial_operadora "
            "consumo_sip_assistencial_operadora"
        ),
    )

    ingerir_sip_mapa_assistencial >> dbt_transform
