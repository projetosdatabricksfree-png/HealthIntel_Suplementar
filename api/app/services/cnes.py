from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.cnes import CnesMunicipioItem, CnesUfItem
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


async def listar_cnes_municipio(
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
        f"cnes:municipio:{cd_municipio}:{competencia or 'latest'}:"
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
                from api_ans.api_cnes_municipio
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
                    total_estabelecimentos,
                    total_estabelecimentos_vinculo_sus,
                    total_leitos,
                    total_leitos_sus,
                    pct_leitos_sus,
                    pct_vinculo_sus,
                    pop_estimada_ibge,
                    porte_municipio,
                    versao_dataset
                from api_ans.api_cnes_municipio
                {where_clause}
                order by competencia desc, tipo_unidade, nm_municipio
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

    dados = [CnesMunicipioItem(**row).model_dump() for row in rows]
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


async def listar_cnes_uf(
    sg_uf: str,
    *,
    competencia: str | None = None,
    tipo_unidade: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    sg_uf = sg_uf.strip().upper()[:2]
    cache_key = (
        f"cnes:uf:{sg_uf}:{competencia or 'latest'}:"
        f"{tipo_unidade or 'all'}:{pagina}:{por_pagina}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {
        "sg_uf": sg_uf,
        "limit": por_pagina,
        "offset": offset,
    }
    filtros = ["sg_uf = :sg_uf"]
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
                from api_ans.api_cnes_municipio
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
                    sg_uf,
                    nm_uf,
                    tipo_unidade,
                    max(tipo_unidade_desc) as tipo_unidade_desc,
                    sum(total_estabelecimentos) as total_estabelecimentos,
                    sum(total_estabelecimentos_vinculo_sus) as total_estabelecimentos_vinculo_sus,
                    sum(total_leitos) as total_leitos,
                    sum(total_leitos_sus) as total_leitos_sus,
                    round(
                        coalesce(
                            (sum(total_leitos_sus)::numeric / nullif(sum(total_leitos), 0)) * 100,
                            0
                        ),
                        2
                    ) as pct_leitos_sus,
                    round(
                        coalesce(
                            (
                                sum(total_estabelecimentos_vinculo_sus)::numeric
                                / nullif(sum(total_estabelecimentos), 0)
                            ) * 100,
                            0
                        ),
                        2
                    ) as pct_vinculo_sus,
                    max(versao_dataset) as versao_dataset
                from api_ans.api_cnes_municipio
                {where_clause}
                group by 1, 2, 3, 4
                order by competencia desc, tipo_unidade
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

    dados = [
        CnesUfItem(
            **{
                **row,
                "nm_uf": row.get("nm_uf"),
            }
        ).model_dump()
        for row in rows
    ]
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
