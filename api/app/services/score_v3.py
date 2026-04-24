from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.score_v3 import ScoreV3Item

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
        await redis_client.set(
            chave,
            json.dumps(payload, default=str),
            ex=settings.app_cache_ttl_segundos,
        )
    except Exception:
        return


async def buscar_score_v3_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
) -> dict:
    registro_ans = registro_ans.zfill(6)
    cache_key = f"score_v3:{registro_ans}:{competencia or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"registro_ans": registro_ans}
    filtro_competencia = ""
    if competencia:
        filtro_competencia = "and competencia_id = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    operadora_id,
                    competencia_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    trimestre_financeiro,
                    score_core,
                    score_regulatorio,
                    score_financeiro,
                    score_rede,
                    score_estrutural,
                    score_completo,
                    score_v3_final,
                    versao_metodologia
                from api_ans.api_score_v3_operadora_mensal
                where registro_ans = :registro_ans
                {filtro_competencia}
                order by competencia_id desc
                limit 1
                """
            ),
            params,
        )
        row = result.mappings().first()
        if not row:
            return {
                "dados": [],
                "meta": MetaEnvelope(
                    competencia_referencia=competencia or "atual",
                    versao_dataset="score_v3_v1",
                    total=0,
                    pagina=1,
                    por_pagina=1,
                ).model_dump(),
            }

    payload = {
        "dados": [ScoreV3Item(**row).model_dump()],
        "meta": MetaEnvelope(
            competencia_referencia=row["competencia_id"],
            versao_dataset=row["versao_metodologia"] or "v3.0",
            total=1,
            pagina=1,
            por_pagina=1,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload


async def buscar_historico_score_v3(
    registro_ans: str,
    *,
    periodos: int = 12,
) -> dict:
    registro_ans = registro_ans.zfill(6)
    periodos = min(max(periodos, 1), 24)
    cache_key = f"score_v3_hist:{registro_ans}:{periodos}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    operadora_id,
                    competencia_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    trimestre_financeiro,
                    score_core,
                    score_regulatorio,
                    score_financeiro,
                    score_rede,
                    score_estrutural,
                    score_completo,
                    score_v3_final,
                    versao_metodologia
                from api_ans.api_score_v3_operadora_mensal
                where registro_ans = :registro_ans
                order by competencia_id desc
                limit :periodos
                """
            ),
            {"registro_ans": registro_ans, "periodos": periodos},
        )
        rows = result.mappings().all()

    payload = {
        "dados": [ScoreV3Item(**row).model_dump() for row in rows],
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia_id"] if rows else "atual",
            versao_dataset="v3.0",
            total=len(rows),
            pagina=1,
            por_pagina=periodos,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload
