from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_operadoras_exige_api_key() -> None:
    response = client.get("/v1/operadoras")
    assert response.status_code == 401


def test_operadoras_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_listar_operadoras(**kwargs):
        return {
            "dados": [
                {
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "competencia_referencia": "202603",
                    "score_final": 80.5,
                    "rating": "B",
                    "versao_score": "score_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "sib_operadora_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.operadora.listar_operadoras", fake_listar_operadoras)
    try:
        response = client.get("/v1/operadoras", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["registro_ans"] == "123456"
