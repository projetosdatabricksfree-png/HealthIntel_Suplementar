from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit

client = TestClient(app)


@patch("api.app.routers.admin_layout.listar_layouts", new_callable=AsyncMock)
def test_admin_layout_lista_via_servico(mock_listar_layouts: AsyncMock) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        return "ok"

    chamadas_rate_limit = 0

    async def fake_rate_limit(request=None):
        nonlocal chamadas_rate_limit
        chamadas_rate_limit += 1

    mock_listar_layouts.return_value = {
        "dados": [{"layout_id": "layout_cadop_csv", "dataset_codigo": "cadop", "status": "ativo"}]
    }
    app.dependency_overrides[validar_api_key] = fake_auth
    app.dependency_overrides[aplicar_rate_limit] = fake_rate_limit
    try:
        response = client.get("/admin/layouts", headers={"X-API-Key": "teste"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert chamadas_rate_limit == 1
    body = response.json()
    assert body["dados"][0]["layout_id"] == "layout_cadop_csv"
