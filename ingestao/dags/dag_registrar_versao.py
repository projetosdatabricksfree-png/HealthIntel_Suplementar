from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id="dag_registrar_versao",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthintel", "metadata"],
    params={
        "dataset": "generic",
        "competencia": "202603",
        "versao": "1.0.0",
        "hash_arquivo": "manual",
        "registros": 0,
        "status": "registrado",
    },
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    registrar_versao = PostgresOperator(
        task_id="registrar_versao",
        postgres_conn_id="postgres_default",
        sql="""
        insert into plataforma.versao_dataset (
            id,
            dataset,
            versao,
            competencia,
            hash_arquivo,
            carregado_em,
            registros,
            status
        ) values (
            gen_random_uuid(),
            '{{ params.dataset }}',
            '{{ params.versao }}',
            '{{ params.competencia }}',
            '{{ params.hash_arquivo }}',
            now(),
            {{ params.registros }},
            '{{ params.status }}'
        );
        """,
    )

    fim = EmptyOperator(task_id="fim")

    inicio >> registrar_versao >> fim
