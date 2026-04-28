from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_prestador_cadastral",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "arquivo": "",
        "versao": "",
        "url_fonte": "",
        "publicado_em": "",
    },
    tags=["healthintel", "prestador_cadastral", "snapshot_atual"],
) as dag:
    carregar_prestador_cadastral_vigente = BashOperator(
        task_id="carregar_prestador_cadastral_vigente",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/carregar_versao_vigente.py "
            "--dataset prestador_cadastral "
            "--arquivo '{{ params.arquivo }}' "
            "--versao '{{ params.versao }}' "
            "--url-fonte '{{ params.url_fonte }}' "
            "--publicado-em '{{ params.publicado_em }}'"
        ),
    )
