from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


async def _fake_auth(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "premium_smoke"
    request.state.cliente_id = "cliente_premium_smoke"
    request.state.plano_id = "plano_premium_smoke"
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
    return x_api_key or "premium_smoke_key"


ENDPOINTS = [
    "/v1/premium/operadoras?competencia=202501",
    "/v1/premium/cnes/estabelecimentos?competencia=202501",
    "/v1/premium/quality/datasets",
]


def main() -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth
    try:
        client = TestClient(app)
        headers = {"X-API-Key": "premium_smoke_key"}
        falhas: list[dict[str, object]] = []
        for endpoint in ENDPOINTS:
            response = client.get(endpoint, headers=headers)
            if response.status_code != 200:
                falhas.append({"endpoint": endpoint, "status_code": response.status_code})
                continue
            payload = response.json()
            if "dados" not in payload or "meta" not in payload:
                falhas.append({"endpoint": endpoint, "erro": "envelope invalido"})
    finally:
        app.dependency_overrides.clear()

    if falhas:
        raise SystemExit(f"Smoke Premium falhou: {falhas}")
    print({"status": "ok", "endpoints": len(ENDPOINTS)})


if __name__ == "__main__":
    main()
