from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_camada
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.bronze import buscar_bronze

router = APIRouter(
    prefix="/bronze",
    tags=["bronze"],
    dependencies=[Depends(validar_api_key)],
)


async def _executar_bronze(
    request: Request,
    dataset: str,
    *,
    competencia: str,
    lote_id: str | None,
    pagina: int,
    limite: int,
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_bronze(
        dataset,
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/cadop", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_cadop(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "cadop",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/sib/operadora", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_sib_operadora(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "sib_operadora",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/sib/municipio", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_sib_municipio(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "sib_municipio",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/igr", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_igr(
    request: Request,
    competencia: str = Query(..., min_length=5),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "igr",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/nip", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_nip(
    request: Request,
    competencia: str = Query(..., min_length=5),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "nip",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/idss", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_idss(
    request: Request,
    competencia: str = Query(..., min_length=4, max_length=4),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "idss",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/diops", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_diops(
    request: Request,
    competencia: str = Query(..., min_length=5),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "diops",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/fip", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_fip(
    request: Request,
    competencia: str = Query(..., min_length=5),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "fip",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/vda", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_vda(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "vda",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/glosa", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_glosa(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "glosa",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )


@router.get("/rede-assistencial", dependencies=[Depends(verificar_camada("bronze"))])
async def get_bronze_rede_assistencial(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    lote_id: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_bronze(
        request,
        "rede_assistencial",
        competencia=competencia,
        lote_id=lote_id,
        pagina=pagina,
        limite=limite,
    )
