import asyncio
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_glosa_bruto,
    carregar_vda_bruto,
)
from ingestao.app.contratos_financeiros import CONTRATOS_FONTES_FINANCEIRAS

MESES = [
    "202602",
    "202603",
]


async def limpar_registros_demo() -> None:
    async with SessionLocal() as session:
        for tabela in [
            "bruto_ans.vda_operadora_mensal",
            "bruto_ans.glosa_operadora_mensal",
        ]:
            await session.execute(
                text(f"delete from {tabela} where _arquivo_origem like 'financeiro_v2_demo_%'")
            )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset in ('vda', 'glosa', 'score_v2', 'financeiro_v2')
                    and status = 'demo_local_financeiro_v2'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.publicacao_financeira_v2
                where versao_publicacao like 'financeiro_v2_demo_%'
                """
            )
        )
        await session.commit()


async def registrar_publicacoes() -> None:
    async with SessionLocal() as session:
        for dataset, contrato in CONTRATOS_FONTES_FINANCEIRAS.items():
            if dataset not in {"vda", "glosa"}:
                continue
            for competencia in MESES:
                await session.execute(
                    text(
                        """
                        insert into plataforma.publicacao_financeira_v2 (
                            dataset,
                            competencia,
                            data_publicacao_ans,
                            versao_publicacao,
                            hash_sha256,
                            observacao
                        ) values (
                            :dataset,
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
                        "dataset": dataset,
                        "competencia": competencia,
                        "data_publicacao_ans": date(2026, 4, 22),
                        "versao_publicacao": f"financeiro_v2_demo_{dataset}_v1",
                        "hash_sha256": f"demo_hash_{dataset}_{competencia}",
                        "observacao": contrato.observacao,
                    },
                )
        await session.commit()


def _base_vda(registro_ans: str, idx: int) -> dict:
    if registro_ans == "123456":
        saldo = 0 if idx == 0 else 3200 + (idx * 250)
        valor_devido = 18000 + (idx * 900)
        valor_pago = valor_devido - saldo
        return {
            "valor_devido": round(valor_devido, 2),
            "valor_pago": round(valor_pago, 2),
            "saldo_devedor": round(saldo, 2),
            "situacao_cobranca": "inadimplente" if saldo > 0 else "adimplente",
            "data_vencimento": date(2026, 4, 10),
        }
    saldo = 1200 + (idx * 150)
    valor_devido = 14500 + (idx * 650)
    valor_pago = valor_devido - saldo
    return {
        "valor_devido": round(valor_devido, 2),
        "valor_pago": round(valor_pago, 2),
        "saldo_devedor": round(saldo, 2),
        "situacao_cobranca": "parcelado",
        "data_vencimento": date(2026, 4, 12),
    }


def _base_glosa(registro_ans: str, idx: int, tipo_glosa: str) -> dict:
    if registro_ans == "123456":
        fator = 0.11 if tipo_glosa == "assistencial" else 0.04
        if idx == 1 and tipo_glosa == "assistencial":
            fator = 0.18
    else:
        fator = 0.08 if tipo_glosa == "assistencial" else 0.03
        if idx == 1 and tipo_glosa == "assistencial":
            fator = 0.19
    valor_faturado = 50000 + (idx * 1800)
    valor_glosa = round(valor_faturado * fator, 2)
    return {
        "qt_glosa": 8 + idx,
        "valor_glosa": valor_glosa,
        "valor_faturado": round(valor_faturado, 2),
    }


async def seed_demo_financeiro_v2() -> None:
    await limpar_registros_demo()
    await registrar_publicacoes()

    registros_vda: list[dict] = []
    registros_glosa: list[dict] = []
    for idx, competencia in enumerate(MESES):
        for registro_ans in ("123456", "654321"):
            base_vda = _base_vda(registro_ans, idx)
            registros_vda.append(
                {
                    "competencia": competencia,
                    "registro_ans": registro_ans,
                    **base_vda,
                    "fonte_publicacao": f"financeiro_v2_demo_vda_{competencia}",
                }
            )
            for tipo_glosa in ("assistencial", "administrativa"):
                base_glosa = _base_glosa(registro_ans, idx, tipo_glosa)
                registros_glosa.append(
                    {
                        "competencia": competencia,
                        "registro_ans": registro_ans,
                        "tipo_glosa": tipo_glosa,
                        **base_glosa,
                        "fonte_publicacao": f"financeiro_v2_demo_glosa_{competencia}",
                    }
                )

    await carregar_vda_bruto(
        registros_vda,
        arquivo_origem="financeiro_v2_demo_vda.csv",
        layout_id="layout_vda_csv",
        layout_versao_id="layout_vda_csv:v1",
        hash_arquivo="demo_hash_vda",
        hash_estrutura="demo_hash_estrutura_vda",
    )

    await carregar_glosa_bruto(
        registros_glosa,
        arquivo_origem="financeiro_v2_demo_glosa.csv",
        layout_id="layout_glosa_csv",
        layout_versao_id="layout_glosa_csv:v1",
        hash_arquivo="demo_hash_glosa",
        hash_estrutura="demo_hash_estrutura_glosa",
    )

    async with SessionLocal() as session:
        for dataset in ("vda", "glosa", "score_v2", "financeiro_v2"):
            registros = {
                "vda": len(registros_vda),
                "glosa": len(registros_glosa),
                "score_v2": 4,
                "financeiro_v2": len(registros_vda),
            }[dataset]
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
                    "competencia": "202603",
                    "hash_arquivo": f"demo_hash_{dataset}",
                    "hash_sha256": f"demo_hash_{dataset}",
                    "hash_estrutura": f"demo_hash_estrutura_{dataset}",
                    "registros": registros,
                    "status": "demo_local_financeiro_v2",
                },
            )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo_financeiro_v2())
