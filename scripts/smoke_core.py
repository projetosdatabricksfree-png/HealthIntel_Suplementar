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
) -> dict[str, Any]:
    response = await client.request(metodo, url, headers=headers, params=params)
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
    registro_ans = os.getenv("SMOKE_REGISTRO_ANS", "123456")

    h = {"X-API-Key": api_key}

    async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
        resultados = [
            # Health
            await _coletar(client, "GET", "/saude"),
            await _coletar(client, "GET", "/prontidao"),
            # Meta Core
            await _coletar(client, "GET", "/v1/meta/datasets"),
            await _coletar(client, "GET", "/v1/meta/atualizacao"),
            await _coletar(client, "GET", "/v1/meta/qualidade"),
            # Operadoras
            await _coletar(
                client, "GET", "/v1/operadoras", headers=h, params={"pagina": 1, "por_pagina": 10}
            ),
            await _coletar(client, "GET", f"/v1/operadoras/{registro_ans}", headers=h),
            await _coletar(
                client, "GET", f"/v1/operadoras/{registro_ans}/score", headers=h
            ),
            await _coletar(
                client, "GET", f"/v1/operadoras/{registro_ans}/beneficiarios", headers=h
            ),
            await _coletar(
                client, "GET", f"/v1/operadoras/{registro_ans}/financeiro", headers=h
            ),
            await _coletar(
                client, "GET", f"/v1/operadoras/{registro_ans}/regulatorio", headers=h
            ),
            # Rankings
            await _coletar(client, "GET", "/v1/rankings/operadora/score", headers=h),
            await _coletar(client, "GET", "/v1/rankings/operadora/crescimento", headers=h),
            await _coletar(client, "GET", "/v1/rankings/composto", headers=h),
            # Mercado
            await _coletar(
                client,
                "GET",
                "/v1/mercado/municipio",
                headers=h,
                params={"pagina": 1, "por_pagina": 10},
            ),
            await _coletar(client, "GET", "/v1/rankings/municipio/oportunidade", headers=h),
        ]

    falhas = [r for r in resultados if not r["ok"]]
    print({"base_url": base_url, "total_checks": len(resultados), "falhas": len(falhas)})
    for r in resultados:
        print({"url": r["url"], "status_code": r["status_code"], "ok": r["ok"]})
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
