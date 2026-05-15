from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_fip",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 21 */3 *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "financeiro", "fip", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_fonte_indisponivel",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_fonte_indisponivel
asyncio.run(registrar_fonte_indisponivel(
    dominio='financeiro',
    dataset_codigo='fip_operadora_trimestral',
    fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
    dag_id='dag_ingest_fip',
    task_id='registrar_fonte_indisponivel',
    erro_mensagem='FIP (Ficha de Informacoes Periodicas - sinistralidade, contraprestacao) nao disponivel como arquivo plano no ANS FTP PDA. DIOPS conta-contabeis disponivel, mas requer pivot para colunas FIP.',
))
"
""",
    )
