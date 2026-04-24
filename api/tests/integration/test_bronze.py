from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_bronze_bloqueia_plano_sem_camada(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "bronze-test"
        request.state.cliente_id = "cliente-test"
        request.state.plano_id = "plano-test"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro"]
        return "ok"

    async def fake_log_uso(*args, **kwargs):
        return None

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.middleware.log_requisicao.registrar_log_uso",
        fake_log_uso,
    )
    try:
        response = client.get(
            "/v1/bronze/cadop",
            headers={"X-API-Key": "ok"},
            params={"competencia": "202501"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_bronze_retorna_payload(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "bronze-test"
        request.state.cliente_id = "cliente-test"
        request.state.plano_id = "plano-test"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        return "ok"

    async def fake_log_uso(*args, **kwargs):
        return None

    async def fake_service(*args, **kwargs):
        return {
            "dados": [{"registro_ans": "123456", "competencia": "202501"}],
            "meta": {
                "fonte": "cadop",
                "competencia": "202501",
                "lote_id": "lote-1",
                "arquivo_origem": "cadop_demo.csv",
                "carregado_em": "2026-04-22T00:00:00Z",
                "versao_dataset": "cadop_v1",
                "aviso_qualidade": (
                    "Dado bruto sem garantia semantica. Use camada Prata para analise."
                ),
                "cache": "miss",
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.middleware.log_requisicao.registrar_log_uso",
        fake_log_uso,
    )
    monkeypatch.setattr("api.app.routers.bronze.buscar_bronze", fake_service)
    try:
        response = client.get(
            "/v1/bronze/cadop",
            headers={"X-API-Key": "ok"},
            params={"competencia": "202501"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["registro_ans"] == "123456"
