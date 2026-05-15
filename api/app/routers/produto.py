from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.produto import (
    detalhar_produto_plano,
    listar_historico_planos,
    listar_produtos_planos,
)

router = APIRouter(
    prefix="/produtos",
    tags=["produtos"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


@router.get("/planos")
async def get_produtos_planos(
    request: Request,
    registro_ans: str | None = Query(default=None),
    codigo_plano: str | None = Query(default=None),
    segmentacao: str | None = Query(default=None),
    tipo_contratacao: str | None = Query(default=None),
    situacao: str | None = Query(default=None),
    competencia: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    return await listar_produtos_planos(
        registro_ans=registro_ans,
        codigo_plano=codigo_plano,
        segmentacao=segmentacao,
        tipo_contratacao=tipo_contratacao,
        situacao=situacao,
        competencia=competencia,
        pagina=page,
        por_pagina=per_page,
    )


@router.get("/planos/{codigo_plano}")
async def get_produto_plano(codigo_plano: str, request: Request) -> dict:
    await aplicar_rate_limit(request)
    return await detalhar_produto_plano(codigo_plano)


@router.get("/historico")
async def get_historico_planos(
    request: Request,
    registro_ans: str | None = Query(default=None),
    codigo_plano: str | None = Query(default=None),
    situacao: str | None = Query(default=None),
    competencia: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    return await listar_historico_planos(
        registro_ans=registro_ans,
        codigo_plano=codigo_plano,
        situacao=situacao,
        competencia=competencia,
        pagina=page,
        por_pagina=per_page,
    )
