from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.regulatorio_v2 import (
    detalhar_score_regulatorio_operadora,
    listar_portabilidade_operadora,
    listar_regime_especial_operadora,
)

router = APIRouter(
    prefix="/operadoras",
    tags=["regulatorio-v2"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/{registro_ans}/score-regulatorio")
async def get_score_regulatorio(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_score_regulatorio_operadora(registro_ans, competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/regime-especial")
async def get_regime_especial(
    registro_ans: str,
    request: Request,
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_regime_especial_operadora(registro_ans)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/portabilidade")
async def get_portabilidade(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_portabilidade_operadora(
        registro_ans,
        competencia=competencia,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
