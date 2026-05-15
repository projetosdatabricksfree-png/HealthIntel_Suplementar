from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_diops",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 20 */3 *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "financeiro", "diops", "delta_ans_100"],
) as dag:
    ingerir_diops = BashOperator(
        task_id="ingerir_diops_operadora",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import executar_ingestao_diops_operadora
asyncio.run(executar_ingestao_diops_operadora(os.environ['HEALTHINTEL_COMPETENCIA']))
"
""",
    )

    registrar_layout = BashOperator(
        task_id="registrar_layout_nao_mapeado",
        cwd="/workspace",
        trigger_rule="all_done",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_layout_nao_mapeado
asyncio.run(registrar_layout_nao_mapeado(
    dominio='financeiro',
    dataset_codigo='diops_operadora_trimestral',
    arquivo_nome='diops_YYYYMMDD.zip',
    assinatura='DATA;REG_ANS;CD_CONTA_CONTABIL;DESCRICAO;VL_SALDO_INICIAL;VL_SALDO_FINAL',
    dag_id='dag_ingest_diops',
    task_id='registrar_layout_nao_mapeado',
    rascunho_id='diops_contas_contabeis_pivot_necessario',
))
"
""",
    )

    ingerir_diops >> registrar_layout
