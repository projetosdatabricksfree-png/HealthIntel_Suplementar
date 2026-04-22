import httpx

from ingestao.app.config import get_settings

settings = get_settings()


async def validar_arquivo_layout(
    dataset_codigo: str, colunas_detectadas: list[str], nome_arquivo: str
) -> dict:
    payload = {
        "dataset_codigo": dataset_codigo,
        "colunas_detectadas": colunas_detectadas,
        "nome_arquivo": nome_arquivo,
    }
    async with httpx.AsyncClient(
        base_url=settings.layout_service_url,
        timeout=20.0,
        headers={"X-Service-Token": settings.layout_service_token},
    ) as client:
        response = await client.post("/layout/validar-arquivo", json=payload)
    response.raise_for_status()
    return response.json()
