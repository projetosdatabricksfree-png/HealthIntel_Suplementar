import asyncio
import os
from typing import Any

import httpx


async def _coletar(
    client: httpx.AsyncClient,
    metodo: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = await client.request(metodo, url, headers=headers, params=params, json=payload)
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    return {
        "url": url,
        "status_code": response.status_code,
        "ok": response.is_success,
        "body": body,
    }


async def main() -> None:
    base_url = os.getenv("SMOKE_BASE_URL", "http://localhost:8080")
    api_key = os.getenv("SMOKE_API_KEY", "hi_local_dev_2026_api_key")
    admin_key = os.getenv("SMOKE_ADMIN_API_KEY", "hi_local_admin_2026_api_key")

    async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
        resultados = [
            await _coletar(client, "GET", "/saude"),
            await _coletar(client, "GET", "/prontidao"),
            await _coletar(client, "GET", "/v1/meta/dataset"),
            await _coletar(client, "GET", "/v1/meta/versao"),
            await _coletar(client, "GET", "/v1/meta/pipeline"),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras",
                headers={"X-API-Key": api_key},
                params={"pagina": 1, "por_pagina": 10},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456",
                headers={"X-API-Key": api_key},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456/score",
                headers={"X-API-Key": api_key},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456/regulatorio",
                headers={"X-API-Key": api_key},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/regulatorio/rn623",
                headers={"X-API-Key": admin_key},
                params={"trimestre": "2025T4"},
            ),
            await _coletar(
                client,
                "GET",
                "/admin/layouts",
                headers={"X-API-Key": admin_key},
            ),
            await _coletar(
                client,
                "GET",
                "/admin/billing/resumo",
                headers={"X-API-Key": admin_key},
                params={"referencia": os.getenv("SMOKE_REFERENCIA", "2026-04")},
            ),
        ]

    falhas = [resultado for resultado in resultados if not resultado["ok"]]
    print({"base_url": base_url, "total_checks": len(resultados), "falhas": len(falhas)})
    for resultado in resultados:
        print(
            {
                "url": resultado["url"],
                "status_code": resultado["status_code"],
                "ok": resultado["ok"],
            }
        )
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
