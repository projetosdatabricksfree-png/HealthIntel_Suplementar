from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_ressarcimento_sus",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "ressarcimento_sus", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_ressarcimento_abi = BashOperator(
        task_id="ingerir_ressarcimento_beneficiario_abi",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_ressarcimento_beneficiario_abi"),
    )

    ingerir_ressarcimento_operadora_plano = BashOperator(
        task_id="ingerir_ressarcimento_sus_operadora_plano",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_ressarcimento_sus_operadora_plano"),
    )

    ingerir_ressarcimento_hc = BashOperator(
        task_id="ingerir_ressarcimento_hc",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_ressarcimento_hc"),
    )

    ingerir_ressarcimento_cobranca = BashOperator(
        task_id="ingerir_ressarcimento_cobranca_arrecadacao",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_ressarcimento_cobranca_arrecadacao"),
    )

    ingerir_ressarcimento_indice = BashOperator(
        task_id="ingerir_ressarcimento_indice_pagamento",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_ressarcimento_indice_pagamento"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_ressarcimento_sus",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_ressarcimento_beneficiario_abi "
            "+stg_ressarcimento_sus_operadora_plano "
            "+stg_ressarcimento_hc "
            "+stg_ressarcimento_cobranca_arrecadacao "
            "+stg_ressarcimento_indice_pagamento "
            "api_ressarcimento_beneficiario_abi "
            "api_ressarcimento_sus_operadora_plano "
            "api_ressarcimento_hc "
            "api_ressarcimento_cobranca_arrecadacao "
            "api_ressarcimento_indice_pagamento "
            "consumo_ressarcimento_sus_operadora"
        ),
    )

    [
        ingerir_ressarcimento_abi,
        ingerir_ressarcimento_operadora_plano,
        ingerir_ressarcimento_hc,
        ingerir_ressarcimento_cobranca,
        ingerir_ressarcimento_indice,
    ] >> dbt_transform
