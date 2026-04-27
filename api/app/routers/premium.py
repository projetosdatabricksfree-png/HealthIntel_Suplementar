from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.app.dependencia import verificar_camada
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.schemas.premium import (
    PremiumCnesEstabelecimentoValidadoResponse,
    PremiumContratoResponse,
    PremiumMdmOperadoraResponse,
    PremiumMdmPrestadorResponse,
    PremiumOperadora360ValidadoResponse,
    PremiumQualityDatasetResponse,
    PremiumSubfaturaResponse,
    PremiumTissProcedimentoResponse,
    PremiumTussProcedimentoResponse,
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
    tenant_id: str | None = None,
) -> dict:
    await aplicar_rate_limit(request)

    # Tenant obrigatório para datasets privados (validado no service também)
    if tenant_id is None:
        # Tenta extrair do request state se disponível
        tenant_id = getattr(request.state, "cliente_id", None)

    try:
        payload = await buscar_premium(
            dataset,
            filtros=filtros,
            pagina=pagina,
            limite=limite,
            tenant_id=tenant_id,
        )
    except ValueError as exc:
        if "tenant_id obrigatorio" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "codigo": "TENANT_OBRIGATORIO",
                    "mensagem": "Dataset privado exige tenant autenticado.",
                },
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"codigo": "ERRO_PREMIUM", "mensagem": str(exc)},
        ) from exc

    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


# ---------------------------------------------------------------------------
# Rotas públicas (dados públicos ANS — não exigem tenant)
# ---------------------------------------------------------------------------


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


@router.get("/tiss/procedimentos", response_model=PremiumTissProcedimentoResponse)
async def get_premium_tiss_procedimentos(
    request: Request,
    trimestre: str | None = Query(default=None, min_length=5),
    registro_ans: str | None = Query(default=None),
    cd_procedimento_tuss: str | None = Query(default=None),
    grupo_desc: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "trimestre": trimestre,
        "registro_ans": registro_ans,
        "cd_procedimento_tuss": cd_procedimento_tuss,
        "grupo_desc": grupo_desc,
    }
    return await _executar_premium(
        request,
        "tiss_procedimento_tuss_validado",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/tuss/procedimentos", response_model=PremiumTussProcedimentoResponse)
async def get_premium_tuss_procedimentos(
    request: Request,
    codigo_tuss: str | None = Query(default=None),
    versao_tuss: str | None = Query(default=None),
    grupo: str | None = Query(default=None),
    is_tuss_vigente: bool | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "codigo_tuss": codigo_tuss,
        "versao_tuss": versao_tuss,
        "grupo": grupo,
        "is_tuss_vigente": is_tuss_vigente,
    }
    return await _executar_premium(
        request,
        "tuss_procedimento",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/mdm/operadoras", response_model=PremiumMdmOperadoraResponse)
async def get_premium_mdm_operadoras(
    request: Request,
    registro_ans_canonico: str | None = Query(default=None),
    status_mdm: str | None = Query(default=None),
    uf_canonica: str | None = Query(default=None, min_length=2, max_length=2),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "registro_ans_canonico": registro_ans_canonico,
        "status_mdm": status_mdm,
        "uf_canonica": uf_canonica,
    }
    return await _executar_premium(
        request,
        "mdm_operadora",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/mdm/prestadores", response_model=PremiumMdmPrestadorResponse)
async def get_premium_mdm_prestadores(
    request: Request,
    cnes_canonico: str | None = Query(default=None),
    status_mdm: str | None = Query(default=None),
    uf_canonica: str | None = Query(default=None, min_length=2, max_length=2),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = {
        "cnes_canonico": cnes_canonico,
        "status_mdm": status_mdm,
        "uf_canonica": uf_canonica,
    }
    return await _executar_premium(
        request,
        "mdm_prestador",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


# ---------------------------------------------------------------------------
# Rotas privadas (dados por tenant — exigem tenant_id autenticado)
# ---------------------------------------------------------------------------


def _obter_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "cliente_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "codigo": "TENANT_OBRIGATORIO",
                "mensagem": "Dataset privado exige tenant autenticado.",
            },
        )
    return str(tenant_id)


@router.get("/contratos", response_model=PremiumContratoResponse)
async def get_premium_contratos(
    request: Request,
    numero_contrato_normalizado: str | None = Query(default=None),
    status_contrato: str | None = Query(default=None),
    registro_ans_canonico: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    tenant_id = _obter_tenant_id(request)
    filtros = {
        "tenant_id": tenant_id,
        "numero_contrato_normalizado": numero_contrato_normalizado,
        "status_contrato": status_contrato,
        "registro_ans_canonico": registro_ans_canonico,
    }
    return await _executar_premium(
        request,
        "contrato_validado",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
        tenant_id=tenant_id,
    )


@router.get("/subfaturas", response_model=PremiumSubfaturaResponse)
async def get_premium_subfaturas(
    request: Request,
    competencia: str | None = Query(default=None, min_length=6, max_length=6),
    contrato_master_id: str | None = Query(default=None),
    status_subfatura: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    tenant_id = _obter_tenant_id(request)
    filtros = {
        "tenant_id": tenant_id,
        "competencia": competencia,
        "contrato_master_id": contrato_master_id,
        "status_subfatura": status_subfatura,
    }
    return await _executar_premium(
        request,
        "subfatura_validada",
        filtros=filtros,
        pagina=pagina,
        limite=limite,
        tenant_id=tenant_id,
    )


# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------


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