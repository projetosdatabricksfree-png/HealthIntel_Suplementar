from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_rede_assistencial",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 20 * *",
    catchup=False,
    tags=["healthintel", "rede", "cobertura", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_fonte_indisponivel",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_fonte_indisponivel
asyncio.run(registrar_fonte_indisponivel(
    dominio='rede',
    dataset_codigo='rede_assistencial_quarentena',
    fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
    dag_id='dag_ingest_rede_assistencial',
    task_id='registrar_fonte_indisponivel',
    erro_mensagem='Rede assistencial detalhada (municipio+operadora) nao disponivel como arquivo plano no ANS FTP PDA. Dados de rede_prestador_municipio sao carregados via dag_ingest_rede_prestadores.',
))
"
""",
    )
