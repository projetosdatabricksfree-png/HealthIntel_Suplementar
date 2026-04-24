from __future__ import annotations

import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.prata import PrataQualidadeMeta, QuarentenaRegistroItem, QuarentenaResumoItem

settings = get_settings()


PRATA_DATASETS = {
    "cadop": {
        "tabela": "api_ans.api_prata_cadop",
        "competencia": "competencia",
        "fonte": "cadop",
    },
    "sib_operadora": {
        "tabela": "api_ans.api_prata_sib_operadora",
        "competencia": "competencia",
        "fonte": "sib_operadora",
    },
    "sib_municipio": {
        "tabela": "api_ans.api_prata_sib_municipio",
        "competencia": "competencia",
        "fonte": "sib_municipio",
    },
    "igr": {
        "tabela": "api_ans.api_prata_igr",
        "competencia": "trimestre",
        "fonte": "igr",
    },
    "nip": {
        "tabela": "api_ans.api_prata_nip",
        "competencia": "trimestre",
        "fonte": "nip",
    },
    "idss": {
        "tabela": "api_ans.api_prata_idss",
        "competencia": "ano_base",
        "fonte": "idss",
    },
    "diops": {
        "tabela": "api_ans.api_prata_diops",
        "competencia": "trimestre",
        "fonte": "diops",
    },
    "fip": {
        "tabela": "api_ans.api_prata_fip",
        "competencia": "trimestre",
        "fonte": "fip",
    },
    "vda": {
        "tabela": "api_ans.api_prata_vda",
        "competencia": "competencia",
        "fonte": "vda",
    },
    "glosa": {
        "tabela": "api_ans.api_prata_glosa",
        "competencia": "competencia",
        "fonte": "glosa",
    },
    "rede_assistencial": {
        "tabela": "api_ans.api_prata_rede_assistencial",
        "competencia": "competencia",
        "fonte": "rede_assistencial",
    },
    "operadora_enriquecida": {
        "tabela": "api_ans.api_prata_operadora_enriquecida",
        "competencia": "competencia",
        "fonte": "beneficiario_operadora",
    },
    "municipio_metrica": {
        "tabela": "api_ans.api_prata_municipio_metrica",
        "competencia": "competencia",
        "fonte": "beneficiario_localidade",
    },
    "financeiro_periodo": {
        "tabela": "api_ans.api_prata_financeiro_periodo",
        "competencia": "trimestre",
        "fonte": "diops",
    },
    "cnes_municipio": {
        "tabela": "api_ans.api_prata_cnes_municipio",
        "competencia": "competencia",
        "fonte": "cnes_estabelecimento",
    },
    "cnes_rede_gap": {
        "tabela": "api_ans.api_prata_cnes_rede_gap",
        "competencia": "competencia",
        "fonte": "cnes_estabelecimento",
    },
    "tiss_procedimento": {
        "tabela": "api_ans.api_prata_tiss_procedimento",
        "competencia": "trimestre",
        "fonte": "tiss_procedimento",
    },
}

