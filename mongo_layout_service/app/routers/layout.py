from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from mongo_layout_service.app.core.database import get_database
from mongo_layout_service.app.core.exceptions import LayoutRegistryError
from mongo_layout_service.app.core.security import validar_service_token
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
    ReprocessamentoRequest,
    StatusLayoutUpdateRequest,
    ValidacaoArquivoRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService

router = APIRouter(prefix="/layout", tags=["layout"], dependencies=[Depends(validar_service_token)])


def get_layout_service() -> LayoutService:
    repository = LayoutRepository(get_database())
    return LayoutService(repository)


LayoutServiceDep = Annotated[LayoutService, Depends(get_layout_service)]


@router.get("/datasets")
async def get_datasets(service: LayoutServiceDep) -> dict:
    return {"dados": await service.listar_datasets()}


@router.get("/layouts")
async def get_layouts(
    service: LayoutServiceDep,
    dataset_codigo: str | None = Query(default=None),
) -> dict:
    return {"dados": await service.listar_layouts(dataset_codigo=dataset_codigo)}


@router.post("/layouts")
async def post_layout(payload: LayoutCreate, service: LayoutServiceDep) -> dict:
    try:
        return await service.criar_layout(payload)
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.get("/layouts/{layout_id}")
async def get_layout(layout_id: str, service: LayoutServiceDep) -> dict:
    try:
        return {"dados": await service.obter_layout(layout_id)}
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.get("/layouts/{layout_id}/versoes")
async def get_layout_versoes(layout_id: str, service: LayoutServiceDep) -> dict:
    try:
        return {"dados": await service.listar_versoes(layout_id)}
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.post("/layouts/{layout_id}/versoes")
async def post_layout_versao(
    layout_id: str,
    payload: LayoutVersaoCreate,
    service: LayoutServiceDep,
) -> dict:
    try:
        return await service.criar_versao_layout(layout_id, payload)
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.post("/layouts/{layout_id}/aliases")
async def post_layout_alias(
    layout_id: str,
    payload: LayoutAliasCreate,
    service: LayoutServiceDep,
) -> dict:
    try:
        return await service.criar_alias(layout_id, payload)
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.post("/layouts/{layout_id}/status")
async def post_layout_status(
    layout_id: str,
    payload: StatusLayoutUpdateRequest,
    service: LayoutServiceDep,
) -> dict:
    try:
        return await service.atualizar_status_layout(layout_id, payload)
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.get("/incompativeis")
async def get_layouts_incompativeis(service: LayoutServiceDep) -> dict:
    return {"dados": await service.listar_incompativeis()}


@router.post("/reprocessar")
async def post_reprocessar(
    payload: ReprocessamentoRequest,
    service: LayoutServiceDep,
) -> dict:
    try:
        return await service.reprocessar(payload)
    except LayoutRegistryError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail={"codigo_erro": exc.code, "mensagem": exc.message}
        ) from exc


@router.post("/validar-arquivo")
async def post_validar_arquivo(
    payload: ValidacaoArquivoRequest,
    service: LayoutServiceDep,
) -> dict:
    return await service.validar_arquivo(payload)
