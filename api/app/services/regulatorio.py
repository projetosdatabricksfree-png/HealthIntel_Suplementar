import json

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.regulatorio import OperadoraRegulatorioResponse, Rn623ListaResponse

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
        return {"competencia_referencia": fallback_competencia, "versao_dataset": f"{dataset}_v1"}
    return {
        "competencia_referencia": row["competencia"] or fallback_competencia,
        "versao_dataset": row["versao"],
    }


async def detalhar_regulatorio_operadora(
    registro_ans: str,
    *,
    trimestre: str | None = None,
) -> dict:
    cache_key = f"regulatorio:{registro_ans}:{trimestre or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtro_trimestre = ""
    params = {"registro_ans": registro_ans.zfill(6)}
    if trimestre:
        filtro_trimestre = "and trimestre = :trimestre"
        params["trimestre"] = trimestre.upper()

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    registro_ans,
                    trimestre,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    igr,
                    meta_igr,
                    atingiu_meta_excelencia,
                    demandas_nip,
                    demandas_resolvidas,
                    taxa_intermediacao_resolvida,
                    taxa_resolutividade,
                    rn623_excelencia,
                    rn623_reducao,
                    faixa_risco_regulatorio,
                    status_rn623,
                    versao_regulatoria
                from api_ans.api_regulatorio_operadora_trimestral
                where registro_ans = :registro_ans
                {filtro_trimestre}
                order by trimestre desc
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
                    "codigo_erro": "REGULATORIO_NAO_ENCONTRADO",
                    "mensagem": "Nao ha consolidado regulatorio para o registro ANS informado.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(session, "igr", row["trimestre"])

    payload = {
        "dados": [OperadoraRegulatorioResponse(**row).model_dump()],
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


async def listar_rn623(
    *,
    trimestre: str | None = None,
    tipo_lista: str | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    trimestre = trimestre.upper() if trimestre else None
    tipo_lista = tipo_lista.lower() if tipo_lista else None
    cache_key = f"rn623:{trimestre or 'latest'}:{tipo_lista or 'all'}:{pagina}:{por_pagina}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if trimestre:
        filtros.append("trimestre = :trimestre")
        params["trimestre"] = trimestre
    if tipo_lista:
        filtros.append("tipo_lista = :tipo_lista")
        params["tipo_lista"] = tipo_lista
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(
                "select count(*) as total "
                f"from api_ans.api_rn623_lista_trimestral {where_clause}"
            ),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    trimestre,
                    tipo_lista,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    total_nip,
                    beneficiarios,
                    igr,
                    meta_igr,
                    elegivel,
                    observacao
                from api_ans.api_rn623_lista_trimestral
                {where_clause}
                order by trimestre desc, tipo_lista, nome nulls last, registro_ans
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        competencia = rows[0]["trimestre"] if rows else (trimestre or "atual")
        meta_dataset = await _resolver_meta_dataset(session, "rn623_lista", competencia)

    payload = {
        "dados": [Rn623ListaResponse(**row).model_dump() for row in rows],
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
