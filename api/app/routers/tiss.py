from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.tiss import (
    listar_gap_rede_municipio,
    listar_sinistralidade_procedimento,
    listar_tiss_procedimentos,
)

router = APIRouter(
    tags=["tiss", "rede"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/tiss/{registro_ans}/procedimentos")
async def get_tiss_procedimentos(
    registro_ans: str,
    request: Request,
    trimestre: str | None = Query(default=None, min_length=6),
    grupo_procedimento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_tiss_procedimentos(
        registro_ans,
        trimestre=trimestre,
        grupo_procedimento=grupo_procedimento,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/tiss/{registro_ans}/sinistralidade")
async def get_tiss_sinistralidade(
    registro_ans: str,
    request: Request,
    trimestre: str | None = Query(default=None, min_length=6),
    grupo_procedimento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_sinistralidade_procedimento(
        registro_ans,
        trimestre=trimestre,
        grupo_procedimento=grupo_procedimento,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/rede/gap/{cd_municipio}")
async def get_gap_rede(
    cd_municipio: str,
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    tipo_unidade: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_gap_rede_municipio(
        cd_municipio,
        competencia=competencia,
        tipo_unidade=tipo_unidade,
        pagina=pagina,
        por_pagina=por_pagina,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
