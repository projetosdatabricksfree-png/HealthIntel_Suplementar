from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.tiss import CnesRedeGapItem, SinistralProcedimentoItem, TissProcedimentoItem

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


async def listar_tiss_procedimentos(
    registro_ans: str,
    *,
    trimestre: str | None = None,
    grupo_procedimento: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    registro_ans = registro_ans.zfill(6)
    cache_key = (
        f"tiss:procedimentos:{registro_ans}:{trimestre or 'latest'}:"
        f"{grupo_procedimento or 'all'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {
        "registro_ans": registro_ans,
        "limit": por_pagina,
        "offset": offset,
    }
    filtros = ["registro_ans = :registro_ans"]
    if trimestre:
        filtros.append("trimestre = :trimestre")
        params["trimestre"] = trimestre
    if grupo_procedimento:
        filtros.append("grupo_procedimento = :grupo_procedimento")
        params["grupo_procedimento"] = grupo_procedimento
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_tiss_operadora_trimestral
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
                    trimestre,
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade_operadora,
                    uf_sede,
                    grupo_procedimento,
                    grupo_desc,
                    subgrupo_procedimento,
                    qt_procedimentos,
                    qt_beneficiarios_distintos,
                    valor_total,
                    valor_medio,
                    pct_do_total_operadora,
                    rank_por_valor,
                    versao_dataset
                from api_ans.api_tiss_operadora_trimestral
                {where_clause}
                order by trimestre desc, rank_por_valor, grupo_procedimento
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "tiss_procedimento",
            str(rows[0]["trimestre"]) if rows else (trimestre or "atual"),
        )

    dados = [TissProcedimentoItem(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
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


async def listar_sinistralidade_procedimento(
    registro_ans: str,
    *,
    trimestre: str | None = None,
    grupo_procedimento: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    registro_ans = registro_ans.zfill(6)
    cache_key = (
        f"tiss:sinistralidade:{registro_ans}:{trimestre or 'latest'}:"
        f"{grupo_procedimento or 'all'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {
        "registro_ans": registro_ans,
        "limit": por_pagina,
        "offset": offset,
    }
    filtros = ["registro_ans = :registro_ans"]
    if trimestre:
        filtros.append("trimestre = :trimestre")
        params["trimestre"] = trimestre
    if grupo_procedimento:
        filtros.append("grupo_procedimento = :grupo_procedimento")
        params["grupo_procedimento"] = grupo_procedimento
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_sinistralidade_procedimento
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
                    trimestre,
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade_operadora,
                    uf_sede,
                    grupo_procedimento,
                    grupo_desc,
                    subgrupo_procedimento,
                    qt_procedimentos,
                    qt_beneficiarios_distintos,
                    valor_tiss,
                    receita_total,
                    sinistralidade_grupo_pct,
                    desvio_padrao_sinistralidade,
                    flag_sinistralidade_alta,
                    rank_sinistralidade,
                    versao_dataset
                from api_ans.api_sinistralidade_procedimento
                {where_clause}
                order by trimestre desc, rank_sinistralidade, grupo_procedimento
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "tiss_procedimento",
            str(rows[0]["trimestre"]) if rows else (trimestre or "atual"),
        )

    dados = [SinistralProcedimentoItem(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
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


async def listar_gap_rede_municipio(
    cd_municipio: str,
    *,
    competencia: str | None = None,
    tipo_unidade: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cd_municipio = "".join(filter(str.isdigit, cd_municipio)).zfill(7)
    cache_key = (
        f"tiss:gap:{cd_municipio}:{competencia or 'latest'}:"
        f"{tipo_unidade or 'all'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {
        "cd_municipio": cd_municipio,
        "limit": por_pagina,
        "offset": offset,
    }
    filtros = ["cd_municipio = :cd_municipio"]
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = competencia
    if tipo_unidade:
        filtros.append("tipo_unidade = :tipo_unidade")
        params["tipo_unidade"] = tipo_unidade
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_cnes_rede_gap
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
                    competencia,
                    cd_municipio,
                    nm_municipio,
                    nm_uf,
                    sg_uf,
                    regiao,
                    tipo_unidade,
                    tipo_unidade_desc,
                    estabelecimentos_cnes,
                    prestadores_credenciados,
                    gap_absoluto,
                    gap_pct,
                    severidade_gap,
                    flag_gap_critico,
                    versao_dataset
                from api_ans.api_cnes_rede_gap
                {where_clause}
                order by competencia desc, gap_absoluto desc, tipo_unidade
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "cnes_estabelecimento",
            str(rows[0]["competencia"]) if rows else (competencia or "atual"),
        )

    dados = [CnesRedeGapItem(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
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
