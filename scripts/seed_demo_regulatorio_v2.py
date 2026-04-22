import asyncio
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_portabilidade_bruto,
    carregar_prudencial_bruto,
    carregar_regime_especial_bruto,
    carregar_taxa_resolutividade_bruto,
)
from ingestao.app.contratos_regulatorios_v2 import CONTRATOS_FONTES_REGULATORIAS_V2


async def limpar_registros_demo() -> None:
    async with SessionLocal() as session:
        for tabela in [
            "bruto_ans.regime_especial_operadora_trimestral",
            "bruto_ans.prudencial_operadora_trimestral",
            "bruto_ans.portabilidade_operadora_mensal",
            "bruto_ans.taxa_resolutividade_operadora_trimestral",
        ]:
            await session.execute(
                text(f"delete from {tabela} where _arquivo_origem like 'regulatorio_v2_demo_%'")
            )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset in (
                    'regime_especial',
                    'prudencial',
                    'portabilidade',
                    'taxa_resolutividade',
                    'score_regulatorio'
                )
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.publicacao_regulatoria
                where status = 'demo_local_regulatorio_v2'
                """
            )
        )
        await session.commit()


async def registrar_publicacoes() -> None:
    async with SessionLocal() as session:
        for dataset, contrato in CONTRATOS_FONTES_REGULATORIAS_V2.items():
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
                {
                    "id": str(uuid4()),
                    "dataset": dataset,
                    "competencia": "2025T4" if contrato.cadencia == "trimestral" else "202603",
                    "versao_publicacao": f"{dataset}_demo_v1",
                    "titulo_publicacao": contrato.nome,
                    "fonte_oficial": "ANS",
                    "url_publicacao": contrato.url_publicacao,
                    "formato_publicacao": contrato.formato_publicacao,
                    "publicado_em": date(2026, 4, 22),
                    "hash_publicacao": f"demo_hash_{dataset}",
                    "status": "demo_local_regulatorio_v2",
                    "observacao": contrato.observacao,
                },
            )
        await session.commit()


async def seed_demo_regulatorio_v2() -> None:
    await limpar_registros_demo()

    await carregar_regime_especial_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "tipo_regime": "direcao_fiscal",
                "data_inicio": date(2025, 10, 1),
                "data_fim": None,
                "descricao": "Operadora em monitoramento por desequilibrio assistencial.",
                "fonte_publicacao": "regulatorio_v2_demo_regime_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "tipo_regime": "direcao_tecnica",
                "data_inicio": date(2025, 7, 1),
                "data_fim": date(2025, 12, 31),
                "descricao": "Regime encerrado com plano de saneamento.",
                "fonte_publicacao": "regulatorio_v2_demo_regime_2025t4",
            },
        ],
        arquivo_origem="regulatorio_v2_demo_regime_especial.csv",
        layout_id="layout_regime_especial_csv",
        layout_versao_id="layout_regime_especial_csv:v1",
        hash_arquivo="demo_hash_regime_especial",
        hash_estrutura="demo_hash_estrutura_regime_especial",
    )

    await carregar_prudencial_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "margem_solvencia": 1200000.00,
                "capital_minimo_requerido": 1000000.00,
                "capital_disponivel": 1350000.00,
                "indice_liquidez": 1.35,
                "situacao_prudencial": "adequada",
                "fonte_publicacao": "regulatorio_v2_demo_prudencial_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "margem_solvencia": 800000.00,
                "capital_minimo_requerido": 1000000.00,
                "capital_disponivel": 780000.00,
                "indice_liquidez": 0.78,
                "situacao_prudencial": "inadequada",
                "fonte_publicacao": "regulatorio_v2_demo_prudencial_2025t4",
            },
        ],
        arquivo_origem="regulatorio_v2_demo_prudencial.csv",
        layout_id="layout_prudencial_csv",
        layout_versao_id="layout_prudencial_csv:v1",
        hash_arquivo="demo_hash_prudencial",
        hash_estrutura="demo_hash_estrutura_prudencial",
    )

    await carregar_portabilidade_bruto(
        [
            {
                "competencia": "202603",
                "registro_ans": "123456",
                "modalidade": "MEDICINA_DE_GRUPO",
                "tipo_contratacao": "COLETIVO",
                "qt_portabilidade_entrada": 10,
                "qt_portabilidade_saida": 3,
                "fonte_publicacao": "regulatorio_v2_demo_portabilidade_202603",
            },
            {
                "competencia": "202603",
                "registro_ans": "654321",
                "modalidade": "COOPERATIVA_MEDICA",
                "tipo_contratacao": "INDIVIDUAL",
                "qt_portabilidade_entrada": 4,
                "qt_portabilidade_saida": 1,
                "fonte_publicacao": "regulatorio_v2_demo_portabilidade_202603",
            },
        ],
        arquivo_origem="regulatorio_v2_demo_portabilidade_202603.csv",
        layout_id="layout_portabilidade_csv",
        layout_versao_id="layout_portabilidade_csv:v1",
        hash_arquivo="demo_hash_portabilidade",
        hash_estrutura="demo_hash_estrutura_portabilidade",
    )

    await carregar_taxa_resolutividade_bruto(
        [
            {
                "trimestre": "2025T4",
                "registro_ans": "123456",
                "modalidade": "MEDICINA_DE_GRUPO",
                "taxa_resolutividade": 92.5,
                "n_reclamacao_resolvida": 27,
                "n_reclamacao_total": 30,
                "fonte_publicacao": "regulatorio_v2_demo_tr_2025t4",
            },
            {
                "trimestre": "2025T4",
                "registro_ans": "654321",
                "modalidade": "COOPERATIVA_MEDICA",
                "taxa_resolutividade": 74.0,
                "n_reclamacao_resolvida": 18,
                "n_reclamacao_total": 24,
                "fonte_publicacao": "regulatorio_v2_demo_tr_2025t4",
            },
        ],
        arquivo_origem="regulatorio_v2_demo_tr_2025t4.csv",
        layout_id="layout_taxa_resolutividade_csv",
        layout_versao_id="layout_taxa_resolutividade_csv:v1",
        hash_arquivo="demo_hash_taxa_resolutividade",
        hash_estrutura="demo_hash_estrutura_taxa_resolutividade",
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
                    :dataset,
                    :versao,
                    :competencia,
                    :hash_arquivo,
                    :hash_sha256,
                    :hash_estrutura,
                    :registros,
                    :status
                )
                on conflict do nothing
                """
            ),
            {
                "id": str(uuid4()),
                "dataset": "score_regulatorio",
                "versao": "score_regulatorio_demo_v1",
                "competencia": "202603",
                "hash_arquivo": "demo_hash_score_regulatorio",
                "hash_sha256": "demo_hash_score_regulatorio",
                "hash_estrutura": "demo_hash_estrutura_score_regulatorio",
                "registros": 2,
                "status": "sucesso",
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
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": "dag_mestre_trimestral_regulatorio_v2",
                "nome_job": "seed_demo_regulatorio_v2",
                "fonte_ans": "demo_regulatorio_v2",
                "status": "sucesso",
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": 8,
                "registro_com_falha": 0,
            },
        )

        await registrar_publicacoes()
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_regulatorio_v2())
