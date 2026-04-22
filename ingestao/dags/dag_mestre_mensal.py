from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="dag_mestre_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 20 * *",
    catchup=False,
    tags=["healthintel", "mensal"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")
    identificar_dataset = EmptyOperator(task_id="identificar_dataset")
    resolver_layout = EmptyOperator(task_id="resolver_layout")
    carregar_bruto = EmptyOperator(task_id="carregar_bruto")
    executar_dbt = EmptyOperator(task_id="executar_dbt")
    publicar_api = EmptyOperator(task_id="publicar_api")
    fim = EmptyOperator(task_id="fim")

    (
        inicio
        >> identificar_dataset
        >> resolver_layout
        >> carregar_bruto
        >> executar_dbt
        >> publicar_api
        >> fim
    )
