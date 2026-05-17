import os

from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.financeiro_v2 import (
    detalhar_financeiro_operadora,
    detalhar_score_v2_operadora,
)

# Release 0.9 manteve a flag para endpoints vazios; financeiro por operadora
# tem fonte consumo_ans com cobertura auditavel e permanece publicado.
_SHOW_EMPTY = os.getenv("HEALTHINTEL_RELEASE_0_9_HIDE_EMPTY", "1") != "1"

router = APIRouter(
    prefix="/operadoras",
    tags=["financeiro-v2"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/{registro_ans}/financeiro")
async def get_financeiro(
    registro_ans: str,
    request: Request,
    trimestre: str | None = Query(default=None, min_length=6, max_length=6),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await detalhar_financeiro_operadora(
        registro_ans,
        competencia=trimestre or competencia,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
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
