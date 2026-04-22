from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.financeiro_v2 import (
    detalhar_financeiro_operadora,
    detalhar_score_v2_operadora,
)

router = APIRouter(
    prefix="/operadoras",
    tags=["financeiro-v2"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/{registro_ans}/financeiro")
async def get_financeiro(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_financeiro_operadora(registro_ans, competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/{registro_ans}/score-v2")
async def get_score_v2(
    registro_ans: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_score_v2_operadora(registro_ans, competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
