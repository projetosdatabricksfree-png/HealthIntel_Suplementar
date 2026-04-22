import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal, carregar_idss_bruto


async def seed_demo_idss() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                delete from bruto_ans.idss
                where _arquivo_origem like 'idss_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset = 'idss'
                """
            )
        )
        await session.commit()

    await carregar_idss_bruto(
        [
            {
                "ano_base": 2024,
                "registro_ans": "123456",
                "idss_total": 0.8421,
                "idqs": 0.8010,
                "idga": 0.8230,
                "idsm": 0.8700,
                "idgr": 0.9150,
                "faixa_idss": "A",
                "fonte_publicacao": "idss_demo_2024",
            },
            {
                "ano_base": 2024,
                "registro_ans": "654321",
                "idss_total": 0.7125,
                "idqs": 0.6900,
                "idga": 0.7050,
                "idsm": 0.7300,
                "idgr": 0.7800,
                "faixa_idss": "B",
                "fonte_publicacao": "idss_demo_2024",
            },
        ],
        arquivo_origem="idss_demo_2024.csv",
        layout_id="layout_idss_csv",
        layout_versao_id="layout_idss_csv:v1",
        hash_arquivo="demo_hash_idss_2024",
        hash_estrutura="demo_hash_estrutura_idss_v1",
    )

    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.job (
                    id,
                    dag_id,
                    nome_job,
                    fonte_ans,
                    status,
                    iniciado_em,
                    finalizado_em,
                    registro_processado,
                    registro_com_falha
                ) values (
                    :id,
                    :dag_id,
                    :nome_job,
                    :fonte_ans,
                    :status,
                    :iniciado_em,
                    :finalizado_em,
                    :registro_processado,
                    :registro_com_falha
                )
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": "dag_anual_idss",
                "nome_job": "seed_demo_idss",
                "fonte_ans": "idss",
                "status": "sucesso",
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": 2,
                "registro_com_falha": 0,
            },
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_idss())
