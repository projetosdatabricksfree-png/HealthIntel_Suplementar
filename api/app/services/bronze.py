from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.bronze import BronzeMetaResponse

settings = get_settings()


BRONZE_DATASETS = {
    "cadop": {"tabela": "api_ans.api_bronze_cadop", "competencia": "competencia", "fonte": "cadop"},
    "sib_operadora": {
        "tabela": "api_ans.api_bronze_sib_operadora",
        "competencia": "competencia",
        "fonte": "sib_operadora",
    },
    "sib_municipio": {
        "tabela": "api_ans.api_bronze_sib_municipio",
        "competencia": "competencia",
        "fonte": "sib_municipio",
    },
    "igr": {"tabela": "api_ans.api_bronze_igr", "competencia": "trimestre", "fonte": "igr"},
    "nip": {"tabela": "api_ans.api_bronze_nip", "competencia": "trimestre", "fonte": "nip"},
    "idss": {"tabela": "api_ans.api_bronze_idss", "competencia": "ano_base", "fonte": "idss"},
    "diops": {"tabela": "api_ans.api_bronze_diops", "competencia": "trimestre", "fonte": "diops"},
    "fip": {"tabela": "api_ans.api_bronze_fip", "competencia": "trimestre", "fonte": "fip"},
    "vda": {"tabela": "api_ans.api_bronze_vda", "competencia": "competencia", "fonte": "vda"},
    "glosa": {"tabela": "api_ans.api_bronze_glosa", "competencia": "competencia", "fonte": "glosa"},
    "rede_assistencial": {
        "tabela": "api_ans.api_bronze_rede_assistencial",
        "competencia": "competencia",
        "fonte": "rede_assistencial",
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


async def _resolver_versao_dataset(session, dataset: str, competencia: str) -> tuple[str, str, str]:
    result = await session.execute(
        text(
            """
            select
                versao,
                coalesce(competencia, :competencia) as competencia,
                hash_arquivo
            from plataforma.versao_dataset
            where dataset = :dataset
            order by carregado_em desc
            limit 1
            """
        ),
        {"dataset": dataset, "competencia": competencia},
    )
    row = result.mappings().first()
    if not row:
        return competencia, f"{dataset}_v1", ""
    return str(row["competencia"] or competencia), str(row["versao"]), str(row["hash_arquivo"])


async def buscar_bronze(
    dataset: str,
    *,
    competencia: str,
    lote_id: str | None = None,
    pagina: int = 1,
    limite: int = 50,
) -> dict:
    if dataset not in BRONZE_DATASETS:
        raise ValueError(f"Dataset bronze nao suportado: {dataset}")

    pagina = max(pagina, 1)
    limite = min(max(limite, 1), 100)
    offset = (pagina - 1) * limite
    cfg = BRONZE_DATASETS[dataset]
    cache_key = f"bronze:{dataset}:{competencia}:{lote_id or 'all'}:{pagina}:{limite}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"competencia": competencia, "limit": limite, "offset": offset}
    where_clauses = [f"{cfg['competencia']} = :competencia"]
    if lote_id:
        where_clauses.append("_lote_id = :lote_id")
        params["lote_id"] = lote_id
    where_clause = " where " + " and ".join(where_clauses)

    async with SessionLocal() as session:
        await session.execute(
            text(f"select count(*) from {cfg['tabela']} {where_clause}"),
            params,
        )
        result = await session.execute(
            text(
                f"""
                select *
                from {cfg["tabela"]}
                {where_clause}
                order by _carregado_em desc, _lote_id desc
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = [dict(row) for row in result.mappings().all()]
        competencia_ref, versao_dataset, _ = await _resolver_versao_dataset(
            session,
            dataset,
            competencia,
        )

    primeiro = rows[0] if rows else {}
    payload = {
        "dados": rows,
        "meta": BronzeMetaResponse(
            fonte=cfg["fonte"],
            competencia=competencia_ref,
            lote_id=str(primeiro.get("_lote_id") or lote_id or ""),
            arquivo_origem=str(primeiro.get("_arquivo_origem") or ""),
            carregado_em=primeiro.get("_carregado_em") or datetime.now(tz=UTC),
            versao_dataset=versao_dataset,
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload
