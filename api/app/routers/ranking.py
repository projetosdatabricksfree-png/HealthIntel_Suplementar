from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.ranking import (
    listar_ranking_composto,
    listar_ranking_crescimento,
    listar_ranking_oportunidade,
    listar_ranking_oportunidade_v2,
    listar_ranking_score,
)

router = APIRouter(
    prefix="/rankings",
    tags=["ranking"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/operadora/score")
async def get_ranking_score(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_ranking_score(pagina=pagina, por_pagina=por_pagina)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/operadora/crescimento")
async def get_ranking_crescimento(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_ranking_crescimento(pagina=pagina, por_pagina=por_pagina)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/municipio/oportunidade")
async def get_ranking_oportunidade(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_ranking_oportunidade(pagina=pagina, por_pagina=por_pagina)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/municipio/oportunidade-v2")
async def get_ranking_oportunidade_v2(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_ranking_oportunidade_v2(pagina=pagina, por_pagina=por_pagina)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/composto")
async def get_ranking_composto(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    modalidade: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_ranking_composto(
        pagina=pagina,
        por_pagina=por_pagina,
        competencia=competencia,
        modalidade=modalidade,
        uf=uf,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
