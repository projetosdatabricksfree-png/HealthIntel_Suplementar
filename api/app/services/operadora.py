import json

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.meta import MetaEnvelope
from api.app.schemas.operadora import OperadoraResumoResponse, OperadoraScoreResponse

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


async def listar_operadoras(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    busca: str | None = None,
    uf: str | None = None,
    modalidade: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = f"operadoras:{pagina}:{por_pagina}:{busca or ''}:{uf or ''}:{modalidade or ''}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if busca:
        busca_normalizada = busca.strip()
        params["busca_like"] = f"%{busca_normalizada}%"
        if busca_normalizada.isdigit():
            params["busca_exata"] = busca_normalizada.zfill(6)
            filtros.append(
                "("
                "nome ilike :busca_like "
                "or nome_fantasia ilike :busca_like "
                "or registro_ans = :busca_exata"
                ")"
            )
        else:
            filtros.append("(nome ilike :busca_like or nome_fantasia ilike :busca_like)")
    if uf:
        params["uf"] = uf.upper()
        filtros.append("uf_sede = :uf")
    if modalidade:
        params["modalidade"] = modalidade.upper()
        filtros.append("modalidade = :modalidade")
    where_clause = " where " + " and ".join(filtros)
    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) as total from api_ans.api_operadora {where_clause}"),
            params,
        )
        total = int(total_result.scalar_one())

        result = await session.execute(
            text(
                f"""
                select
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia_referencia,
                    score_final,
                    rating,
                    versao_score
                from api_ans.api_operadora
                {where_clause}
                order by score_final desc nulls last, nome
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()
        competencia = rows[0]["competencia_referencia"] if rows else "atual"
        meta_dataset = await _resolver_meta_dataset(
            session,
            "sib_operadora",
            competencia or "atual",
        )

    dados = [OperadoraResumoResponse(**row).model_dump() for row in rows]
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


async def detalhar_operadora(registro_ans: str) -> dict:
    cache_key = f"operadora:{registro_ans}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia_referencia,
                    score_final,
                    rating,
                    versao_score
                from api_ans.api_operadora
                where registro_ans = :registro_ans
                limit 1
                """
            ),
            {"registro_ans": registro_ans.zfill(6)},
        )
        row = result.mappings().first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "OPERADORA_NAO_ENCONTRADA",
                    "mensagem": "Registro ANS nao encontrado na camada de servico.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(
            session, "sib_operadora", row["competencia_referencia"] or "atual"
        )

    payload = {
        "dados": [OperadoraResumoResponse(**row).model_dump()],
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


async def detalhar_score_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
) -> dict:
    cache_key = f"score:{registro_ans}:{competencia or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    filtro_competencia = ""
    params = {"registro_ans": registro_ans.zfill(6)}
    if competencia:
        filtro_competencia = "and competencia = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    registro_ans,
                    competencia,
                    nome,
                    modalidade,
                    uf_sede,
                    score_final,
                    rating,
                    score_crescimento,
                    score_qualidade,
                    score_estabilidade,
                    score_presenca,
                    versao_score
                from api_ans.api_score_operadora_mensal
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
                    "codigo_erro": "SCORE_NAO_ENCONTRADO",
                    "mensagem": "Score nao encontrado para o registro ANS informado.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(session, "sib_operadora", row["competencia"])

    payload = {
        "dados": [OperadoraScoreResponse(**row).model_dump()],
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
