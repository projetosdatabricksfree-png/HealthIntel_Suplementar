from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_tiss_subfamilias",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "tiss_subfamilias", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_tiss_ambulatorial = BashOperator(
        task_id="ingerir_tiss_ambulatorial",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_tiss_ambulatorial"),
    )

    ingerir_tiss_hospitalar = BashOperator(
        task_id="ingerir_tiss_hospitalar",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_tiss_hospitalar"),
    )

    ingerir_tiss_dados_plano = BashOperator(
        task_id="ingerir_tiss_dados_plano",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_tiss_dados_plano"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_tiss_subfamilias",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_tiss_ambulatorial +stg_tiss_hospitalar +stg_tiss_dados_plano "
            "api_tiss_ambulatorial_operadora_mes api_tiss_hospitalar_operadora_mes "
            "api_tiss_plano_mes consumo_tiss_utilizacao_operadora_mes"
        ),
    )

    [
        ingerir_tiss_ambulatorial,
        ingerir_tiss_hospitalar,
        ingerir_tiss_dados_plano,
    ] >> dbt_transform
