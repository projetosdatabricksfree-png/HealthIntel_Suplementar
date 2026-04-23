import asyncio
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal, carregar_rede_assistencial_bruto


async def limpar_registros_demo() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                delete from bruto_ans.rede_prestador_municipio
                where _arquivo_origem like 'rede_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset = 'rede_assistencial'
                    and status = 'demo_local_rede'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.publicacao_rede
                where versao_publicacao like 'rede_demo_%'
                """
            )
        )
        await session.commit()


async def registrar_publicacoes() -> None:
    async with SessionLocal() as session:
        for competencia in ("202603", "202604"):
            await session.execute(
                text(
                    """
                    insert into plataforma.publicacao_rede (
                        dataset,
                        competencia,
                        data_publicacao_ans,
                        versao_publicacao,
                        hash_sha256,
                        observacao
                    ) values (
                        'rede_assistencial',
                        :competencia,
                        :data_publicacao_ans,
                        :versao_publicacao,
                        :hash_sha256,
                        :observacao
                    )
                    on conflict (dataset, competencia, versao_publicacao) do update set
                        data_publicacao_ans = excluded.data_publicacao_ans,
                        hash_sha256 = excluded.hash_sha256,
                        observacao = excluded.observacao
                    """
                ),
                {
                    "competencia": competencia,
                    "data_publicacao_ans": date(2026, 4, 22),
                    "versao_publicacao": f"rede_demo_{competencia}",
                    "hash_sha256": f"rede_demo_hash_{competencia}",
                    "observacao": "Demo local de rede assistencial para Sprint 11.",
                },
            )
        await session.commit()


async def seed_demo_rede() -> None:
    await limpar_registros_demo()
    await registrar_publicacoes()

    registros = [
        {
            "competencia": "202603",
            "registro_ans": "123456",
            "cd_municipio": "3550308",
            "nm_municipio": "Sao Paulo",
            "sg_uf": "SP",
            "segmento": "MEDICO",
            "tipo_prestador": "HOSPITAL",
            "qt_prestador": 32,
            "qt_especialidade_disponivel": 18,
            "fonte_publicacao": "rede_demo_202603",
        },
        {
            "competencia": "202603",
            "registro_ans": "654321",
            "cd_municipio": "3550308",
            "nm_municipio": "Sao Paulo",
            "sg_uf": "SP",
            "segmento": "ODONTO",
            "tipo_prestador": "CLINICA",
            "qt_prestador": 20,
            "qt_especialidade_disponivel": 12,
            "fonte_publicacao": "rede_demo_202603",
        },
        {
            "competencia": "202604",
            "registro_ans": "123456",
            "cd_municipio": "3106200",
            "nm_municipio": "Belo Horizonte",
            "sg_uf": "MG",
            "segmento": "MEDICO",
            "tipo_prestador": "HOSPITAL",
            "qt_prestador": 14,
            "qt_especialidade_disponivel": 9,
            "fonte_publicacao": "rede_demo_202604",
        },
        {
            "competencia": "202604",
            "registro_ans": "654321",
            "cd_municipio": "2611606",
            "nm_municipio": "Recife",
            "sg_uf": "PE",
            "segmento": "ODONTO",
            "tipo_prestador": "CLINICA",
            "qt_prestador": 17,
            "qt_especialidade_disponivel": 11,
            "fonte_publicacao": "rede_demo_202604",
        },
    ]

    await carregar_rede_assistencial_bruto(
        registros,
        arquivo_origem="rede_demo.csv",
        layout_id="layout_rede_assistencial_csv",
        layout_versao_id="layout_rede_assistencial_csv:v1",
        hash_arquivo="demo_hash_rede",
        hash_estrutura="demo_hash_estrutura_rede",
    )

    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.versao_dataset (
                    id,
                    dataset,
                    versao,
                    competencia,
                    hash_arquivo,
                    hash_sha256,
                    hash_estrutura,
                    registros,
                    status
                ) values (
                    :id,
                    'rede_assistencial',
                    :versao,
                    :competencia,
                    :hash_arquivo,
                    :hash_sha256,
                    :hash_estrutura,
                    :registros,
                    'demo_local_rede'
                )
                on conflict do nothing
                """
            ),
            {
                "id": str(uuid4()),
                "versao": (
                    "rede_assistencial_demo_v1_"
                    f"{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}"
                ),
                "competencia": "202604",
                "hash_arquivo": "demo_hash_rede",
                "hash_sha256": "demo_hash_rede",
                "hash_estrutura": "demo_hash_estrutura_rede",
                "registros": len(registros),
            },
        )
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
                on conflict do nothing
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": "dag_ingest_rede_assistencial",
                "nome_job": "seed_demo_rede",
                "fonte_ans": "demo_local",
                "status": "sucesso",
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": len(registros),
                "registro_com_falha": 0,
            },
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_rede())
