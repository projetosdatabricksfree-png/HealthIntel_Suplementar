from fastapi import APIRouter, Depends, Query, Request

from api.app.dependencia import verificar_camada, verificar_plano
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.prata import (
    buscar_prata,
    buscar_quarentena_dataset,
    buscar_quarentena_resumo,
)

router = APIRouter(
    prefix="/prata",
    tags=["prata"],
    dependencies=[Depends(validar_api_key), Depends(verificar_plano)],
)


async def _executar_prata(
    request: Request,
    dataset: str,
    *,
    competencia: str,
    filtros: dict[str, object] | None = None,
    pagina: int,
    limite: int,
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_prata(
        dataset,
        competencia=competencia,
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/cadop", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_cadop(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "cadop",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/sib/operadora", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_sib_operadora(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "sib_operadora",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/sib/municipio", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_sib_municipio(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    cd_municipio: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros: dict[str, object] = {}
    if registro_ans:
        filtros["registro_ans"] = registro_ans.zfill(6)
    if cd_municipio:
        filtros["codigo_ibge"] = "".join(filter(str.isdigit, cd_municipio)).zfill(7)
    return await _executar_prata(
        request,
        "sib_municipio",
        competencia=competencia,
        filtros=filtros or None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/igr", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_igr(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "igr",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/nip", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_nip(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "nip",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/idss", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_idss(
    request: Request,
    competencia: str = Query(..., min_length=4, max_length=4),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "idss",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/diops", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_diops(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "diops",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/fip", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_fip(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "fip",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/vda", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_vda(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "vda",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/glosa", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_glosa(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    tipo_glosa: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros: dict[str, object] = {}
    if registro_ans:
        filtros["registro_ans"] = registro_ans.zfill(6)
    if tipo_glosa:
        filtros["tipo_glosa"] = tipo_glosa
    return await _executar_prata(
        request,
        "glosa",
        competencia=competencia,
        filtros=filtros or None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/rede-assistencial", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_rede_assistencial(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    cd_municipio: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros: dict[str, object] = {}
    if registro_ans:
        filtros["registro_ans"] = registro_ans.zfill(6)
    if cd_municipio:
        filtros["cd_municipio"] = "".join(filter(str.isdigit, cd_municipio)).zfill(7)
    return await _executar_prata(
        request,
        "rede_assistencial",
        competencia=competencia,
        filtros=filtros or None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/operadora/enriquecida", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_operadora_enriquecida(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "operadora_enriquecida",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/municipio/metrica", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_municipio_metrica(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    cd_municipio: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = (
        {"cd_municipio": "".join(filter(str.isdigit, cd_municipio)).zfill(7)}
        if cd_municipio
        else None
    )
    return await _executar_prata(
        request,
        "municipio_metrica",
        competencia=competencia,
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/financeiro/periodo", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_financeiro_periodo(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    return await _executar_prata(
        request,
        "financeiro_periodo",
        competencia=competencia,
        filtros={"registro_ans": registro_ans.zfill(6)} if registro_ans else None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/cnes/municipio", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_cnes_municipio(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    cd_municipio: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros = (
        {"cd_municipio": "".join(filter(str.isdigit, cd_municipio)).zfill(7)}
        if cd_municipio
        else None
    )
    return await _executar_prata(
        request,
        "cnes_municipio",
        competencia=competencia,
        filtros=filtros,
        pagina=pagina,
        limite=limite,
    )


@router.get("/cnes/rede-gap", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_cnes_rede_gap(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    cd_municipio: str | None = Query(default=None),
    registro_ans: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros: dict[str, object] = {}
    if cd_municipio:
        filtros["cd_municipio"] = "".join(filter(str.isdigit, cd_municipio)).zfill(7)
    if registro_ans:
        filtros["registro_ans"] = registro_ans.zfill(6)
    return await _executar_prata(
        request,
        "cnes_rede_gap",
        competencia=competencia,
        filtros=filtros or None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/tiss/procedimento", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_tiss_procedimento(
    request: Request,
    competencia: str = Query(..., min_length=5),
    registro_ans: str | None = Query(default=None),
    cd_procedimento_tuss: str | None = Query(default=None),
    grupo_procedimento: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    filtros: dict[str, object] = {}
    if registro_ans:
        filtros["registro_ans"] = registro_ans.zfill(6)
    if cd_procedimento_tuss:
        filtros["cd_procedimento_tuss"] = cd_procedimento_tuss
    if grupo_procedimento:
        filtros["grupo_procedimento"] = grupo_procedimento
    return await _executar_prata(
        request,
        "tiss_procedimento",
        competencia=competencia,
        filtros=filtros or None,
        pagina=pagina,
        limite=limite,
    )


@router.get("/quarentena/resumo", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_quarentena_resumo(
    request: Request,
    competencia: str | None = Query(default=None),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_quarentena_resumo(competencia=competencia)
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload


@router.get("/quarentena/{dataset}", dependencies=[Depends(verificar_camada("prata"))])
async def get_prata_quarentena_dataset(
    dataset: str,
    request: Request,
    competencia: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
) -> dict:
    await aplicar_rate_limit(request)
    payload = await buscar_quarentena_dataset(
        dataset,
        competencia=competencia,
        pagina=pagina,
        limite=limite,
    )
    request.state.cache_status = payload.get("meta", {}).get("cache", "miss")
    return payload
