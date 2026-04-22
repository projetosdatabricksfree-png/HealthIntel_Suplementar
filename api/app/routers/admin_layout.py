import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from api.app.middleware.autenticacao import validar_api_key
from api.app.schemas.layout_admin import (
    LayoutAliasCreate,
    LayoutCreate,
    LayoutReprocessamentoRequest,
    LayoutStatusUpdateRequest,
    LayoutValidacaoArquivoRequest,
    LayoutVersaoCreate,
)
from api.app.services.layout_admin import (
    atualizar_status_layout,
    criar_alias,
    criar_layout,
    criar_versao_layout,
    listar_layouts,
    listar_layouts_incompativeis,
    obter_layout,
    reprocessar_layout,
    validar_arquivo_layout,
)

router = APIRouter(
    prefix="/admin/layouts", tags=["admin-layout"], dependencies=[Depends(validar_api_key)]
)


@router.post("")
async def post_layout(payload: LayoutCreate) -> dict:
    try:
        return await criar_layout(payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/{layout_id}/versoes")
async def post_layout_versao(layout_id: str, payload: LayoutVersaoCreate) -> dict:
    try:
        return await criar_versao_layout(layout_id, payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/{layout_id}/aliases")
async def post_layout_alias(layout_id: str, payload: LayoutAliasCreate) -> dict:
    try:
        return await criar_alias(layout_id, payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.get("")
async def get_layouts(dataset_codigo: str | None = Query(default=None)) -> dict:
    try:
        return await listar_layouts(dataset_codigo=dataset_codigo)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.get("/incompativeis")
async def get_layouts_incompativeis() -> dict:
    try:
        return await listar_layouts_incompativeis()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.get("/{layout_id}")
async def get_layout(layout_id: str) -> dict:
    try:
        return await obter_layout(layout_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/validar-arquivo")
async def post_validar_arquivo(payload: LayoutValidacaoArquivoRequest) -> dict:
    try:
        return await validar_arquivo_layout(payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/{layout_id}/aprovar")
async def post_aprovar_layout(layout_id: str, payload: LayoutStatusUpdateRequest) -> dict:
    try:
        payload.status = "ativo"
        return await atualizar_status_layout(layout_id, payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/{layout_id}/desativar")
async def post_desativar_layout(layout_id: str, payload: LayoutStatusUpdateRequest) -> dict:
    try:
        payload.status = "inativo"
        return await atualizar_status_layout(layout_id, payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/{layout_id}/reativar")
async def post_reativar_layout(layout_id: str, payload: LayoutStatusUpdateRequest) -> dict:
    try:
        payload.status = "ativo"
        return await atualizar_status_layout(layout_id, payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc


@router.post("/reprocessar")
async def post_reprocessar_layout(payload: LayoutReprocessamentoRequest) -> dict:
    try:
        return await reprocessar_layout(payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.json().get("detail")
        ) from exc
