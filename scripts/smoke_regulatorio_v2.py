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
    async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
        resultados = [
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456/score-regulatorio",
                headers={"X-API-Key": api_key},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456/regime-especial",
                headers={"X-API-Key": api_key},
            ),
            await _coletar(
                client,
                "GET",
                "/v1/operadoras/123456/portabilidade",
                headers={"X-API-Key": api_key},
            ),
        ]

    score_body = resultados[0]["body"]
    if isinstance(score_body, dict) and score_body.get("dados"):
        score_regulatorio = score_body["dados"][0].get("score_regulatorio")
        if score_regulatorio is not None and score_regulatorio > 39.99:
            raise SystemExit("score_regulatorio acima do limite de truncamento esperado")

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
