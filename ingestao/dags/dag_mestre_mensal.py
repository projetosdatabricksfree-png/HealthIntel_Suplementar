from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

with DAG(
    dag_id="dag_mestre_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 20 * *",
    catchup=False,
    tags=["healthintel", "mensal"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    with TaskGroup(group_id="preparar_particoes") as preparar_particoes:
        preparar_particoes_inicio = EmptyOperator(task_id="inicio")
        preparar_particoes_fim = EmptyOperator(task_id="fim")
        preparar_particoes_inicio >> preparar_particoes_fim

    identificar_dataset = EmptyOperator(task_id="identificar_dataset")
    resolver_layout = EmptyOperator(task_id="resolver_layout")
    carregar_bruto = EmptyOperator(task_id="carregar_bruto")
    executar_dbt = EmptyOperator(task_id="executar_dbt")

    with TaskGroup(group_id="validar_freshness") as validar_freshness:
        validar_freshness_inicio = EmptyOperator(task_id="inicio")
        validar_freshness_fim = EmptyOperator(task_id="fim")
        validar_freshness_inicio >> validar_freshness_fim

    with TaskGroup(group_id="registrar_versao") as registrar_versao:
        registrar_versao_inicio = EmptyOperator(task_id="inicio")
        registrar_versao_fim = EmptyOperator(task_id="fim")
        registrar_versao_inicio >> registrar_versao_fim

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
