from fastapi import APIRouter, Depends, Query, Request

from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.operadora import (
    detalhar_operadora,
    detalhar_score_operadora,
    listar_operadoras,
)
from api.app.services.regulatorio import detalhar_regulatorio_operadora

router = APIRouter(
    prefix="/operadoras",
    tags=["operadoras"],
    dependencies=[Depends(validar_api_key)],
)


@router.get("")
async def get_operadoras(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    busca: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    modalidade: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_operadoras(
        pagina=pagina,
        por_pagina=por_pagina,
        busca=busca,
        uf=uf,
        modalidade=modalidade,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}")
async def get_operadora(registro_ans: str, request: Request) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_operadora(registro_ans)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/score")
async def get_operadora_score(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_score_operadora(registro_ans, competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/regulatorio")
async def get_operadora_regulatorio(
    registro_ans: str,
    request: Request,
    trimestre: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_regulatorio_operadora(registro_ans, trimestre=trimestre)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
