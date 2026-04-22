from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="dag_registrar_versao",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthintel", "metadata"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    registrar_versao = PostgresOperator(
        task_id="registrar_versao",
        postgres_conn_id="postgres_default",
        sql="""
        insert into plataforma.versao_dataset (
            dataset,
            competencia,
            versao_metodologia,
            data_inicio_vigencia,
            data_fim_vigencia,
            ativo,
            _criado_em
        ) values (
            '{{ params.dataset }}',
            '{{ params.competencia }}',
            '{{ params.versao_metodologia }}',
            current_date,
            null,
            true,
            now()
        )
        on conflict (dataset, competencia) do update
        set versao_metodologia = excluded.versao_metodologia,
            data_fim_vigencia = null,
            ativo = true;
        """,
        params={
            "dataset": "generic",
            "competencia": "{{ ti.xcom_pull(key='competencia') }}",
            "versao_metodologia": "1.0.0",
        },
    )

    fim = EmptyOperator(task_id="fim")

    inicio >> registrar_versao >> fim
