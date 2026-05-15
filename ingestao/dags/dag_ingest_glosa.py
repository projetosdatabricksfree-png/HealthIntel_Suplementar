from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

_BASE = f"""{PYTHON_ENV} python -c "
import asyncio, os
from ingestao.app.ingestao_delta_ans import {{func}}
asyncio.run({{func}}(os.environ['HEALTHINTEL_COMPETENCIA']))
"
"""

with DAG(
    dag_id="dag_ingest_glosa",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 20 * *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "financeiro", "glosa", "delta_ans_100"],
) as dag:
    ingerir_glosa = BashOperator(
        task_id="ingerir_glosa_operadora_mensal",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
        },
        append_env=True,
        bash_command=_BASE.format(func="executar_ingestao_glosa_operadora"),
    )
