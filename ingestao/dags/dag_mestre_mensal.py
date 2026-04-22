from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.subdag import SubDagOperator

with DAG(
    dag_id="dag_mestre_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 20 * *",
    catchup=False,
    tags=["healthintel", "mensal"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    preparar_particoes = SubDagOperator(
        task_id="preparar_particoes",
        subdag_id="dag_criar_particao_mensal",
    )

    identificar_dataset = EmptyOperator(task_id="identificar_dataset")
    resolver_layout = EmptyOperator(task_id="resolver_layout")
    carregar_bruto = EmptyOperator(task_id="carregar_bruto")
    executar_dbt = EmptyOperator(task_id="executar_dbt")

    validar_freshness = SubDagOperator(
        task_id="validar_freshness",
        subdag_id="dag_dbt_freshness",
    )

    registrar_versao = SubDagOperator(
        task_id="registrar_versao",
        subdag_id="dag_registrar_versao",
    )

    publicar_api = EmptyOperator(task_id="publicar_api")
    fim = EmptyOperator(task_id="fim")

    (
        inicio
        >> preparar_particoes
        >> identificar_dataset
        >> resolver_layout
        >> carregar_bruto
        >> executar_dbt
        >> validar_freshness
        >> registrar_versao
        >> publicar_api
        >> fim
    )
