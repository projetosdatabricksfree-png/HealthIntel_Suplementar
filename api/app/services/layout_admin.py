import httpx

from api.app.core.config import get_settings
from api.app.schemas.layout_admin import (
    LayoutAliasCreate,
    LayoutCreate,
    LayoutReprocessamentoRequest,
    LayoutStatusUpdateRequest,
    LayoutValidacaoArquivoRequest,
    LayoutVersaoCreate,
)

settings = get_settings()


async def _request_layout_service(
    method: str, path: str, payload: dict | None = None, params: dict | None = None
) -> dict:
    async with httpx.AsyncClient(
        base_url=settings.layout_service_url,
        timeout=20.0,
        headers={"X-Service-Token": settings.layout_service_token},
    ) as client:
        response = await client.request(method, path, json=payload, params=params)
    response.raise_for_status()
    return response.json()


async def criar_layout(payload: LayoutCreate) -> dict:
    return await _request_layout_service("POST", "/layout/layouts", payload=payload.model_dump())


async def listar_layouts(dataset_codigo: str | None = None) -> dict:
    return await _request_layout_service(
        "GET",
        "/layout/layouts",
        params={"dataset_codigo": dataset_codigo} if dataset_codigo else None,
    )


async def obter_layout(layout_id: str) -> dict:
    return await _request_layout_service("GET", f"/layout/layouts/{layout_id}")


async def criar_versao_layout(layout_id: str, payload: LayoutVersaoCreate) -> dict:
    return await _request_layout_service(
        "POST", f"/layout/layouts/{layout_id}/versoes", payload=payload.model_dump()
    )


async def criar_alias(layout_id: str, payload: LayoutAliasCreate) -> dict:
    return await _request_layout_service(
        "POST", f"/layout/layouts/{layout_id}/aliases", payload=payload.model_dump()
    )


async def validar_arquivo_layout(payload: LayoutValidacaoArquivoRequest) -> dict:
    return await _request_layout_service(
        "POST", "/layout/validar-arquivo", payload=payload.model_dump()
    )


async def atualizar_status_layout(layout_id: str, payload: LayoutStatusUpdateRequest) -> dict:
    return await _request_layout_service(
        "POST", f"/layout/layouts/{layout_id}/status", payload=payload.model_dump()
    )


async def listar_layouts_incompativeis() -> dict:
    return await _request_layout_service("GET", "/layout/incompativeis")


async def reprocessar_layout(payload: LayoutReprocessamentoRequest) -> dict:
    return await _request_layout_service(
        "POST", "/layout/reprocessar", payload=payload.model_dump()
    )
