from fastapi import APIRouter

from api.app.services.meta import (
    listar_datasets,
    listar_endpoints,
    listar_pipeline,
    listar_versoes,
)

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/dataset")
async def get_datasets() -> dict:
    return await listar_datasets()


@router.get("/versao")
async def get_versoes() -> dict:
    return await listar_versoes()


@router.get("/pipeline")
async def get_pipeline() -> dict:
    return await listar_pipeline()


@router.get("/endpoints")
async def get_endpoints() -> dict:
    return await listar_endpoints()
