from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_ingest_rede_prestadores",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["healthintel", "rede_prestadores", "delta_ans_100"],
) as dag:
    _BASE = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from ingestao.app.ingestao_delta_ans import {func}
competencia_conf = '{{ dag_run.conf.get(\"competencia\", \"\") }}'
competencia = competencia_conf or '{{ ds_nodash[:6] }}'
asyncio.run({func}(competencia))
"
    """
    _BASE_NO_COMP = r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from ingestao.app.ingestao_delta_ans import {func}
asyncio.run({func}())
"
    """

    ingerir_operadora_cancelada = BashOperator(
        task_id="ingerir_operadora_cancelada",
        cwd="/workspace",
        bash_command=_BASE_NO_COMP.format(func="executar_ingestao_operadora_cancelada"),
    )

    ingerir_operadora_acreditada = BashOperator(
        task_id="ingerir_operadora_acreditada",
        cwd="/workspace",
        bash_command=_BASE_NO_COMP.format(func="executar_ingestao_operadora_acreditada"),
    )

    ingerir_prestador_acreditado = BashOperator(
        task_id="ingerir_prestador_acreditado",
        cwd="/workspace",
        bash_command=_BASE_NO_COMP.format(func="executar_ingestao_prestador_acreditado"),
    )

    ingerir_produto_prestador_hosp = BashOperator(
        task_id="ingerir_produto_prestador_hospitalar",
        cwd="/workspace",
        bash_command=_BASE.format(func="executar_ingestao_produto_prestador_hospitalar"),
    )

    ingerir_operadora_prestador_nao_hosp = BashOperator(
        task_id="ingerir_operadora_prestador_nao_hospitalar",
        cwd="/workspace",
        bash_command=_BASE.format(func="executar_ingestao_operadora_prestador_nao_hospitalar"),
    )

    ingerir_solicitacao_alteracao = BashOperator(
        task_id="ingerir_solicitacao_alteracao_rede_hospitalar",
        cwd="/workspace",
        bash_command=_BASE.format(
            func="executar_ingestao_solicitacao_alteracao_rede_hospitalar"
        ),
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform_rede_prestadores",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            "dbt build --select "
            "+stg_operadora_cancelada +stg_operadora_acreditada "
            "+stg_prestador_acreditado +stg_produto_prestador_hospitalar "
            "+stg_operadora_prestador_nao_hospitalar "
            "+stg_solicitacao_alteracao_rede_hospitalar "
            "api_operadora_cancelada api_operadora_acreditada "
            "api_prestador_acreditado api_produto_prestador_hospitalar "
            "api_operadora_prestador_nao_hospitalar api_alteracao_rede_hospitalar"
        ),
    )

    [
        ingerir_operadora_cancelada,
        ingerir_operadora_acreditada,
        ingerir_prestador_acreditado,
        ingerir_produto_prestador_hosp,
        ingerir_operadora_prestador_nao_hosp,
        ingerir_solicitacao_alteracao,
    ] >> dbt_transform
