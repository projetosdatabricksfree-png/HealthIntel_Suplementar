from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.cnes import listar_cnes_municipio, listar_cnes_uf

router = APIRouter(
    prefix="/cnes",
    tags=["cnes"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/municipio/{cd_municipio}")
async def get_cnes_municipio(
    cd_municipio: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    tipo_unidade: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_cnes_municipio(
        cd_municipio,
        competencia=competencia,
        tipo_unidade=tipo_unidade,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/uf/{sg_uf}")
async def get_cnes_uf(
    sg_uf: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    tipo_unidade: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_cnes_uf(
        sg_uf,
        competencia=competencia,
        tipo_unidade=tipo_unidade,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
