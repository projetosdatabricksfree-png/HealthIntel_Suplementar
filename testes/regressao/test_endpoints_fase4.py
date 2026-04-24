from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


def _fake_auth(camadas: list[str]):
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "fase4-test"
        request.state.cliente_id = "cliente-fase4"
        request.state.plano_id = "plano-fase4"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = camadas
        return "ok"

    return fake_auth


async def _fake_log_uso(*args, **kwargs):
    return None


def test_endpoints_prata_fase4_registrados(monkeypatch) -> None:
    async def fake_service(dataset: str, **kwargs):
        return {
            "dados": [],
            "meta": {
                "fonte": dataset,
                "competencia": kwargs["competencia"],
                "versao_dataset": "v1",
                "qualidade": {
                    "taxa_aprovacao": 1.0,
                    "registros_quarentena": 0,
                    "motivos_rejeicao": [],
                },
                "aviso_qualidade": None,
                "total": 0,
                "pagina": 1,
                "por_pagina": 50,
                "cache": "miss",
            },
        }

    app.dependency_overrides[validar_api_key] = _fake_auth(["prata", "ouro", "bronze"])
    monkeypatch.setattr("api.app.routers.prata.buscar_prata", fake_service)
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        client = TestClient(app)
        endpoints = [
            "/v1/prata/cnes/municipio?competencia=202501",
            "/v1/prata/cnes/rede-gap?competencia=202501",
            "/v1/prata/tiss/procedimento?competencia=2025T1",
        ]
        responses = [client.get(endpoint, headers={"X-API-Key": "ok"}) for endpoint in endpoints]
    finally:
        app.dependency_overrides.clear()

    assert [response.status_code for response in responses] == [200, 200, 200]


def test_bloqueio_prata_para_plano_sem_camada(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth(["bronze"])
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        client = TestClient(app)
        response = client.get("/v1/prata/cadop?competencia=202501", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
