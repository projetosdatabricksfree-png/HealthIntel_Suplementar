from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_beneficiarios_cobertura",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "beneficiarios_cobertura", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_regiao_geografica = BashOperator(
        task_id="ingerir_beneficiario_regiao_geografica",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_beneficiario_regiao_geografica"),
    )

    ingerir_informacao_consolidada = BashOperator(
        task_id="ingerir_beneficiario_informacao_consolidada",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(
            func="executar_ingestao_beneficiario_informacao_consolidada"
        ),
    )

    ingerir_taxa_cobertura = BashOperator(
        task_id="ingerir_taxa_cobertura_plano",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_taxa_cobertura_plano"),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_beneficiarios_cobertura",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_beneficiario_regiao_geografica "
            "+stg_beneficiario_informacao_consolidada "
            "+stg_taxa_cobertura_plano "
            "api_beneficiario_regiao_geografica "
            "api_beneficiario_informacao_consolidada "
            "api_taxa_cobertura_plano"
        ),
    )

    [
        ingerir_regiao_geografica,
        ingerir_informacao_consolidada,
        ingerir_taxa_cobertura,
    ] >> dbt_transform
