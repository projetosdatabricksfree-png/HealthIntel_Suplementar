from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

DBT_ENV = (
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)

with DAG(
    dag_id="dag_mestre_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 20 * *",
    catchup=False,
    tags=["healthintel", "mensal"],
) as dag:
    preparar_particoes = PostgresOperator(
        task_id="preparar_particoes_sib",
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

    ingest_cadop = TriggerDagRunOperator(
        task_id="acionar_dag_ingest_cadop",
        trigger_dag_id="dag_ingest_cadop",
        wait_for_completion=True,
        reset_dag_run=True,
        conf={"competencia": "{{ dag_run.conf.get('competencia', ds_nodash[:6]) }}"},
    )

    ingest_sib = TriggerDagRunOperator(
        task_id="acionar_dag_ingest_sib",
        trigger_dag_id="dag_ingest_sib",
        wait_for_completion=True,
        reset_dag_run=True,
        conf={
            "competencia": "{{ dag_run.conf.get('competencia', ds_nodash[:6]) }}",
            "ufs": "{{ dag_run.conf.get('ufs', 'SP') }}",
        },
    )

    executar_dbt_servico = BashOperator(
        task_id="executar_dbt_servico",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build --select "
            "api_operadora api_score_operadora_mensal "
            "api_regulatorio_operadora_trimestral api_rn623_lista_trimestral"
        ),
    )

    registrar_evidencia = BashOperator(
        task_id="registrar_evidencia_mensal",
        cwd="/workspace",
        bash_command=r"""
        PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace python -c "
import asyncio
from uuid import uuid4
from sqlalchemy import text
from ingestao.app.carregar_postgres import SessionLocal

async def main():
    async with SessionLocal() as session:
        await session.execute(
            text('''
            insert into plataforma.job (
                id, dag_id, nome_job, fonte_ans, status, iniciado_em, finalizado_em,
                registro_processado, registro_com_falha, mensagem_erro
            ) values (
                :id, 'dag_mestre_mensal', 'orquestracao_mensal_minima', 'ans',
                'sucesso', now(), now(), 0, 0, null
            )
            '''),
            {'id': str(uuid4())},
        )
        await session.commit()

asyncio.run(main())
"
        """,
    )

    preparar_particoes >> ingest_cadop >> ingest_sib >> executar_dbt_servico >> registrar_evidencia
