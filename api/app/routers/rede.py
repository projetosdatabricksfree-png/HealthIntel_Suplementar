from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.rede import listar_rede_municipio

router = APIRouter(
    prefix="/rede",
    tags=["rede"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/municipio/{cd_municipio}")
async def get_rede_municipio(
    cd_municipio: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    segmento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_rede_municipio(
        cd_municipio,
        competencia=competencia,
        segmento=segmento,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
