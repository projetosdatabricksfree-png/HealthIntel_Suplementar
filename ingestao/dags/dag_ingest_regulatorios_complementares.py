from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_regulatorios_complementares",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "regulatorios_complementares", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_penalidade = BashOperator(
        task_id="ingerir_penalidade_operadora",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_penalidade_operadora"),
    )

    ingerir_garantia = BashOperator(
        task_id="ingerir_monitoramento_garantia_atendimento",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(
            func="executar_ingestao_monitoramento_garantia_atendimento"
        ),
    )

    ingerir_peona = BashOperator(
        task_id="ingerir_peona_sus",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_peona_sus"),
    )

    ingerir_promoprev = BashOperator(
        task_id="ingerir_promoprev",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_promoprev"),
    )

    ingerir_rpc = BashOperator(
        task_id="ingerir_rpc",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_rpc"),
    )

    ingerir_iap = BashOperator(
        task_id="ingerir_iap",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_iap"),
    )

    ingerir_pfa = BashOperator(
        task_id="ingerir_pfa",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_pfa"),
    )

    ingerir_programa_qualificacao = BashOperator(
        task_id="ingerir_programa_qualificacao_institucional",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(
            func="executar_ingestao_programa_qualificacao_institucional"
        ),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_regulatorios_complementares",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_penalidade_operadora +stg_monitoramento_garantia_atendimento "
            "+stg_peona_sus +stg_promoprev +stg_rpc +stg_iap +stg_pfa "
            "+stg_programa_qualificacao_institucional "
            "api_penalidade_operadora api_garantia_atendimento "
            "api_peona_sus api_promoprev api_rpc_operadora_mes "
            "api_iap api_pfa api_programa_qualificacao_institucional"
        ),
    )

    [
        ingerir_penalidade,
        ingerir_garantia,
        ingerir_peona,
        ingerir_promoprev,
        ingerir_rpc,
        ingerir_iap,
        ingerir_pfa,
        ingerir_programa_qualificacao,
    ] >> dbt_transform
