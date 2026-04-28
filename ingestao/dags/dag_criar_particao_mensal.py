from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

# LEGADO:
# O nome do arquivo/dag_id menciona "mensal" por compatibilidade.
# Desde a Sprint 35, as tabelas SIB usam particionamento anual por competencia YYYYMM.
# Não adicionar novas partições mensais para SIB neste arquivo.
# A criação mensal remanescente só pode existir para objetos fora do escopo de
# competencia SIB, como logs operacionais.

with DAG(
    dag_id="dag_criar_particao_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 0 25 * *",
    catchup=False,
    tags=["healthintel", "infra"],
) as dag:
    preparar_particoes_anuais_sib = PostgresOperator(
        task_id="preparar_particoes_anuais_sib",
        postgres_conn_id="postgres_default",
        sql="""
        select plataforma.preparar_particoes_janela_atual(
            'bruto_ans',
            'sib_beneficiario_operadora',
            2
        );

        select plataforma.preparar_particoes_janela_atual(
            'bruto_ans',
            'sib_beneficiario_municipio',
            2
        );
        """,
    )

    criar_particao_log_uso = PostgresOperator(
        task_id="criar_particao_log_uso",
        postgres_conn_id="postgres_default",
        sql="""
        do $$
        declare
            v_inicio timestamp;
            v_fim    timestamp;
            v_label  varchar(6);
        begin
            v_inicio := date_trunc('month', current_date + interval '1 month');
            v_fim    := date_trunc('month', current_date + interval '2 months');
            v_label  := to_char(v_inicio, 'YYYYMM');
            execute 'create table if not exists plataforma.log_uso_' || v_label ||
                ' partition of plataforma.log_uso for values from (''' || v_inicio::text ||
                ''') to (''' || v_fim::text || ''')';
        end $$;
        """,
    )

    preparar_particoes_anuais_sib >> criar_particao_log_uso
