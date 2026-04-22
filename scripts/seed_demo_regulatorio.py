import asyncio
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_igr_bruto,
    carregar_nip_bruto,
    carregar_rn623_lista_bruto,
)
from ingestao.app.contratos_regulatorios import CONTRATOS_FONTES_REGULATORIAS


async def limpar_registros_demo() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                delete from bruto_ans.rn623_lista_operadora_trimestral
                where _arquivo_origem like 'regulatorio_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from bruto_ans.nip_operadora_trimestral
                where _arquivo_origem like 'regulatorio_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from bruto_ans.igr_operadora_trimestral
                where _arquivo_origem like 'regulatorio_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.publicacao_regulatoria
                where status = 'demo_local'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset in ('igr', 'nip', 'rn623_lista')
                  and status = 'sucesso'
                """
            )
        )
        await session.commit()


async def registrar_publicacoes() -> None:
    publicacoes = [
        {
            "dataset": "igr",
            "competencia": "2025T4",
            "versao_publicacao": "igr_2025t4_v1",
            "titulo_publicacao": "Painel IGR - historico trimestral",
            "url_publicacao": CONTRATOS_FONTES_REGULATORIAS["igr"].url_publicacao,
            "fonte_oficial": "ANS",
            "formato_publicacao": "painel_powerbi",
            "publicado_em": date(2025, 9, 24),
            "hash_publicacao": "demo_hash_igr_2025t4",
            "status": "demo_local",
            "observacao": CONTRATOS_FONTES_REGULATORIAS["igr"].observacao,
        },
        {
            "dataset": "nip",
            "competencia": "2025T4",
            "versao_publicacao": "nip_2025t4_v1",
            "titulo_publicacao": "Painel Demandas NIP/TIR - historico trimestral",
            "url_publicacao": CONTRATOS_FONTES_REGULATORIAS["nip"].url_publicacao,
            "fonte_oficial": "ANS",
            "formato_publicacao": "painel_powerbi",
            "publicado_em": date(2025, 9, 24),
            "hash_publicacao": "demo_hash_nip_2025t4",
            "status": "demo_local",
            "observacao": CONTRATOS_FONTES_REGULATORIAS["nip"].observacao,
        },
        {
            "dataset": "rn623_lista",
            "competencia": "2025T4",
            "versao_publicacao": "rn623_2025t4_v1",
            "titulo_publicacao": "Listas de Excelencia e Reducao - 4T2025",
            "url_publicacao": CONTRATOS_FONTES_REGULATORIAS["rn623_lista"].url_publicacao,
            "fonte_oficial": "ANS",
            "formato_publicacao": "html_pdf_painel",
            "publicado_em": date(2026, 3, 13),
            "hash_publicacao": "demo_hash_rn623_2025t4",
            "status": "demo_local",
            "observacao": CONTRATOS_FONTES_REGULATORIAS["rn623_lista"].observacao,
        },
    ]

    async with SessionLocal() as session:
        for publicacao in publicacoes:
            await session.execute(
                text(
                    """
                    insert into plataforma.publicacao_regulatoria (
                        id,
                        dataset,
                        competencia,
                        versao_publicacao,
                        titulo_publicacao,
                        fonte_oficial,
                        url_publicacao,
                        formato_publicacao,
                        publicado_em,
                        hash_publicacao,
                        status,
                        observacao
                    ) values (
                        :id,
                        :dataset,
                        :competencia,
                        :versao_publicacao,
                        :titulo_publicacao,
                        :fonte_oficial,
                        :url_publicacao,
                        :formato_publicacao,
                        :publicado_em,
                        :hash_publicacao,
                        :status,
                        :observacao
                    )
                    on conflict (dataset, competencia, versao_publicacao) do update set
                        titulo_publicacao = excluded.titulo_publicacao,
                        url_publicacao = excluded.url_publicacao,
                        formato_publicacao = excluded.formato_publicacao,
                        publicado_em = excluded.publicado_em,
                        hash_publicacao = excluded.hash_publicacao,
                        status = excluded.status,
                        observacao = excluded.observacao
                    """
                ),
                {"id": str(uuid4()), **publicacao},
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
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": "dag_ingest_reclamacoes_regulatorias",
                "nome_job": "seed_demo_regulatorio",
                "fonte_ans": "demo_regulatorio",
                "status": "sucesso",
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": 9,
                "registro_com_falha": 0,
            },
        )
        await session.commit()


async def seed_demo_regulatorio() -> None:
    await limpar_registros_demo()

    await carregar_igr_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "modalidade": "MEDICO_HOSPITALAR",
                "porte": "GRANDE",
                "total_reclamacoes": 30,
                "beneficiarios": 120000,
                "igr": 2.10,
                "meta_igr": 2.40,
                "atingiu_meta": True,
                "fonte_publicacao": "painel_igr_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "modalidade": "MEDICO_HOSPITALAR",
                "porte": "MEDIO",
                "total_reclamacoes": 26,
                "beneficiarios": 80000,
                "igr": 3.25,
                "meta_igr": 2.40,
                "atingiu_meta": False,
                "fonte_publicacao": "painel_igr_2025t4",
            },
        ],
        arquivo_origem="regulatorio_demo_igr_2025t4.csv",
        layout_id="layout_igr_csv",
        layout_versao_id="layout_igr_csv:v1",
        hash_arquivo="demo_hash_arquivo_igr_2025t4",
        hash_estrutura="demo_hash_estrutura_igr_v1",
    )

    await carregar_nip_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "modalidade": "MEDICO_HOSPITALAR",
                "demandas_nip": 30,
                "demandas_resolvidas": 27,
                "beneficiarios": 120000,
                "taxa_intermediacao_resolvida": 90.0,
                "taxa_resolutividade": 92.5,
                "fonte_publicacao": "painel_nip_tir_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "modalidade": "MEDICO_HOSPITALAR",
                "demandas_nip": 26,
                "demandas_resolvidas": 18,
                "beneficiarios": 80000,
                "taxa_intermediacao_resolvida": 69.2,
                "taxa_resolutividade": 74.0,
                "fonte_publicacao": "painel_nip_tir_2025t4",
            },
        ],
        arquivo_origem="regulatorio_demo_nip_2025t4.csv",
        layout_id="layout_nip_csv",
        layout_versao_id="layout_nip_csv:v1",
        hash_arquivo="demo_hash_arquivo_nip_2025t4",
        hash_estrutura="demo_hash_estrutura_nip_v1",
    )

    await carregar_rn623_lista_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "modalidade": "MEDICO_HOSPITALAR",
                "tipo_lista": "excelencia",
                "total_nip": 30,
                "beneficiarios": 120000,
                "igr": 2.10,
                "meta_igr": 2.40,
                "elegivel": True,
                "observacao": "Operadora enquadrada na lista de excelencia do 4T2025.",
                "fonte_publicacao": "rn623_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "modalidade": "MEDICO_HOSPITALAR",
                "tipo_lista": "reducao",
                "total_nip": 26,
                "beneficiarios": 80000,
                "igr": 3.25,
                "meta_igr": 2.40,
                "elegivel": True,
                "observacao": "Operadora com reducao do IGR em dois trimestres consecutivos.",
                "fonte_publicacao": "rn623_2025t4",
            },
        ],
        arquivo_origem="regulatorio_demo_rn623_2025t4.csv",
        layout_id="layout_rn623_lista_csv",
        layout_versao_id="layout_rn623_lista_csv:v1",
        hash_arquivo="demo_hash_arquivo_rn623_2025t4",
        hash_estrutura="demo_hash_estrutura_rn623_v1",
    )

    await registrar_publicacoes()


if __name__ == "__main__":
    asyncio.run(seed_demo_regulatorio())
