from fastapi import APIRouter, Depends, Query, Request

from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.regulatorio import listar_rn623

router = APIRouter(
    prefix="/regulatorio",
    tags=["regulatorio"],
    dependencies=[Depends(validar_api_key)],
)


@router.get("/rn623")
async def get_rn623(
    request: Request,
    trimestre: str | None = Query(default=None, min_length=6, max_length=6),
    tipo_lista: str | None = Query(default=None, pattern="^(excelencia|reducao)$"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_rn623(
        trimestre=trimestre,
        tipo_lista=tipo_lista,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
