from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_prata_quarentena_resumo_retorna_payload(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "prata-test"
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
            "dados": [
                {
                    "dataset": "cadop",
                    "arquivo_origem": "cadop_demo.csv",
                    "competencia": "202501",
                    "hash_arquivo": "hash",
                    "total_registros": 2,
                    "primeiro_registro_em": "2026-04-22T00:00:00Z",
                    "ultimo_registro_em": "2026-04-22T00:00:00Z",
                    "status_quarentena": ["pendente"],
                }
            ],
            "meta": {
                "fonte": "plataforma.vw_resumo_quarentena",
                "competencia": "202501",
                "versao_dataset": "quarentena_v1",
                "qualidade": {
                    "taxa_aprovacao": 1.0,
                    "registros_quarentena": 1,
                    "motivos_rejeicao": [],
                },
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
    monkeypatch.setattr("api.app.routers.prata.buscar_quarentena_resumo", fake_service)
    try:
        response = client.get(
            "/v1/prata/quarentena/resumo",
            headers={"X-API-Key": "ok"},
            params={"competencia": "202501"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["dataset"] == "cadop"
