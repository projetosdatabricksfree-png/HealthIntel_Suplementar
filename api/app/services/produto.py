from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.schemas.meta import MetaEnvelope


def _normalizar_paginacao(pagina: int, por_pagina: int) -> tuple[int, int, int]:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    return pagina, por_pagina, (pagina - 1) * por_pagina


async def listar_produtos_planos(
    *,
    registro_ans: str | None = None,
    codigo_plano: str | None = None,
    segmentacao: str | None = None,
    tipo_contratacao: str | None = None,
    situacao: str | None = None,
    competencia: int | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina, por_pagina, offset = _normalizar_paginacao(pagina, por_pagina)
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if registro_ans:
        filtros.append("registro_ans = :registro_ans")
        params["registro_ans"] = registro_ans.zfill(6)
    if codigo_plano:
        filtros.append("(codigo_plano = :codigo_plano or codigo_produto = :codigo_plano)")
        params["codigo_plano"] = codigo_plano
    if segmentacao:
        filtros.append("segmentacao ilike :segmentacao")
        params["segmentacao"] = f"%{segmentacao.strip()}%"
    if tipo_contratacao:
        filtros.append("tipo_contratacao ilike :tipo_contratacao")
        params["tipo_contratacao"] = f"%{tipo_contratacao.strip()}%"
    if situacao:
        filtros.append("situacao_plano ilike :situacao")
        params["situacao"] = f"%{situacao.strip()}%"
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = competencia
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_produto_plano {where_clause}"),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    registro_ans,
                    codigo_produto,
                    codigo_plano,
                    nome_produto,
                    segmentacao,
                    tipo_contratacao,
                    abrangencia_geografica,
                    cobertura_area,
                    modalidade,
                    uf_comercializacao,
                    competencia,
                    situacao_plano,
                    data_situacao,
                    competencia_historico
                from api_ans.api_produto_plano
                {where_clause}
                order by competencia desc nulls last, registro_ans, codigo_produto
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    return {
        "dados": [dict(row) for row in rows],
        "meta": MetaEnvelope(
            competencia_referencia=str(rows[0]["competencia"]) if rows else "atual",
            versao_dataset="produto_plano_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }


async def detalhar_produto_plano(codigo_plano: str) -> dict:
    payload = await listar_produtos_planos(codigo_plano=codigo_plano, pagina=1, por_pagina=20)
    if not payload["dados"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "codigo_erro": "PLANO_NAO_ENCONTRADO",
                "mensagem": "Plano/produto nao encontrado na camada de servico.",
            },
        )
    return payload


async def listar_historico_planos(
    *,
    registro_ans: str | None = None,
    codigo_plano: str | None = None,
    situacao: str | None = None,
    competencia: int | None = None,
    pagina: int = 1,
    por_pagina: int = 50,
) -> dict:
    pagina, por_pagina, offset = _normalizar_paginacao(pagina, por_pagina)
    params: dict[str, object] = {"limit": por_pagina, "offset": offset}
    filtros = ["1=1"]
    if registro_ans:
        filtros.append("registro_ans = :registro_ans")
        params["registro_ans"] = registro_ans.zfill(6)
    if codigo_plano:
        filtros.append("codigo_plano = :codigo_plano")
        params["codigo_plano"] = codigo_plano
    if situacao:
        filtros.append("situacao ilike :situacao")
        params["situacao"] = f"%{situacao.strip()}%"
    if competencia:
        filtros.append("competencia = :competencia")
        params["competencia"] = competencia
    where_clause = " where " + " and ".join(filtros)

    async with SessionLocal() as session:
        total_result = await session.execute(
            text(f"select count(*) from api_ans.api_historico_plano {where_clause}"),
            params,
        )
        total = int(total_result.scalar_one())
        result = await session.execute(
            text(
                f"""
                select
                    registro_ans,
                    codigo_plano,
                    nome_plano,
                    situacao,
                    data_situacao,
                    segmentacao,
                    tipo_contratacao,
                    abrangencia_geografica,
                    uf,
                    competencia
                from api_ans.api_historico_plano
                {where_clause}
                order by competencia desc nulls last, registro_ans, codigo_plano
                limit :limit offset :offset
                """
            ),
            params,
        )
        rows = result.mappings().all()

    return {
        "dados": [dict(row) for row in rows],
        "meta": MetaEnvelope(
            competencia_referencia=str(rows[0]["competencia"]) if rows else "atual",
            versao_dataset="historico_plano_v1",
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
        ).model_dump(),
    }
