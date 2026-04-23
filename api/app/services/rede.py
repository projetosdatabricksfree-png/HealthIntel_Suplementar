from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.rede import RedeMunicipioResponse, RedeOperadoraResponse

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
    fallback_competencia = str(fallback_competencia)
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


async def detalhar_rede_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
    segmento: str | None = None,
    uf: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"rede:operadora:{registro_ans}:{competencia or 'latest'}:"
        f"{segmento or 'all'}:{uf or 'all'}:{pagina}:{por_pagina}"
    )
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
        params["competencia"] = competencia
    if segmento:
        filtros.append("segmento = :segmento")
        params["segmento"] = segmento.upper()
    if uf:
        filtros.append("sg_uf = :uf")
        params["uf"] = uf.upper()
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_rede_assistencial
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
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    competencia_id,
                    cd_municipio,
                    nm_municipio,
                    sg_uf,
                    nm_regiao,
                    segmento,
                    pop_estimada_ibge,
                    porte_municipio,
                    qt_prestador,
                    qt_especialidade_disponivel,
                    beneficiario_total,
                    qt_prestador_por_10k_beneficiarios,
                    limiar_prestador_por_10k,
                    limiar_especialidade_por_10k,
                    tem_cobertura,
                    cobertura_minima_atendida,
                    qt_municipio_coberto,
                    qt_uf_coberto,
                    pct_municipios_cobertos,
                    pct_ufs_cobertos,
                    score_rede,
                    versao_dataset
                from api_ans.api_rede_assistencial
                {where_clause}
                order by
                    competencia desc,
                    score_rede desc nulls last,
                    qt_prestador_por_10k_beneficiarios desc nulls last,
                    nm_municipio
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "rede_assistencial",
            str(rows[0]["competencia"]) if rows else (competencia or "atual"),
        )

    dados = [RedeOperadoraResponse(**row).model_dump() for row in rows]
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


async def listar_rede_municipio(
    cd_municipio: str,
    *,
    competencia: str | None = None,
    segmento: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cd_municipio = "".join(filter(str.isdigit, cd_municipio)).zfill(7)
    cache_key = (
        f"rede:municipio:{cd_municipio}:{competencia or 'latest'}:"
        f"{segmento or 'all'}:{pagina}:{por_pagina}"
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
    if segmento:
        filtros.append("segmento = :segmento")
        params["segmento"] = segmento.upper()
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                f"""
                select count(*) as total
                from api_ans.api_rede_assistencial
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
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    competencia_id,
                    cd_municipio,
                    nm_municipio,
                    sg_uf,
                    nm_regiao,
                    segmento,
                    pop_estimada_ibge,
                    porte_municipio,
                    qt_prestador,
                    qt_especialidade_disponivel,
                    beneficiario_total,
                    qt_prestador_por_10k_beneficiarios,
                    limiar_prestador_por_10k,
                    limiar_especialidade_por_10k,
                    tem_cobertura,
                    cobertura_minima_atendida,
                    qt_municipio_coberto,
                    qt_uf_coberto,
                    pct_municipios_cobertos,
                    pct_ufs_cobertos,
                    score_rede,
                    versao_dataset
                from api_ans.api_rede_assistencial
                {where_clause}
                order by
                    competencia desc,
                    score_rede desc nulls last,
                    qt_prestador_por_10k_beneficiarios desc nulls last,
                    nome
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        meta_dataset = await _resolver_meta_dataset(
            session,
            "rede_assistencial",
            str(rows[0]["competencia"]) if rows else (competencia or "atual"),
        )

    dados = [RedeMunicipioResponse(**row).model_dump() for row in rows]
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
