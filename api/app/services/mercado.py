from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.redis_client import redis_client
from api.app.database import SessionLocal
from api.app.schemas.mercado import MercadoResumoResponse, VazioAssistencialResponse
from api.app.schemas.meta import MetaEnvelope

settings = get_settings()


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
        await redis_client.set(chave, json.dumps(payload), ex=settings.app_cache_ttl_segundos)
    except Exception:
        return


async def listar_mercado_municipio(
    *,
    uf: str | None = None,
    competencia: str | None = None,
    segmento: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"mercado:{uf or 'all'}:{competencia or 'latest'}:"
        f"{segmento or 'all'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if uf:
        filtros.append("sg_uf = :uf")
        params["uf"] = uf.upper()
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = competencia
    if segmento:
        filtros.append("segmento = :segmento")
        params["segmento"] = segmento.upper()
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_market_share_mensal
                {where_clause}
                """
            ),
            params,
        )
        total = int(total_result.scalar_one())

        result = await session.execute(
            text(
                f"""
                select
                    cd_municipio,
                    nm_municipio,
                    sg_uf,
                    nm_regiao,
                    segmento,
                    competencia,
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    beneficiario_total,
                    market_share_pct,
                    hhi_municipio,
                    versao_dataset
                from api_ans.api_market_share_mensal
                {where_clause}
                order by competencia desc, hhi_municipio desc, market_share_pct desc, nm_municipio
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        competencia_referencia = rows[0]["competencia"] if rows else (competencia or "atual")

    dados = [MercadoResumoResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=competencia_referencia,
            versao_dataset="market_share_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_vazios_assistenciais(
    *,
    uf: str | None = None,
    segmento: str | None = None,
    competencia: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"vazio:{uf or 'all'}:{segmento or 'all'}:"
        f"{competencia or 'latest'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if uf:
        filtros.append("sg_uf = :uf")
        params["uf"] = uf.upper()
    if segmento:
        filtros.append("segmento = :segmento")
        params["segmento"] = segmento.upper()
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = competencia
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_vazio_assistencial
                {where_clause}
                """
            ),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    cd_municipio,
                    nm_municipio,
                    sg_uf,
                    nm_regiao,
                    competencia,
                    segmento,
                    qt_operadora_presente,
                    qt_operadora_sem_cobertura,
                    qt_operadora_total,
                    pct_operadoras_com_cobertura,
                    pct_operadoras_sem_cobertura,
                    vazio_total,
                    vazio_parcial,
                    versao_dataset
                from api_ans.api_vazio_assistencial
                {where_clause}
                order by competencia desc, vazio_total desc,
                    pct_operadoras_sem_cobertura desc, nm_municipio
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        competencia_referencia = rows[0]["competencia"] if rows else (competencia or "atual")

    dados = [VazioAssistencialResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=competencia_referencia,
            versao_dataset="vazio_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload
