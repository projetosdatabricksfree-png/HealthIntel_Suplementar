from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_tuss",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "arquivo": "",
        "versao": "",
        "url_fonte": "",
        "publicado_em": "",
    },
    tags=["healthintel", "tuss", "versao_vigente"],
) as dag:
    carregar_tuss_vigente = BashOperator(
        task_id="carregar_tuss_vigente",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/carregar_versao_vigente.py "
            "--dataset tuss_procedimento "
            "--arquivo '{{ params.arquivo }}' "
            "--versao '{{ params.versao }}' "
            "--url-fonte '{{ params.url_fonte }}' "
            "--publicado-em '{{ params.publicado_em }}'"
        ),
    )
