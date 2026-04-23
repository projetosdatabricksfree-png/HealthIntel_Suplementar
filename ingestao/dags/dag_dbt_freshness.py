from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="dag_dbt_freshness",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    tags=["healthintel", "dbt"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    executar_freshness = BashOperator(
        task_id="executar_freshness",
        bash_command="cd /workspace/healthintel_dbt && /home/airflow/.local/bin/dbt source freshness",
    )

    fim = EmptyOperator(task_id="fim")

    inicio >> executar_freshness >> fim
