from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


async def _fake_auth(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = "teste"
    request.state.cliente_id = "cliente-teste"
    request.state.plano_id = "plano-teste"
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
    request.state.is_admin = False
    return "ok"


def test_mercado_municipio_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_mercado(**_kwargs):
        return {
            "dados": [
                {
                    "cd_municipio": "3550308",
                    "nm_municipio": "SAO PAULO",
                    "sg_uf": "SP",
                    "competencia": "202603",
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "beneficiario_total": 1000,
                    "market_share_pct": 55.5,
                    "hhi_municipio": 1800.0,
                    "versao_dataset": "market_share_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "market_share_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = _fake_auth
    monkeypatch.setattr("api.app.routers.mercado.listar_mercado_municipio", fake_mercado)
    try:
        response = client.get("/v1/mercado/municipio", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["cd_municipio"] == "3550308"


def test_ranking_score_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_ranking_score(**_kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "competencia": "202603",
                    "score_final": 87.3,
                    "rating": "A",
                    "ranking_posicao": 1,
                    "versao_score": "score_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "score_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = _fake_auth
    monkeypatch.setattr("api.app.routers.ranking.listar_ranking_score", fake_ranking_score)
    try:
        response = client.get("/v1/rankings/operadora/score", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["ranking_posicao"] == 1
