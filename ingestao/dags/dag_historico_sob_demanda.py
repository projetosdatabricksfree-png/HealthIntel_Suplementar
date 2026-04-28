from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_historico_sob_demanda",
    start_date=datetime(2026, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["healthintel", "historico_sob_demanda", "premium"],
) as dag:
    processar_solicitacao_aprovada = BashOperator(
        task_id="processar_solicitacao_aprovada",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python -c "
            "\"from ingestao.app.historico_sob_demanda import "
            "processar_proxima_solicitacao_historico_sync; "
            "print(processar_proxima_solicitacao_historico_sync())\""
        ),
    )
