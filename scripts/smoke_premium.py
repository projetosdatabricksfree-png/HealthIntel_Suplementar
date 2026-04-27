from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


async def _mock_premium_service(dataset, *, filtros=None, pagina=1, limite=50, tenant_id=None, **kw) -> dict:
    return {
        "dados": [],
        "meta": {
            "fonte": "smoke_mock",
            "competencia": "202501",
            "versao_dataset": "smoke_v1",
            "total": 0,
            "pagina": pagina,
            "por_pagina": limite,
            "cache": "miss",
        },
    }


async def _fake_auth_premium(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "premium_smoke"
    request.state.cliente_id = "cliente_premium_smoke"
    request.state.plano_id = "plano_premium_smoke"
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
    return x_api_key or "premium_smoke_key"


async def _fake_auth_free(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "free_smoke"
    request.state.cliente_id = "cliente_free_smoke"
    request.state.plano_id = "plano_free_smoke"
    request.state.limite_rpm = 100
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["ouro"]
    return x_api_key or "free_smoke_key"


async def _fake_auth_sem_tenant(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "sem_tenant_smoke"
    request.state.cliente_id = None
    request.state.plano_id = "plano_premium_smoke"
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
    return x_api_key or "sem_tenant_smoke_key"


ENDPOINTS_PUBLICOS = [
    "/v1/premium/operadoras?competencia=202501",
    "/v1/premium/cnes/estabelecimentos?competencia=202501",
    "/v1/premium/tiss/procedimentos?trimestre=2025T1",
    "/v1/premium/tuss/procedimentos",
    "/v1/premium/mdm/operadoras",
    "/v1/premium/mdm/prestadores",
]

ENDPOINTS_PRIVADOS = [
    "/v1/premium/contratos",
    "/v1/premium/subfaturas",
]

HEADERS = {"X-API-Key": "premium_smoke_key"}


def main() -> None:
    falhas: list[dict[str, object]] = []
    client = TestClient(app)

    # Monkeypatch service e log para evitar dependência de DB no smoke offline
    import api.app.middleware.log_requisicao as log_middleware
    import api.app.routers.premium as premium_router
    premium_router.buscar_premium = _mock_premium_service  # type: ignore[assignment]
    async def _fake_log(**kw): return None
    log_middleware.registrar_log_uso = _fake_log  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Cenário 1-6: Plano premium acessa endpoints públicos
    # ------------------------------------------------------------------
    app.dependency_overrides[validar_api_key] = _fake_auth_premium
    try:
        for endpoint in ENDPOINTS_PUBLICOS:
            response = client.get(endpoint, headers=HEADERS)
            if response.status_code != 200:
                falhas.append({"cenario": "premium_publico", "endpoint": endpoint, "status_code": response.status_code})
                continue
            payload = response.json()
            if "dados" not in payload or "meta" not in payload:
                falhas.append({"cenario": "premium_publico", "endpoint": endpoint, "erro": "envelope invalido"})
                continue
            meta = payload["meta"]
            if "pagina" not in meta or "por_pagina" not in meta:
                falhas.append({"cenario": "premium_publico", "endpoint": endpoint, "erro": "paginacao ausente"})
    finally:
        app.dependency_overrides.clear()

    # ------------------------------------------------------------------
    # Cenário 7-8: Plano premium com tenant acessa endpoints privados
    # ------------------------------------------------------------------
    app.dependency_overrides[validar_api_key] = _fake_auth_premium
    try:
        for endpoint in ENDPOINTS_PRIVADOS:
            response = client.get(endpoint, headers=HEADERS)
            if response.status_code != 200:
                falhas.append({"cenario": "premium_privado", "endpoint": endpoint, "status_code": response.status_code})
                continue
            payload = response.json()
            if "dados" not in payload or "meta" not in payload:
                falhas.append({"cenario": "premium_privado", "endpoint": endpoint, "erro": "envelope invalido"})
                continue
            meta = payload["meta"]
            if "pagina" not in meta or "por_pagina" not in meta:
                falhas.append({"cenario": "premium_privado", "endpoint": endpoint, "erro": "paginacao ausente"})
    finally:
        app.dependency_overrides.clear()

    # ------------------------------------------------------------------
    # Cenário 9: Plano não premium recebe HTTP 403
    # ------------------------------------------------------------------
    app.dependency_overrides[validar_api_key] = _fake_auth_free
    try:
        response = client.get(ENDPOINTS_PUBLICOS[0], headers={"X-API-Key": "free_smoke_key"})
        if response.status_code != 403:
            falhas.append({"cenario": "nao_premium_403", "status_code": response.status_code})
    finally:
        app.dependency_overrides.clear()

    # ------------------------------------------------------------------
    # Cenário 10: Rota privada sem tenant recebe 403
    # ------------------------------------------------------------------
    app.dependency_overrides[validar_api_key] = _fake_auth_sem_tenant
    try:
        for endpoint in ENDPOINTS_PRIVADOS:
            response = client.get(endpoint, headers={"X-API-Key": "sem_tenant_smoke_key"})
            if response.status_code not in (401, 403):
                falhas.append({"cenario": "sem_tenant_403", "endpoint": endpoint, "status_code": response.status_code})
    finally:
        app.dependency_overrides.clear()

    # ------------------------------------------------------------------
    # Cenário 11-14: Verificar envelope, paginação e qualidade
    # ------------------------------------------------------------------
    app.dependency_overrides[validar_api_key] = _fake_auth_premium
    try:
        # Envelope padronizado
        response = client.get(ENDPOINTS_PUBLICOS[0], headers=HEADERS)
        payload = response.json()
        if not isinstance(payload.get("dados"), list):
            falhas.append({"cenario": "envelope", "erro": "dados nao e lista"})
        if not isinstance(payload.get("meta"), dict):
            falhas.append({"cenario": "envelope", "erro": "meta ausente"})

        # Paginação
        response = client.get("/v1/premium/operadoras?competencia=202501&pagina=1&limite=10", headers=HEADERS)
        meta = response.json().get("meta", {})
        if meta.get("pagina") != 1 or meta.get("por_pagina") != 10:
            falhas.append({"cenario": "paginacao", "erro": "pagina/por_pagina incorretos"})

        # Metadados de qualidade
        response = client.get("/v1/premium/quality/datasets", headers=HEADERS)
        quality_data = response.json()
        if "dados" not in quality_data:
            falhas.append({"cenario": "qualidade", "erro": "quality/datasets sem dados"})
        elif quality_data["dados"]:
            item = quality_data["dados"][0]
            if "quality_score_documental" not in item:
                falhas.append({"cenario": "qualidade", "erro": "quality_score_documental ausente"})

        # Nenhum smoke faz dump completo — verificar que limite máximo é respeitado
        response = client.get("/v1/premium/operadoras?competencia=202501&limite=100", headers=HEADERS)
        if response.status_code == 200:
            meta = response.json().get("meta", {})
            if meta.get("por_pagina", 0) > 100:
                falhas.append({"cenario": "limite_maximo", "erro": "limite > 100 permitido"})

    finally:
        app.dependency_overrides.clear()

    if falhas:
        raise SystemExit(f"Smoke Premium falhou: {falhas}")
    print({"status": "ok", "endpoints_publicos": len(ENDPOINTS_PUBLICOS), "endpoints_privados": len(ENDPOINTS_PRIVADOS)})


if __name__ == "__main__":
    main()