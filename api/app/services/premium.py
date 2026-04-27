from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.premium import (
    PremiumCnesEstabelecimentoValidadoItem,
    PremiumOperadora360ValidadoItem,
    PremiumQualityDatasetItem,
)

settings = get_settings()


PREMIUM_DATASETS: dict[str, dict[str, Any]] = {
    "operadora_360_validado": {
        "tabela": "api_ans.api_premium_operadora_360_validado",
        "fonte": "api_premium_operadora_360_validado",
        "competencia": "competencia",
        "ordenacao": "competencia desc, registro_ans",
        "schema": PremiumOperadora360ValidadoItem,
        "filtros": {
            "competencia": "competencia",
            "registro_ans": "registro_ans",
            "uf": "uf",
            "modalidade": "modalidade",
        },
    },
    "cnes_estabelecimento_validado": {
        "tabela": "api_ans.api_premium_cnes_estabelecimento_validado",
        "fonte": "api_premium_cnes_estabelecimento_validado",
        "competencia": "competencia",
        "ordenacao": "competencia desc, cnes_normalizado",
        "schema": PremiumCnesEstabelecimentoValidadoItem,
        "filtros": {
            "competencia": "competencia",
            "cnes": "cnes_normalizado",
            "cd_municipio": "cd_municipio",
            "sg_uf": "sg_uf",
            "tipo_unidade": "tipo_unidade",
        },
    },
    "quality_dataset": {
        "tabela": "api_ans.api_premium_quality_dataset",
        "fonte": "api_premium_quality_dataset",
        "competencia": None,
        "ordenacao": "fonte_documento, documento_quality_status",
        "schema": PremiumQualityDatasetItem,
        "filtros": {
            "fonte_documento": "fonte_documento",
            "documento_quality_status": "documento_quality_status",
        },
    },
}


async def _obter_cache(chave: str) -> dict | None:
    try:
        valor = await redis_client.get(chave)
    except Exception:
        return None
    if not valor:
        return None
    return json.loads(valor)


async def _salvar_cache(chave: str, payload: dict) -> None:
    try:
        await redis_client.set(
            chave,
            json.dumps(payload, default=str),
            ex=settings.app_cache_ttl_segundos,
        )
    except Exception:
        return


def _normalizar_filtros(dataset: str, filtros: dict[str, object] | None) -> dict[str, object]:
    normalizados = dict(filtros or {})
    if dataset == "operadora_360_validado":
        if normalizados.get("registro_ans"):
            normalizados["registro_ans"] = str(normalizados["registro_ans"]).zfill(6)
        if normalizados.get("uf"):
            normalizados["uf"] = str(normalizados["uf"]).upper()
        if normalizados.get("modalidade"):
            normalizados["modalidade"] = str(normalizados["modalidade"]).upper()
    if dataset == "cnes_estabelecimento_validado":
        if normalizados.get("cnes"):
            normalizados["cnes"] = "".join(filter(str.isdigit, str(normalizados["cnes"]))).zfill(7)
        if normalizados.get("cd_municipio"):
            normalizados["cd_municipio"] = "".join(
                filter(str.isdigit, str(normalizados["cd_municipio"]))
            ).zfill(7)
        if normalizados.get("sg_uf"):
            normalizados["sg_uf"] = str(normalizados["sg_uf"]).upper()
    if dataset == "quality_dataset" and normalizados.get("documento_quality_status"):
        normalizados["documento_quality_status"] = str(
            normalizados["documento_quality_status"]
        ).upper()
    return normalizados


def _montar_where(cfg: dict[str, Any], filtros: dict[str, object]) -> tuple[str, dict[str, object]]:
    filtros_permitidos: dict[str, str] = cfg["filtros"]
    params: dict[str, object] = {}
    where_clauses: list[str] = []
    for chave, valor in filtros.items():
        if valor is None or chave not in filtros_permitidos:
            continue
        coluna = filtros_permitidos[chave]
        where_clauses.append(f"{coluna}::text = :{chave}")
        params[chave] = valor
    where_clause = " where " + " and ".join(where_clauses) if where_clauses else ""
    return where_clause, params


async def buscar_premium(
    dataset: str,
    *,
    filtros: dict[str, object] | None = None,
    pagina: int = 1,
    limite: int = 50,
) -> dict:
    if dataset not in PREMIUM_DATASETS:
        raise ValueError(f"Dataset premium nao suportado: {dataset}")

    pagina = max(pagina, 1)
    limite = min(max(limite, 1), 100)
    offset = (pagina - 1) * limite
    filtros_normalizados = _normalizar_filtros(dataset, filtros)
    cache_key = (
        f"premium:{dataset}:{pagina}:{limite}:"
        f"{json.dumps(filtros_normalizados, sort_keys=True)}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    cfg = PREMIUM_DATASETS[dataset]
    where_clause, params = _montar_where(cfg, filtros_normalizados)
    params.update({"limit": limite, "offset": offset})
    item_schema: type[BaseModel] = cfg["schema"]

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from {cfg['tabela']} {where_clause}"),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select *
                from {cfg["tabela"]}
                {where_clause}
                order by {cfg["ordenacao"]}
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = [item_schema(**dict(row)).model_dump() for row in result.mappings().all()]

    competencia = str(filtros_normalizados.get("competencia") or "todas")
    payload = {
        "dados": rows,
        "meta": {
            "fonte": cfg["fonte"],
            "competencia": competencia,
            "versao_dataset": f"{dataset}_v1",
            "total": total,
            "pagina": pagina,
            "por_pagina": limite,
            "cache": "miss",
        },
    }
    await _salvar_cache(cache_key, payload)
    return payload
