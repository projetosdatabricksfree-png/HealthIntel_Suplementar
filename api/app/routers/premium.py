from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_camada
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.schemas.premium import (
    PremiumCnesEstabelecimentoValidadoResponse,
    PremiumOperadora360ValidadoResponse,
    PremiumQualityDatasetResponse,
)
from api.app.services.premium import buscar_premium

router = APIRouter(
    prefix="/premium",
    tags=["premium"],
    dependencies=[Depends(validar_api_key), Depends(verificar_camada("premium"))],
)


async def _executar_premium(
    request: Request,
    dataset: str,
    *,
    filtros: dict[str, object] | None = None,
    pagina: int,
    limite: int,
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_premium(dataset, filtros=filtros, pagina=pagina, limite=limite)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/operadoras", response_model=PremiumOperadora360ValidadoResponse)
async def get_premium_operadoras(
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    uf: str | None = Query(default=None, min_length=2, max_length=2),
    modalidade: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "competencia": competencia,
        "registro_ans": registro_ans,
        "uf": uf,
        "modalidade": modalidade,
    }
    return await _executar_premium(
        request,
        "operadora_360_validado",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/cnes/estabelecimentos", response_model=PremiumCnesEstabelecimentoValidadoResponse)
async def get_premium_cnes_estabelecimentos(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    cnes: str | None = Query(default=None),
    cd_municipio: str | None = Query(default=None),
    sg_uf: str | None = Query(default=None, min_length=2, max_length=2),
    tipo_unidade: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "competencia": competencia,
        "cnes": cnes,
        "cd_municipio": cd_municipio,
        "sg_uf": sg_uf,
        "tipo_unidade": tipo_unidade,
    }
    return await _executar_premium(
        request,
        "cnes_estabelecimento_validado",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/quality/datasets", response_model=PremiumQualityDatasetResponse)
async def get_premium_quality_datasets(
    request: Request,
    fonte_documento: str | None = Query(default=None),
    documento_quality_status: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "fonte_documento": fonte_documento,
        "documento_quality_status": documento_quality_status,
    }
    return await _executar_premium(
        request,
        "quality_dataset",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )
