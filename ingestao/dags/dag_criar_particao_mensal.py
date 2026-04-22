from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id="dag_criar_particao_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 0 25 * *",
    catchup=False,
    tags=["healthintel", "infra"],
) as dag:
    criar_particao_sib_operadora = PostgresOperator(
        task_id="criar_particao_sib_operadora",
        postgres_conn_id="postgres_default",
        sql="""
        do $$
        declare
            v_next_competencia varchar(6);
        begin
            v_next_competencia := to_char(date_trunc('month', current_date + interval '1 month'), 'YYYYMM');
            execute 'create table if not exists bruto_ans.sib_beneficiario_operadora_' || v_next_competencia ||
                ' partition of bruto_ans.sib_beneficiario_operadora for values from (''' || v_next_competencia ||
                ''') to (''' || to_char(date_trunc('month', current_date + interval '2 months'), 'YYYYMM') || ''')';
        end $$;
        """,
    )

    criar_particao_sib_municipio = PostgresOperator(
        task_id="criar_particao_sib_municipio",
        postgres_conn_id="postgres_default",
        sql="""
        do $$
        declare
            v_next_competencia varchar(6);
        begin
            v_next_competencia := to_char(date_trunc('month', current_date + interval '1 month'), 'YYYYMM');
            execute 'create table if not exists bruto_ans.sib_beneficiario_municipio_' || v_next_competencia ||
                ' partition of bruto_ans.sib_beneficiario_municipio for values from (''' || v_next_competencia ||
                ''') to (''' || to_char(date_trunc('month', current_date + interval '2 months'), 'YYYYMM') || ''')';
        end $$;
        """,
    )

    criar_particao_log_uso = PostgresOperator(
        task_id="criar_particao_log_uso",
        postgres_conn_id="postgres_default",
        sql="""
        do $$
        declare
            v_next_competencia varchar(6);
        begin
            v_next_competencia := to_char(date_trunc('month', current_date + interval '1 month'), 'YYYYMM');
            execute 'create table if not exists plataforma.log_uso_' || v_next_competencia ||
                ' partition of plataforma.log_uso for values from (''' || v_next_competencia ||
                ''') to (''' || to_char(date_trunc('month', current_date + interval '2 months'), 'YYYYMM') || ''')';
        end $$;
        """,
    )

    [criar_particao_sib_operadora, criar_particao_sib_municipio, criar_particao_log_uso]
