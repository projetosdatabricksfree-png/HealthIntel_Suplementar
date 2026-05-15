from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_portabilidade",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 19 * *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "regulatorio", "portabilidade", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_fonte_indisponivel",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_fonte_indisponivel
asyncio.run(registrar_fonte_indisponivel(
    dominio='beneficiario',
    dataset_codigo='portabilidade_operadora_mensal',
    fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
    dag_id='dag_ingest_portabilidade',
    task_id='registrar_fonte_indisponivel',
    erro_mensagem='Portabilidade mensal por operadora nao disponivel no ANS FTP PDA.',
))
"
""",
    )
