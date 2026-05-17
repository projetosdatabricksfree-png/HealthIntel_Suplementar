from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.comercial import (
    listar_financeiro,
    listar_glosa,
    listar_historico_planos,
    listar_idss,
    listar_igr,
    listar_nip,
    listar_produtos_planos,
    listar_prudencial,
    listar_regime_especial,
    listar_regulatorio,
)

router = APIRouter(
    tags=["comercial"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/produtos-planos")
async def get_produtos_planos(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    competencia: int | None = Query(default=None),
    competencia_inicio: int | None = Query(default=None),
    competencia_fim: int | None = Query(default=None),
    situacao_plano: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_produtos_planos(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
        situacao_plano=situacao_plano,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/historico-planos")
async def get_historico_planos(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    competencia: int | None = Query(default=None),
    competencia_inicio: int | None = Query(default=None),
    competencia_fim: int | None = Query(default=None),
    situacao: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_historico_planos(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
        situacao=situacao,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/regulatorio")
async def get_regulatorio(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
    nivel_alerta: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_regulatorio(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
        nivel_alerta=nivel_alerta,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/igr")
async def get_igr(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_igr(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/nip")
async def get_nip(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_nip(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/idss")
async def get_idss(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    ano_base: int | None = Query(default=None),
    ano_inicio: int | None = Query(default=None),
    ano_fim: int | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_idss(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        ano_base=ano_base,
        ano_inicio=ano_inicio,
        ano_fim=ano_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/financeiro")
async def get_financeiro(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_financeiro(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/prudencial")
async def get_prudencial(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_prudencial(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/regime-especial")
async def get_regime_especial(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    trimestre: str | None = Query(default=None),
    trimestre_inicio: str | None = Query(default=None),
    trimestre_fim: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_regime_especial(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/glosa")
async def get_glosa(
    request: Request,
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=50, ge=1, le=100),
    page: int | None = Query(default=None, ge=1),
    per_page: int | None = Query(default=None, ge=1, le=100),
    registro_ans: str | None = Query(default=None),
    competencia: int | None = Query(default=None),
    competencia_inicio: int | None = Query(default=None),
    competencia_fim: int | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await listar_glosa(
        pagina=page or pagina,
        por_pagina=per_page or por_pagina,
        registro_ans=registro_ans,
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
