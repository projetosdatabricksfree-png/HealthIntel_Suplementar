from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_produto_plano",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "produto_plano", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
    """

    ingerir_produto_caracteristica = BashOperator(
        task_id="ingerir_produto_caracteristica",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_produto_caracteristica"),
    )

    ingerir_historico_plano = BashOperator(
        task_id="ingerir_historico_plano",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_historico_plano"),
    )

    ingerir_plano_servico_opcional = BashOperator(
        task_id="ingerir_plano_servico_opcional",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(func="executar_ingestao_plano_servico_opcional"),
    )

    ingerir_quadro_auxiliar = BashOperator(
        task_id="ingerir_quadro_auxiliar_corresponsabilidade",
        cwd="/workspace",
        env={"HEALTHINTEL_COMPETENCIA": "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"},
        bash_command=_BASE.format(
            func="executar_ingestao_quadro_auxiliar_corresponsabilidade"
        ),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_produto_plano",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select tag:delta_ans_100,config.materialized:table "
            "+stg_produto_caracteristica +stg_historico_plano "
            "+stg_plano_servico_opcional "
            "api_produto_plano api_historico_plano "
            "consumo_produto_plano"
        ),
    )

    [
        ingerir_produto_caracteristica,
        ingerir_historico_plano,
        ingerir_plano_servico_opcional,
        ingerir_quadro_auxiliar,
    ] >> dbt_transform
