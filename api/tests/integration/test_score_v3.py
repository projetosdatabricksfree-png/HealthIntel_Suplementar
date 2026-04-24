from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_score_v3_retorna_payload(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "score-v3-test"
        request.state.cliente_id = "cliente-test"
        request.state.plano_id = "plano-test"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro", "prata", "bronze"]
        return "ok"

    async def fake_log_uso(*args, **kwargs):
        return None

    async def fake_service(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "competencia_id": "202604",
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "trimestre_financeiro": "2026T1",
                    "score_core": 75.0,
                    "score_regulatorio": 80.0,
                    "score_financeiro": 70.0,
                    "score_rede": 65.0,
                    "score_estrutural": None,
                    "score_completo": False,
                    "score_v3_final": 74.5,
                    "versao_metodologia": "v3.0",
                }
            ],
            "meta": {
                "competencia_referencia": "202604",
                "versao_dataset": "v3.0",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
                "cache": "miss",
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.middleware.log_requisicao.registrar_log_uso",
        fake_log_uso,
    )
    monkeypatch.setattr(
        "api.app.routers.operadora.buscar_score_v3_operadora",
        fake_service,
    )
    try:
        response = client.get(
            "/v1/operadoras/123456/score-v3",
            headers={"X-API-Key": "ok"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["score_v3_final"] == 74.5
