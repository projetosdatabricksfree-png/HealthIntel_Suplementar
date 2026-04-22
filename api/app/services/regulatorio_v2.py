from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.regulatorio_v2 import (
    PortabilidadeResponse,
    RegimeEspecialResponse,
    ScoreRegulatorioResponse,
)

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


async def _resolver_meta_dataset(session, dataset: str, fallback_competencia: str) -> dict:
    result = await session.execute(
        text(
            """
            select
                coalesce(competencia, :fallback_competencia) as competencia,
                versao
            from plataforma.versao_dataset
            where dataset = :dataset
            order by carregado_em desc
            limit 1
            """
        ),
        {"dataset": dataset, "fallback_competencia": fallback_competencia},
    )
    row = result.mappings().first()
    if not row:
        return {
            "competencia_referencia": str(fallback_competencia),
            "versao_dataset": f"{dataset}_v1",
        }
    return {
        "competencia_referencia": str(row["competencia"] or fallback_competencia),
        "versao_dataset": row["versao"],
    }


async def detalhar_score_regulatorio_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
) -> dict:
    cache_key = f"score_regulatorio:{registro_ans}:{competencia or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtro_competencia = ""
    params: dict[str, object] = {"registro_ans": registro_ans.zfill(6)}
    if competencia:
        filtro_competencia = "and competencia = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    score_igr,
                    score_nip,
                    score_rn623,
                    score_prudencial,
                    score_taxa_resolutividade,
                    regime_especial_ativo,
                    tipo_regime,
                    situacao_inadequada,
                    qt_portabilidade_entrada,
                    qt_portabilidade_saida,
                    saldo_portabilidade,
                    score_regulatorio_base,
                    score_regulatorio,
                    rating,
                    versao_regulatoria
                from api_ans.api_score_regulatorio_operadora_mensal
                where registro_ans = :registro_ans
                {filtro_competencia}
                order by competencia desc
                limit 1
                """
            ),
            params,
        )
        row = result.mappings().first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "SCORE_REGULATORIO_NAO_ENCONTRADO",
                    "mensagem": "Nao ha consolidado regulatorio v2 para o registro ANS informado.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(
            session,
            "score_regulatorio",
            row["competencia"],
        )

    payload = {
        "dados": [ScoreRegulatorioResponse(**row).model_dump()],
        "meta": MetaEnvelope(
            competencia_referencia=meta_dataset["competencia_referencia"],
            versao_dataset=meta_dataset["versao_dataset"],
            total=1,
            pagina=1,
            por_pagina=1,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_regime_especial_operadora(registro_ans: str) -> dict:
    cache_key = f"regime_especial:{registro_ans}"
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
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    trimestre,
                    trimestre_fim,
                    tipo_regime,
                    ativo,
                    duracao_trimestres,
                    data_inicio,
                    data_fim,
                    versao_dataset
                from api_ans.api_regime_especial_operadora
                where registro_ans = :registro_ans
                order by data_inicio desc nulls last, trimestre desc
                limit 20
                """
            ),
            {"registro_ans": registro_ans.zfill(6)},
        )
        rows = result.mappings().all()
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "REGIME_ESPECIAL_NAO_ENCONTRADO",
                    "mensagem": (
                        "Nao ha historico de regime especial para o registro ANS informado."
                    ),
                },
            )
        meta_dataset = await _resolver_meta_dataset(
            session,
            "regime_especial",
            rows[0]["trimestre"],
        )

    payload = {
        "dados": [RegimeEspecialResponse(**row).model_dump() for row in rows],
        "meta": MetaEnvelope(
            competencia_referencia=meta_dataset["competencia_referencia"],
            versao_dataset=meta_dataset["versao_dataset"],
            total=len(rows),
            pagina=1,
            por_pagina=len(rows),
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_portabilidade_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = f"portabilidade:{registro_ans}:{competencia or 'all'}:{pagina}:{por_pagina}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {
        "registro_ans": registro_ans.zfill(6),
        "limit": por_pagina,
        "offset": offset,
    }
    filtros = ["registro_ans = :registro_ans"]
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = int(competencia)
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                "select count(*) as total "
                f"from api_ans.api_portabilidade_operadora_mensal {where_clause}"
            ),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    competencia_data,
                    modalidade_descricao,
                    tipo_contratacao,
                    qt_portabilidade_entrada,
                    qt_portabilidade_saida,
                    saldo_portabilidade,
                    fonte_publicacao,
                    versao_dataset
                from api_ans.api_portabilidade_operadora_mensal
                {where_clause}
                order by competencia desc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "portabilidade",
            str(rows[0]["competencia"]) if rows else (competencia or "atual"),
        )

    payload = {
        "dados": [PortabilidadeResponse(**row).model_dump() for row in rows],
        "meta": MetaEnvelope(
            competencia_referencia=meta_dataset["competencia_referencia"],
            versao_dataset=meta_dataset["versao_dataset"],
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload
