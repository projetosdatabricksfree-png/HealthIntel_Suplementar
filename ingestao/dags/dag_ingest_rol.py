from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_rol",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "arquivo": "",
        "versao": "",
        "url_fonte": "",
        "publicado_em": "",
    },
    tags=["healthintel", "rol", "versao_vigente"],
) as dag:
    carregar_rol_vigente = BashOperator(
        task_id="carregar_rol_vigente",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/carregar_versao_vigente.py "
            "--dataset rol_procedimento "
            "--arquivo '{{ params.arquivo }}' "
            "--versao '{{ params.versao }}' "
            "--url-fonte '{{ params.url_fonte }}' "
            "--publicado-em '{{ params.publicado_em }}'"
        ),
    )
