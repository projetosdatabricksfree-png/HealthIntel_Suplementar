from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"
DBT_ENV = (
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)

# Modelos dbt dependentes do SIB tipado — rebuildar apos ingestao bem-sucedida
_DBT_SELECTORS = (
    "+api_ranking_score "
    "+api_market_share_mensal "
    "+api_score_operadora_mensal "
    "+api_ranking_crescimento "
    "+api_ranking_oportunidade"
)
_DBT_EXCLUDE = "tag:tiss tag:premium tag:consumo_premium"

with DAG(
    dag_id="dag_ingest_sib",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "retry_exponential_backoff": True,
    },
    params={
        "ufs": "SP",
        "competencia": "",
    },
    tags=["healthintel", "sib", "core_ans"],
) as dag:
    ingerir_sib = BashOperator(
        task_id="ingerir_sib_operadora_streaming",
        cwd="/workspace",
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
from ingestao.app.ingestao_real import executar_ingestao_sib_uf_streaming

competencia_conf = '{{{{ dag_run.conf.get("competencia", "") }}}}'
competencia = competencia_conf or '{{{{ ds_nodash[:6] }}}}'
ufs_conf = '{{{{ dag_run.conf.get("ufs", "SP") }}}}'
ufs = [uf.strip().upper() for uf in ufs_conf.split(',') if uf.strip()]

async def main():
    resultados = []
    for uf in ufs:
        resultados.append(await executar_ingestao_sib_uf_streaming(competencia, uf))
    print(resultados)

asyncio.run(main())
"
        """,
    )

    limpar_genericos_sib = BashOperator(
        task_id="limpar_genericos_sib",
        cwd="/workspace",
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from ingestao.app.carregar_postgres import SessionLocal

async def main():
    job_id = str(uuid.uuid4())
    iniciado_em = datetime.now(tz=timezone.utc)
    async with SessionLocal() as session:
        await session.execute(
            text(\"\"\"
                INSERT INTO plataforma.job (id, dag_id, nome_job, fonte_ans, status, iniciado_em,
                    registro_processado, registro_com_falha)
                VALUES (:id, 'dag_ingest_sib', 'limpeza_genericos_sib', 'sib_operadora,sib_municipio',
                    'iniciado', :iniciado_em, 0, 0)
            \"\"\"),
            {{'id': job_id, 'iniciado_em': iniciado_em}}
        )
        await session.commit()
        result = await session.execute(
            text(\"\"\"
                DELETE FROM bruto_ans.ans_linha_generica
                WHERE dataset_codigo IN ('sib_operadora', 'sib_municipio');
            \"\"\")
        )
        removidos = result.rowcount
        print(f'[limpar_genericos_sib] removidos: {{removidos}} registros genericos')
        await session.commit()
        await session.execute(
            text(\"\"\"
                UPDATE plataforma.job
                SET status = 'sucesso', finalizado_em = :fim, registro_processado = :n
                WHERE id = :id
            \"\"\"),
            {{'id': job_id, 'fim': datetime.now(tz=timezone.utc), 'n': removidos}}
        )
        await session.commit()

asyncio.run(main())
"
        """,
    )

    rebuild_serving_sib = BashOperator(
        task_id="rebuild_serving_sib",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build "
            f"--select {_DBT_SELECTORS} "
            f"--exclude {_DBT_EXCLUDE}"
        ),
    )

    ingerir_sib >> limpar_genericos_sib >> rebuild_serving_sib
