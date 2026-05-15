from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_rn623",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 17 */3 *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "regulatorio", "rn623", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_fonte_indisponivel",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_fonte_indisponivel
asyncio.run(registrar_fonte_indisponivel(
    dominio='regulatorio',
    dataset_codigo='rn623_lista_operadora_trimestral',
    fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
    dag_id='dag_ingest_rn623',
    task_id='registrar_fonte_indisponivel',
    erro_mensagem='Lista RN623 trimestral por operadora nao localizada no ANS FTP PDA. Possivel fonte: sistema interno ANS / publicacao em portal separado.',
))
"
""",
    )
