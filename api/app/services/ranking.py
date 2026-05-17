from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.ranking import (
    RankingCompostoResponse,
    RankingCrescimentoResponse,
    RankingOperadoraScoreResponse,
    RankingOportunidadeResponse,
    RankingOportunidadeV2Response,
)
from api.app.services.cobertura_temporal import adicionar_filtro_mensal, anexar_janela_temporal

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


async def listar_ranking_score(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    competencia: str | None = None,
    competencia_inicio: str | None = None,
    competencia_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"ranking:score:{pagina}:{por_pagina}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtros: list[str] = []
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    where_clause = " where " + " and ".join(filtros) if filtros else ""
    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_ranking_score{where_clause}"),
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
                    competencia,
                    score_final,
                    rating,
                    ranking_posicao,
                    versao_score
                from api_ans.api_ranking_score
                {where_clause}
                order by ranking_posicao asc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    dados = [RankingOperadoraScoreResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia"] if rows else "atual",
            versao_dataset="score_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/rankings/operadora/score")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_ranking_crescimento(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    competencia: str | None = None,
    competencia_inicio: str | None = None,
    competencia_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"ranking:crescimento:{pagina}:{por_pagina}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtros: list[str] = []
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    where_clause = " where " + " and ".join(filtros) if filtros else ""
    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_ranking_crescimento{where_clause}"),
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
                    competencia,
                    taxa_crescimento_12m,
                    beneficiario_atual,
                    beneficiario_12m_anterior,
                    ranking_posicao
                from api_ans.api_ranking_crescimento
                {where_clause}
                order by ranking_posicao asc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    dados = [RankingCrescimentoResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia"] if rows else "atual",
            versao_dataset="growth_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/rankings/operadora/crescimento")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_ranking_oportunidade(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    competencia: str | None = None,
    competencia_inicio: str | None = None,
    competencia_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"ranking:oportunidade:{pagina}:{por_pagina}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtros: list[str] = []
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    where_clause = " where " + " and ".join(filtros) if filtros else ""
    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_ranking_oportunidade{where_clause}"),
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
                    competencia,
                    oportunidade_score,
                    ranking_posicao
                from api_ans.api_ranking_oportunidade
                {where_clause}
                order by ranking_posicao asc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    dados = [RankingOportunidadeResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia"] if rows else "atual",
            versao_dataset="opportunity_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/rankings/municipio/oportunidade")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_ranking_oportunidade_v2(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    competencia: str | None = None,
    competencia_inicio: str | None = None,
    competencia_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"ranking:oportunidade:v2:{pagina}:{por_pagina}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtros: list[str] = []
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    where_clause = " where " + " and ".join(filtros) if filtros else ""
    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                "select count(*) from api_ans.api_oportunidade_v2_municipio_mensal"
                f"{where_clause}"
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
                    total_beneficiarios,
                    hhi_municipio,
                    cobertura_media_pct,
                    cobertura_rede,
                    oportunidade_score_v1,
                    qt_operadoras_cobertura,
                    qt_segmentos_cobertos,
                    qt_segmentos_vazios,
                    qt_segmentos_parciais,
                    pct_operadoras_com_cobertura,
                    pct_operadoras_sem_cobertura,
                    vazio_assistencial_presente,
                    operadora_melhor_score_v2,
                    score_v2_maximo,
                    score_oportunidade_rede,
                    score_sip,
                    oportunidade_v2_score,
                    ranking_posicao,
                    sinal_vazio,
                    versao_algoritmo
                from api_ans.api_oportunidade_v2_municipio_mensal
                {where_clause}
                order by ranking_posicao asc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    dados = [RankingOportunidadeV2Response(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia"] if rows else "atual",
            versao_dataset="opportunity_v2",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/rankings/municipio/oportunidade-v2")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_ranking_composto(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    competencia: str | None = None,
    competencia_inicio: str | None = None,
    competencia_fim: str | None = None,
    modalidade: str | None = None,
    uf: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"ranking:composto:{pagina}:{por_pagina}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}:{modalidade or ''}:{uf or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtros = ["1=1"]
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia_id",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    if modalidade:
        filtros.append("modalidade = :modalidade")
        params["modalidade"] = modalidade
    if uf:
        filtros.append("uf_sede = :uf")
        params["uf"] = uf.upper()
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_ranking_composto_mensal {where_clause}"),
            params,
        )
        total = int(total_result.scalar_one())
        sql = f"""
            select
                operadora_id,
                competencia_id,
                registro_ans,
                nome,
                nome_fantasia,
                modalidade,
                uf_sede,
                score_v3_final,
                posicao_geral,
                posicao_por_modalidade,
                variacao_posicao_3m,
                versao_metodologia
            from api_ans.api_ranking_composto_mensal
            {where_clause}
            order by posicao_geral asc, score_v3_final desc
            limit :limit offset :offset
            """
        result = await session.execute(
            text(sql),
            params,
        )
        rows = result.mappings().all()

    dados = [RankingCompostoResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=rows[0]["competencia_id"] if rows else "atual",
            versao_dataset="score_v3",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/rankings/composto")
    await _salvar_cache(cache_key, payload)
    return payload
