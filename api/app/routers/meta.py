from fastapi import APIRouter

from api.app.services.meta import (
    listar_atualizacao,
    listar_datasets,
    listar_endpoints,
    listar_pipeline,
    listar_qualidade,
    listar_versoes,
)

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/datasets")
async def get_datasets_plural() -> dict:
    return await listar_datasets()


@router.get("/dataset")
async def get_datasets() -> dict:
    return await listar_datasets()


@router.get("/atualizacao")
async def get_atualizacao() -> dict:
    return await listar_atualizacao()


@router.get("/qualidade")
async def get_qualidade() -> dict:
    return await listar_qualidade()


@router.get("/versao")
async def get_versoes() -> dict:
    return await listar_versoes()


@router.get("/pipeline")
async def get_pipeline() -> dict:
    return await listar_pipeline()


@router.get("/endpoints")
async def get_endpoints() -> dict:
    return await listar_endpoints()
