from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_precificacao_ntrp",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "precificacao_ntrp", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_ntrp_area = BashOperator(
        task_id="ingerir_ntrp_area_comercializacao",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_ntrp_area_comercializacao"),
    )

    ingerir_painel = BashOperator(
        task_id="ingerir_painel_precificacao",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_painel_precificacao"),
    )

    ingerir_reajuste = BashOperator(
        task_id="ingerir_percentual_reajuste_agrupamento",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_percentual_reajuste_agrupamento"),
    )

    ingerir_ntrp_vcm = BashOperator(
        task_id="ingerir_ntrp_vcm_faixa_etaria",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_ntrp_vcm_faixa_etaria"),
    )

    ingerir_vcm_municipio = BashOperator(
        task_id="ingerir_valor_comercial_medio_municipio",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_valor_comercial_medio_municipio"),
    )

    ingerir_faixa_preco = BashOperator(
        task_id="ingerir_faixa_preco",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_faixa_preco"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_precificacao_ntrp",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_ntrp_area_comercializacao +stg_painel_precificacao "
            "+stg_percentual_reajuste_agrupamento +stg_ntrp_vcm_faixa_etaria "
            "+stg_valor_comercial_medio_municipio +stg_faixa_preco "
            "api_ntrp_area_comercializacao api_painel_precificacao "
            "api_reajuste_agrupamento api_ntrp_vcm_faixa_etaria "
            "api_valor_comercial_medio_municipio api_faixa_preco"
        ),
    )

    [
        ingerir_ntrp_area,
        ingerir_painel,
        ingerir_reajuste,
        ingerir_ntrp_vcm,
        ingerir_vcm_municipio,
        ingerir_faixa_preco,
    ] >> dbt_transform
