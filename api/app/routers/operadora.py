from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.operadora import (
    detalhar_operadora,
    detalhar_score_operadora,
    listar_operadoras,
)
from api.app.services.rede import detalhar_rede_operadora
from api.app.services.regulatorio import detalhar_regulatorio_operadora
from api.app.services.score_v3 import buscar_historico_score_v3, buscar_score_v3_operadora

router = APIRouter(
    prefix="/operadoras",
    tags=["operadoras"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
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


@router.get("/{registro_ans}/rede")
async def get_operadora_rede(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    segmento: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_rede_operadora(
        registro_ans,
        competencia=competencia,
        segmento=segmento,
        uf=uf,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/score-v3")
async def get_operadora_score_v3(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_score_v3_operadora(registro_ans, competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/score-v3/historico")
async def get_operadora_score_v3_historico(
    registro_ans: str,
    request: Request,
    periodos: int = Query(default=12, ge=1, le=24),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_historico_score_v3(registro_ans, periodos=periodos)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
