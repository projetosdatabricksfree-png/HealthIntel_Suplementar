from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


async def _fake_auth(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "prata_smoke"
    request.state.cliente_id = "prata_smoke_cliente"
    request.state.plano_id = "prata_smoke_plano"
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["prata", "ouro", "bronze"]
    return x_api_key or "prata_smoke_key"


ENDPOINTS = [
    "/v1/prata/cadop?competencia=202501",
    "/v1/prata/sib/operadora?competencia=202501",
    "/v1/prata/sib/municipio?competencia=202501",
    "/v1/prata/igr?competencia=2025T1",
    "/v1/prata/nip?competencia=2025T1",
    "/v1/prata/idss?competencia=2024",
    "/v1/prata/diops?competencia=2025T1",
    "/v1/prata/fip?competencia=2025T1",
    "/v1/prata/vda?competencia=202501",
    "/v1/prata/glosa?competencia=202501",
    "/v1/prata/rede-assistencial?competencia=202501",
    "/v1/prata/operadora/enriquecida?competencia=202501",
    "/v1/prata/municipio/metrica?competencia=202501",
    "/v1/prata/financeiro/periodo?competencia=2025T1",
    "/v1/prata/cnes/municipio?competencia=202501",
    "/v1/prata/cnes/rede-gap?competencia=202501",
    "/v1/prata/tiss/procedimento?competencia=2025T1",
]


def main() -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth
    try:
        client = TestClient(app)
        headers = {"X-API-Key": "prata_smoke_key"}
        falhas: list[dict[str, object]] = []
        for endpoint in ENDPOINTS:
            response = client.get(endpoint, headers=headers)
            if response.status_code != 200:
                falhas.append({"endpoint": endpoint, "status_code": response.status_code})
                continue
            payload = response.json()
            if "qualidade" not in payload.get("meta", {}):
                falhas.append({"endpoint": endpoint, "erro": "meta.qualidade ausente"})
    finally:
        app.dependency_overrides.clear()
    if falhas:
        raise SystemExit(f"Smoke Prata falhou: {falhas}")
    print({"status": "ok", "endpoints": len(ENDPOINTS)})


if __name__ == "__main__":
    main()
