from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="dag_anual_idss",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthintel", "idss", "anual"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")
    dag_ingest_idss = EmptyOperator(task_id="dag_ingest_idss")
    dag_dbt_staging_idss = EmptyOperator(task_id="dag_dbt_staging_idss")
    dag_dbt_fat_idss = EmptyOperator(task_id="dag_dbt_fat_idss")
    dag_dbt_recalculo_score = EmptyOperator(task_id="dag_dbt_recalculo_score")
    fim = EmptyOperator(task_id="fim")

    (
        inicio
        >> dag_ingest_idss
        >> dag_dbt_staging_idss
        >> dag_dbt_fat_idss
        >> dag_dbt_recalculo_score
        >> fim
    )
