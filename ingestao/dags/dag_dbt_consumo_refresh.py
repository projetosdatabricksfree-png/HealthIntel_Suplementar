from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


def _dbt(*args: str) -> None:
    dbt_executavel = Path(".venv/bin/dbt")
    comando = [str(dbt_executavel) if dbt_executavel.exists() else "dbt", *args]
    resultado = subprocess.run(
        comando,
        cwd="healthintel_dbt",
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stdout + "\n" + resultado.stderr)


async def _registrar_refresh_async(status: str, mensagem_erro: str | None = None) -> None:
    async with SessionLocal() as session:
        existe_job = await session.scalar(
            text("select to_regclass('plataforma.job') is not null")
        )
        if not existe_job:
            await session.execute(
                text(
                    """
                    create table if not exists plataforma.refresh_consumo (
                        id uuid primary key,
                        dataset text not null,
                        nome_job text not null,
                        status text not null,
                        iniciado_em timestamptz not null,
                        concluido_em timestamptz,
                        comando text,
                        mensagem_erro text,
                        linhas_afetadas bigint
                    )
                    """
                )
            )
            await session.execute(
                text(
                    """
                    insert into plataforma.refresh_consumo (
                        id,
                        dataset,
                        nome_job,
                        status,
                        iniciado_em,
                        concluido_em,
                        comando,
                        mensagem_erro
                    ) values (
                        :id,
                        'consumo_ans',
                        'dag_dbt_consumo_refresh',
                        :status,
                        now(),
                        now(),
                        :comando,
                        :erro
                    )
                    """
                ),
                {
                    "id": str(uuid4()),
                    "status": status,
                    "comando": "dbt consumo refresh",
                    "erro": mensagem_erro,
                },
            )
            await session.commit()
            return
        await session.execute(
            text(
                """
                insert into plataforma.job (
                    id, dag_id, nome_job, fonte_ans, status, iniciado_em, finalizado_em,
                    registro_processado, registro_com_falha, mensagem_erro
                ) values (
                    :id, 'dag_dbt_consumo_refresh', 'refresh_consumo_ans', 'consumo_ans',
                    :status, now(), now(), 0, :falhas, :erro
                )
                """
            ),
            {
                "id": str(uuid4()),
                "status": status,
                "falhas": 1 if mensagem_erro else 0,
                "erro": mensagem_erro,
            },
        )
        await session.commit()


def _registrar_refresh(status: str, mensagem_erro: str | None = None) -> None:
    asyncio.run(_registrar_refresh_async(status, mensagem_erro))


def dbt_run_marts() -> None:
    _dbt("run", "--select", "tag:mart")


def dbt_run_consumo() -> None:
    _dbt("run", "--select", "tag:consumo")


def dbt_test_consumo() -> None:
    _dbt("test", "--select", "tag:consumo")


def registrar_refresh_consumo() -> None:
    _registrar_refresh("sucesso")


with DAG(
    dag_id="dag_dbt_consumo_refresh",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["healthintel", "dbt", "consumo_ans"],
) as dag:
    run_marts = PythonOperator(task_id="dbt_run_marts", python_callable=dbt_run_marts)
    run_consumo = PythonOperator(task_id="dbt_run_consumo", python_callable=dbt_run_consumo)
    test_consumo = PythonOperator(task_id="dbt_test_consumo", python_callable=dbt_test_consumo)
    registrar = PythonOperator(
        task_id="registrar_refresh_consumo",
        python_callable=registrar_refresh_consumo,
    )

    run_marts >> run_consumo >> test_consumo >> registrar
