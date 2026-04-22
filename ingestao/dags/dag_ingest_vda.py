from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="dag_ingest_vda",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 15 * *",
    catchup=False,
    tags=["healthintel", "financeiro_v2", "vda"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")
    mapear_publicacao = EmptyOperator(task_id="mapear_publicacao")
    validar_layout = EmptyOperator(task_id="validar_layout")
    carregar_bruto = EmptyOperator(task_id="carregar_bruto")
    registrar_versao = EmptyOperator(task_id="registrar_versao")
    fim = EmptyOperator(task_id="fim")

    inicio >> mapear_publicacao >> validar_layout >> carregar_bruto >> registrar_versao >> fim
