from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.mercado import listar_mercado_municipio, listar_vazios_assistenciais

router = APIRouter(
    prefix="/mercado",
    tags=["mercado"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/municipio")
async def get_mercado_municipio(
    request: Request,
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    segmento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_mercado_municipio(
        uf=uf,
        competencia=competencia,
        segmento=segmento,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/vazio-assistencial")
async def get_vazio_assistencial(
    request: Request,
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    segmento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_vazios_assistenciais(
        uf=uf,
        segmento=segmento,
        competencia=competencia,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
