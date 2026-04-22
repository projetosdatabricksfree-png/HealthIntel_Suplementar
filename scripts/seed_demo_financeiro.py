import asyncio
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_diops_bruto,
    carregar_fip_bruto,
)
from ingestao.app.contratos_financeiros import CONTRATOS_FONTES_FINANCEIRAS

TRIMESTRES = [
    "2024T1",
    "2024T2",
    "2024T3",
    "2024T4",
    "2025T1",
    "2025T2",
    "2025T3",
    "2025T4",
]


async def limpar_registros_demo() -> None:
    async with SessionLocal() as session:
        for tabela in [
            "bruto_ans.diops_operadora_trimestral",
            "bruto_ans.fip_operadora_trimestral",
        ]:
            await session.execute(
                text(f"delete from {tabela} where _arquivo_origem like 'financeiro_demo_%'")
            )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset in ('diops', 'fip')
                    and status = 'demo_local_financeiro_v1'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.publicacao_financeira
                where versao_publicacao like 'financeiro_demo_%'
                """
            )
        )
        await session.commit()


async def registrar_publicacoes() -> None:
    async with SessionLocal() as session:
        for dataset, contrato in CONTRATOS_FONTES_FINANCEIRAS.items():
            for trimestre in TRIMESTRES:
                await session.execute(
                    text(
                        """
                        insert into plataforma.publicacao_financeira (
                            dataset,
                            trimestre,
                            data_publicacao_ans,
                            versao_publicacao,
                            hash_sha256,
                            observacao
                        ) values (
                            :dataset,
                            :trimestre,
                            :data_publicacao_ans,
                            :versao_publicacao,
                            :hash_sha256,
                            :observacao
                        )
                        on conflict (dataset, trimestre, versao_publicacao) do update set
                            data_publicacao_ans = excluded.data_publicacao_ans,
                            hash_sha256 = excluded.hash_sha256,
                            observacao = excluded.observacao
                        """
                    ),
                    {
                        "dataset": dataset,
                        "trimestre": trimestre,
                        "data_publicacao_ans": date(2026, 4, 22),
                        "versao_publicacao": f"financeiro_demo_{dataset}_v1",
                        "hash_sha256": f"demo_hash_{dataset}_{trimestre}",
                        "observacao": contrato.observacao,
                    },
                )
        await session.commit()


def _base_financeiro(registro_ans: str, idx: int) -> dict:
    if registro_ans == "123456":
        multiplicador = 1.0 + idx * 0.04
        return {
            "cnpj": "12345678000190",
            "ativo_total": round(12000000 * multiplicador, 2),
            "passivo_total": round(7800000 * multiplicador, 2),
            "patrimonio_liquido": round(4200000 * multiplicador, 2),
            "receita_total": round(5600000 * multiplicador, 2),
            "despesa_total": round(5150000 * multiplicador, 2),
            "resultado_periodo": round(450000 * multiplicador, 2),
            "provisao_tecnica": round(950000 * multiplicador, 2),
            "margem_solvencia_calculada": round(1350000 * multiplicador, 2),
            "modalidade": "medicina_de_grupo",
            "tipo_contratacao": "coletivo",
            "sinistro_total": round(2600000 * multiplicador, 2),
            "contraprestacao_total": round(3300000 * multiplicador, 2),
            "sinistralidade_bruta": round((2600000 / 3300000) + (idx * 0.01), 4),
            "ressarcimento_sus": round(130000 * multiplicador, 2),
            "evento_indenizavel": round(1800000 * multiplicador, 2),
        }
    multiplicador = 1.0 + idx * 0.05
    return {
        "cnpj": "65432198000155",
        "ativo_total": round(9800000 * multiplicador, 2),
        "passivo_total": round(7300000 * multiplicador, 2),
        "patrimonio_liquido": round(2500000 * multiplicador, 2),
        "receita_total": round(4700000 * multiplicador, 2),
        "despesa_total": round(4650000 * multiplicador, 2),
        "resultado_periodo": round(50000 * multiplicador, 2),
        "provisao_tecnica": round(810000 * multiplicador, 2),
        "margem_solvencia_calculada": round(990000 * multiplicador, 2),
        "modalidade": "cooperativa_medica",
        "tipo_contratacao": "individual",
        "sinistro_total": round(2850000 * multiplicador, 2),
        "contraprestacao_total": round(2950000 * multiplicador, 2),
        "sinistralidade_bruta": round((2850000 / 2950000) + (idx * 0.008), 4),
        "ressarcimento_sus": round(90000 * multiplicador, 2),
        "evento_indenizavel": round(1650000 * multiplicador, 2),
    }


async def seed_demo_financeiro() -> None:
    await limpar_registros_demo()
    await registrar_publicacoes()

    registros_diops: list[dict] = []
    registros_fip: list[dict] = []
    for idx, trimestre in enumerate(TRIMESTRES):
        for registro_ans in ("123456", "654321"):
            base = _base_financeiro(registro_ans, idx)
            registros_diops.append(
                {
                    "trimestre": trimestre,
                    "registro_ans": registro_ans,
                    **base,
                    "fonte_publicacao": f"financeiro_demo_diops_{trimestre}",
                }
            )
            registros_fip.append(
                {
                    "trimestre": trimestre,
                    "registro_ans": registro_ans,
                    "modalidade": base["modalidade"],
                    "tipo_contratacao": base["tipo_contratacao"],
                    "sinistro_total": base["sinistro_total"],
                    "contraprestacao_total": base["contraprestacao_total"],
                    "sinistralidade_bruta": base["sinistralidade_bruta"],
                    "ressarcimento_sus": base["ressarcimento_sus"],
                    "evento_indenizavel": base["evento_indenizavel"],
                    "fonte_publicacao": f"financeiro_demo_fip_{trimestre}",
                }
            )

    await carregar_diops_bruto(
        registros_diops,
        arquivo_origem="financeiro_demo_diops.csv",
        layout_id="layout_diops_xml",
        layout_versao_id="layout_diops_xml:v1",
        hash_arquivo="demo_hash_diops",
        hash_estrutura="demo_hash_estrutura_diops",
    )

    await carregar_fip_bruto(
        registros_fip,
        arquivo_origem="financeiro_demo_fip.csv",
        layout_id="layout_fip_csv",
        layout_versao_id="layout_fip_csv:v1",
        hash_arquivo="demo_hash_fip",
        hash_estrutura="demo_hash_estrutura_fip",
    )

    async with SessionLocal() as session:
        for dataset in ("diops", "fip"):
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
                    "dataset": dataset,
                    "versao": f"{dataset}_demo_v1_{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}",
                    "competencia": "2025T4",
                    "hash_arquivo": f"demo_hash_{dataset}",
                    "hash_sha256": f"demo_hash_{dataset}",
                    "hash_estrutura": f"demo_hash_estrutura_{dataset}",
                    "registros": 16,
                    "status": "demo_local_financeiro_v1",
                },
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_financeiro())