PRATA_FILTROS_PERMITIDOS = {
    "cadop": {"registro_ans"},
    "sib_operadora": {"registro_ans"},
    "sib_municipio": {"registro_ans", "codigo_ibge"},
    "igr": {"registro_ans"},
    "nip": {"registro_ans"},
    "idss": {"registro_ans"},
    "diops": {"registro_ans"},
    "fip": {"registro_ans"},
    "vda": {"registro_ans"},
    "glosa": {"registro_ans", "tipo_glosa"},
    "rede_assistencial": {"registro_ans", "cd_municipio"},
    "operadora_enriquecida": {"registro_ans"},
    "municipio_metrica": {"cd_municipio"},
    "financeiro_periodo": {"registro_ans"},
    "cnes_municipio": {"cd_municipio"},
    "cnes_rede_gap": {"cd_municipio", "registro_ans"},
    "tiss_procedimento": {"registro_ans", "grupo_procedimento"},
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


async def _qualidade_prata(
    session,
    *,
    dataset: str,
    competencia: str,
    total_aprovado: int,
) -> PrataQualidadeMeta:
    result = await session.execute(
        text(
            """
            select
                count(*) as registros_quarentena,
                array_remove(array_agg(distinct motivo_rejeicao), null) as motivos_rejeicao
            from (
                select
                    motivo as motivo_rejeicao
                from plataforma.arquivo_quarentena
                where dataset = :dataset
                  and coalesce(hash_arquivo, '') in (
                      select coalesce(hash_arquivo, '')
                      from plataforma.versao_dataset
                      where dataset = :dataset
                        and coalesce(competencia, '') = coalesce(:competencia, '')
                  )
            ) as base
            """
        ),
        {"dataset": dataset, "competencia": competencia},
    )
    row = result.mappings().first() or {}
    registros_quarentena = int(row.get("registros_quarentena") or 0)
    total_bruto = total_aprovado + registros_quarentena
    taxa_aprovacao = round((total_aprovado / total_bruto) if total_bruto else 1.0, 4)
    return PrataQualidadeMeta(
        taxa_aprovacao=taxa_aprovacao,
        registros_quarentena=registros_quarentena,
        motivos_rejeicao=list(row.get("motivos_rejeicao") or []),
    )


async def buscar_prata(
    dataset: str,
    *,
    competencia: str,
    filtros: dict[str, object] | None = None,
    pagina: int = 1,
    limite: int = 50,
) -> dict:
    if dataset not in PRATA_DATASETS:
        raise ValueError(f"Dataset prata nao suportado: {dataset}")

    pagina = max(pagina, 1)
    limite = min(max(limite, 1), 100)
    offset = (pagina - 1) * limite
    filtros = filtros or {}
    cfg = PRATA_DATASETS[dataset]
    cache_key = (
        f"prata:{dataset}:{competencia}:{pagina}:{limite}:{json.dumps(filtros, sort_keys=True)}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"competencia": competencia, "limit": limite, "offset": offset}
    where_clauses = [f"{cfg['competencia']} = :competencia"]
    filtros_permitidos = PRATA_FILTROS_PERMITIDOS.get(dataset, set())
    for chave, valor in filtros.items():
        if valor is None:
            continue
        if chave not in filtros_permitidos:
            continue
        where_clauses.append(f"{chave} = :{chave}")
        params[chave] = valor
    where_clause = " where " + " and ".join(where_clauses)

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
                order by {cfg["competencia"]} desc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = [dict(row) for row in result.mappings().all()]
        qualidade = await _qualidade_prata(
            session,
            dataset=cfg["fonte"],
            competencia=competencia,
            total_aprovado=total,
        )
    aviso_qualidade = (
        f"Qualidade abaixo do limiar: {qualidade.taxa_aprovacao:.1%} aprovado "
        f"({qualidade.registros_quarentena} registros em quarentena)"
        if qualidade.taxa_aprovacao < 0.95
        else None
    )

    payload = {
        "dados": rows,
        "meta": {
            "fonte": cfg["fonte"],
            "competencia": competencia,
            "versao_dataset": rows[0].get("versao_dataset") if rows else f"{dataset}_v1",
            "qualidade": qualidade.model_dump(),
            "aviso_qualidade": aviso_qualidade,
            "total": total,
            "pagina": pagina,
            "por_pagina": limite,
            "cache": "miss",
        },
    }
    await _salvar_cache(cache_key, payload)
    return payload


async def buscar_quarentena_resumo(competencia: str | None = None) -> dict:
    cache_key = f"prata:quarentena:resumo:{competencia or 'all'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtro = ""
    params: dict[str, object] = {}
    if competencia:
        filtro = "where competencia = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    dataset,
                    arquivo_origem,
                    competencia,
                    hash_arquivo,
                    total_registros,
                    primeiro_registro_em,
                    ultimo_registro_em,
                    status_quarentena
                from plataforma.vw_resumo_quarentena
                {filtro}
                order by dataset, competencia desc, arquivo_origem
                """
            ),
            params,
        )
        rows_brutos = result.mappings().all()
        rows = [QuarentenaResumoItem(**row).model_dump() for row in rows_brutos]
        total_quarentena = sum(int(row["total_registros"] or 0) for row in rows_brutos)

    payload = {
        "dados": rows,
        "meta": {
            "fonte": "plataforma.vw_resumo_quarentena",
            "competencia": competencia or "todas",
            "versao_dataset": "quarentena_v1",
            "qualidade": {
                "taxa_aprovacao": 1.0,
                "registros_quarentena": total_quarentena,
                "motivos_rejeicao": [],
            },
            "total": len(rows),
            "pagina": 1,
            "por_pagina": len(rows) or 1,
            "cache": "miss",
        },
    }
    await _salvar_cache(cache_key, payload)
    return payload


async def buscar_quarentena_dataset(
    dataset: str,
    *,
    competencia: str | None = None,
    pagina: int = 1,
    limite: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    limite = min(max(limite, 1), 100)
    offset = (pagina - 1) * limite
    cache_key = f"prata:quarentena:{dataset}:{competencia or 'all'}:{pagina}:{limite}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"dataset": dataset, "limit": limite, "offset": offset}
    where_clauses = ["dataset = :dataset"]
    if competencia:
        where_clauses.append(
            """
            coalesce(hash_arquivo, '') in (
                select coalesce(hash_arquivo, '')
                from plataforma.versao_dataset
                where dataset = :dataset
                  and coalesce(competencia, '') = coalesce(:competencia, '')
            )
            """
        )
        params["competencia"] = competencia
    filtro = " where " + " and ".join(clause.strip() for clause in where_clauses)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from plataforma.arquivo_quarentena {filtro}"),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    id as id_quarentena,
                    dataset,
                    arquivo_origem,
                    hash_arquivo,
                    hash_estrutura,
                    motivo as motivo,
                    status,
                    criado_em
                from plataforma.arquivo_quarentena
                {filtro}
                order by criado_em desc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = [QuarentenaRegistroItem(**row).model_dump() for row in result.mappings().all()]

    payload = {
        "dados": rows,
        "meta": {
            "fonte": "plataforma.arquivo_quarentena",
            "competencia": competencia or "todas",
            "versao_dataset": "quarentena_v1",
            "qualidade": {
                "taxa_aprovacao": 1.0,
                "registros_quarentena": total,
                "motivos_rejeicao": [],
            },
            "total": total,
            "pagina": pagina,
            "por_pagina": limite,
            "cache": "miss",
        },
    }
    await _salvar_cache(cache_key, payload)
    return payload
