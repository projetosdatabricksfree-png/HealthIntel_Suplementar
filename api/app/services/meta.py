from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.schemas.meta import (
    DatasetMetaResponse,
    MetaEnvelope,
    PipelineMetaResponse,
    VersaoDatasetResponse,
)

CATALOGO_DATASETS = {
    "cadop": {
        "descricao": "Cadastro mestre de operadoras.",
        "cadencia": "continua",
        "status": "ativo",
    },
    "sib_operadora": {
        "descricao": "Beneficiarios SIB consolidados por operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "sib_municipio": {
        "descricao": "Beneficiarios SIB consolidados por municipio, operadora e competencia.",
        "cadencia": "mensal",
        "status": "ativo",
    },
    "igr": {
        "descricao": "IGR trimestral por operadora com metadados regulatorios.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "nip": {
        "descricao": "Demandas NIP e TIR/TR trimestrais por operadora.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
    "rn623_lista": {
        "descricao": "Listas trimestrais de excelencia e reducao da RN 623/2024.",
        "cadencia": "trimestral",
        "status": "ativo",
    },
}


def _meta_padrao(total: int) -> dict:
    return MetaEnvelope(
        competencia_referencia="atual",
        versao_dataset="meta_v1",
        total=total,
        pagina=1,
        por_pagina=total,
    ).model_dump()


async def listar_datasets() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select dataset, max(carregado_em) as carregado_em
                from plataforma.versao_dataset
                group by dataset
                order by dataset
                """
            )
        )
        datasets = []
        for row in result.mappings():
            definicao = CATALOGO_DATASETS.get(
                row["dataset"],
                {
                    "descricao": "Dataset catalogado na plataforma.",
                    "cadencia": "sob demanda",
                    "status": "ativo",
                },
            )
            datasets.append(
                DatasetMetaResponse(
                    nome=row["dataset"],
                    descricao=definicao["descricao"],
                    cadencia=definicao["cadencia"],
                    status=definicao["status"],
                ).model_dump()
            )
    return {"dados": datasets, "meta": _meta_padrao(len(datasets))}


async def listar_versoes() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    dataset,
                    versao,
                    carregado_em,
                    competencia,
                    status
                from plataforma.versao_dataset
                order by carregado_em desc
                limit 20
                """
            )
        )
        dados = [
            VersaoDatasetResponse(
                dataset=row["dataset"],
                versao=row["versao"],
                carregado_em=row["carregado_em"].isoformat(),
                competencia=row["competencia"],
                status=row["status"],
            ).model_dump()
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}


async def listar_pipeline() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    dag_id,
                    status,
                    iniciado_em,
                    finalizado_em
                from plataforma.job
                order by iniciado_em desc
                limit 20
                """
            )
        )
        dados = [
            PipelineMetaResponse(
                dag_id=row["dag_id"],
                status=row["status"],
                iniciado_em=row["iniciado_em"].isoformat(),
                finalizado_em=row["finalizado_em"].isoformat() if row["finalizado_em"] else None,
            ).model_dump()
            for row in result.mappings()
        ]
    return {"dados": dados, "meta": _meta_padrao(len(dados))}
