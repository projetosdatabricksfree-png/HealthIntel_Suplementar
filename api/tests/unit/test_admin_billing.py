from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit

client = TestClient(app)


@patch("api.app.routers.admin_billing.listar_resumo_faturamento", new_callable=AsyncMock)
def test_admin_billing_resumo_via_servico(mock_resumo: AsyncMock) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        return "ok"

    chamadas_rate_limit = 0

    async def fake_rate_limit(request=None):
        nonlocal chamadas_rate_limit
        chamadas_rate_limit += 1

    mock_resumo.return_value = {
        "dados": [
            {
                "referencia": "2026-04",
                "cliente_nome": "cliente_local_healthintel",
                "valor_total_centavos": 249000,
            }
        ],
        "meta": {"referencia": "2026-04", "total_clientes": 1},
    }
    app.dependency_overrides[validar_api_key] = fake_auth
    app.dependency_overrides[aplicar_rate_limit] = fake_rate_limit
    try:
        response = client.get(
            "/admin/billing/resumo",
            params={"referencia": "2026-04"},
            headers={"X-API-Key": "teste"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert chamadas_rate_limit == 1
    assert response.json()["dados"][0]["cliente_nome"] == "cliente_local_healthintel"


@patch("api.app.routers.admin_billing.fechar_ciclo_faturamento", new_callable=AsyncMock)
def test_admin_billing_fechar_ciclo_via_servico(mock_fechar: AsyncMock) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        return "ok"

    chamadas_rate_limit = 0

    async def fake_rate_limit(request=None):
        nonlocal chamadas_rate_limit
        chamadas_rate_limit += 1

    mock_fechar.return_value = {"dados": [], "meta": {"referencia": "2026-04", "total_clientes": 0}}
    app.dependency_overrides[validar_api_key] = fake_auth
    app.dependency_overrides[aplicar_rate_limit] = fake_rate_limit
    try:
        response = client.post(
            "/admin/billing/fechar-ciclo",
            json={"referencia": "2026-04"},
            headers={"X-API-Key": "teste"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert chamadas_rate_limit == 1
    assert response.json()["meta"]["referencia"] == "2026-04"
