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
    PremiumContratoValidadoItem,
    PremiumMdmOperadoraItem,
    PremiumMdmPrestadorItem,
    PremiumOperadora360ValidadoItem,
    PremiumQualityDatasetItem,
    PremiumSubfaturaValidadaItem,
    PremiumTissProcedimentoTussValidadoItem,
    PremiumTussProcedimentoItem,
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
    "tiss_procedimento_tuss_validado": {
        "tabela": "api_ans.api_premium_tiss_procedimento_tuss_validado",
        "fonte": "api_premium_tiss_procedimento_tuss_validado",
        "competencia": "trimestre",
        "ordenacao": "trimestre desc, registro_ans, cd_procedimento_tuss",
        "schema": PremiumTissProcedimentoTussValidadoItem,
        "filtros": {
            "trimestre": "trimestre",
            "registro_ans": "registro_ans",
            "cd_procedimento_tuss": "cd_procedimento_tuss",
            "grupo_desc": "grupo_desc",
        },
    },
    "tuss_procedimento": {
        "tabela": "api_ans.api_premium_tuss_procedimento",
        "fonte": "api_premium_tuss_procedimento",
        "competencia": None,
        "ordenacao": "codigo_tuss, versao_tuss",
        "schema": PremiumTussProcedimentoItem,
        "filtros": {
            "codigo_tuss": "codigo_tuss",
            "versao_tuss": "versao_tuss",
            "grupo": "grupo",
            "is_tuss_vigente": "is_tuss_vigente",
        },
    },
    "mdm_operadora": {
        "tabela": "api_ans.api_premium_mdm_operadora",
        "fonte": "api_premium_mdm_operadora",
        "competencia": None,
        "ordenacao": "operadora_master_id",
        "schema": PremiumMdmOperadoraItem,
        "filtros": {
            "registro_ans_canonico": "registro_ans_canonico",
            "status_mdm": "status_mdm",
            "uf_canonica": "uf_canonica",
        },
    },
    "mdm_prestador": {
        "tabela": "api_ans.api_premium_mdm_prestador",
        "fonte": "api_premium_mdm_prestador",
        "competencia": None,
        "ordenacao": "prestador_master_id",
        "schema": PremiumMdmPrestadorItem,
        "filtros": {
            "cnes_canonico": "cnes_canonico",
            "status_mdm": "status_mdm",
            "uf_canonica": "uf_canonica",
        },
    },
    "contrato_validado": {
        "tabela": "api_ans.api_premium_contrato_validado",
        "fonte": "api_premium_contrato_validado",
        "competencia": None,
        "ordenacao": "contrato_master_id",
        "schema": PremiumContratoValidadoItem,
        "filtros": {
            "tenant_id": "tenant_id",
            "numero_contrato_normalizado": "numero_contrato_normalizado",
            "status_contrato": "status_contrato",
            "registro_ans_canonico": "registro_ans_canonico",
        },
        "tenant_obrigatorio": True,
    },
    "subfatura_validada": {
        "tabela": "api_ans.api_premium_subfatura_validada",
        "fonte": "api_premium_subfatura_validada",
        "competencia": "competencia",
        "ordenacao": "competencia desc, subfatura_master_id",
        "schema": PremiumSubfaturaValidadaItem,
        "filtros": {
            "tenant_id": "tenant_id",
            "competencia": "competencia",
            "contrato_master_id": "contrato_master_id",
            "status_subfatura": "status_subfatura",
        },
        "tenant_obrigatorio": True,
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
    if dataset == "tiss_procedimento_tuss_validado":
        if normalizados.get("registro_ans"):
            normalizados["registro_ans"] = str(normalizados["registro_ans"]).zfill(6)
        if normalizados.get("trimestre"):
            normalizados["trimestre"] = str(normalizados["trimestre"]).strip()
    if dataset == "mdm_operadora":
        if normalizados.get("registro_ans_canonico"):
            normalizados["registro_ans_canonico"] = str(
                normalizados["registro_ans_canonico"]
            ).zfill(6)
        if normalizados.get("uf_canonica"):
            normalizados["uf_canonica"] = str(normalizados["uf_canonica"]).upper()
        if normalizados.get("status_mdm"):
            normalizados["status_mdm"] = str(normalizados["status_mdm"]).upper()
    if dataset == "mdm_prestador":
        if normalizados.get("cnpj_canonico"):
            normalizados["cnpj_canonico"] = "".join(
                filter(str.isdigit, str(normalizados["cnpj_canonico"]))
            ).zfill(14)
        if normalizados.get("uf_canonica"):
            normalizados["uf_canonica"] = str(normalizados["uf_canonica"]).upper()
        if normalizados.get("status_mdm"):
            normalizados["status_mdm"] = str(normalizados["status_mdm"]).upper()
    if dataset in ("contrato_validado", "subfatura_validada"):
        if normalizados.get("registro_ans_canonico"):
            normalizados["registro_ans_canonico"] = str(
                normalizados["registro_ans_canonico"]
            ).zfill(6)
        if normalizados.get("status_contrato"):
            normalizados["status_contrato"] = str(normalizados["status_contrato"]).upper()
        if normalizados.get("status_subfatura"):
            normalizados["status_subfatura"] = str(normalizados["status_subfatura"]).upper()
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
        # Para booleanos, compara diretamente
        if isinstance(valor, bool):
            where_clauses.append(f"{coluna} = :{chave}")
        else:
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
    tenant_id: str | None = None,
) -> dict:
    if dataset not in PREMIUM_DATASETS:
        raise ValueError(f"Dataset premium nao suportado: {dataset}")

    pagina = max(pagina, 1)
    limite = min(max(limite, 1), 100)
    offset = (pagina - 1) * limite
    cfg = PREMIUM_DATASETS[dataset]

    # Tenant obrigatório para datasets privados
    if cfg.get("tenant_obrigatorio"):
        if not tenant_id:
            raise ValueError("tenant_id obrigatorio para dataset privado")
        filtros = dict(filtros or {})
        filtros["tenant_id"] = tenant_id

    filtros_normalizados = _normalizar_filtros(dataset, filtros)
    cache_key = (
        f"premium:{dataset}:{pagina}:{limite}:"
        f"{json.dumps(filtros_normalizados, sort_keys=True)}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

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

    # Competência: usa o campo configurado se disponível
    campo_competencia = cfg.get("competencia")
    competencia = (
        str(filtros_normalizados.get(campo_competencia, ""))
        if campo_competencia
        else "todas"
    ) or "todas"

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