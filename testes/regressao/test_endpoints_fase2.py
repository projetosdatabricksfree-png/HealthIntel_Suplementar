from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _fake_auth(request=None, x_api_key: str | None = None):
    if request is not None:
        request.state.chave_api_id = "fase2-test"
        request.state.cliente_id = "cliente-test"
        request.state.plano_id = "plano-test"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
    return "ok"


def _patch_sem_rate_limit(monkeypatch, modulos: list[str]) -> None:
    async def _noop(_request):
        return None

    for modulo in modulos:
        monkeypatch.setattr(modulo, "aplicar_rate_limit", _noop)


def test_endpoints_fase2_mercado_vazio(monkeypatch) -> None:
    async def fake_service(*_args, **_kwargs):
        return {
            "dados": [
                {
                    "cd_municipio": "3550308",
                    "nm_municipio": "SAO PAULO",
                    "sg_uf": "SP",
                    "nm_regiao": "SUDESTE",
                    "competencia": "202604",
                    "segmento": "MEDICO",
                    "qt_operadora_presente": 0,
                    "qt_operadora_sem_cobertura": 4,
                    "qt_operadora_total": 4,
                    "pct_operadoras_com_cobertura": 0.0,
                    "pct_operadoras_sem_cobertura": 100.0,
                    "vazio_total": True,
                    "vazio_parcial": False,
                    "versao_dataset": "vazio_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202604",
                "versao_dataset": "vazio_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = _fake_auth
    _patch_sem_rate_limit(monkeypatch, [__import__("api.app.routers.mercado", fromlist=["*"])])
    monkeypatch.setattr("api.app.routers.mercado.listar_vazios_assistenciais", fake_service)
    try:
        response = client.get("/v1/mercado/vazio-assistencial", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["vazio_total"] is True


def test_endpoints_fase2_oportunidade_v2(monkeypatch) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        if request is not None:
            request.state.chave_api_id = "fase2-test"
            request.state.cliente_id = "cliente-test"
            request.state.plano_id = "plano-test"
            request.state.limite_rpm = 1000
            request.state.endpoint_permitido = ["/v1"]
        return "ok"

    async def fake_service(*_args, **_kwargs):
        return {
            "dados": [
                {
                    "cd_municipio": "3550308",
                    "nm_municipio": "SAO PAULO",
                    "sg_uf": "SP",
                    "nm_regiao": "SUDESTE",
                    "competencia": "202604",
                    "total_beneficiarios": 100000,
                    "hhi_municipio": 1800.0,
                    "cobertura_media_pct": 46.2,
                    "cobertura_rede": 12,
                    "oportunidade_score_v1": 63.4,
                    "qt_operadoras_cobertura": 8,
                    "qt_segmentos_cobertos": 3,
                    "qt_segmentos_vazios": 1,
                    "qt_segmentos_parciais": 2,
                    "pct_operadoras_com_cobertura": 75.0,
                    "pct_operadoras_sem_cobertura": 25.0,
                    "vazio_assistencial_presente": True,
                    "operadora_melhor_score_v2": "123456",
                    "score_v2_maximo": 78.9,
                    "score_oportunidade_rede": 35.0,
                    "score_sip": None,
                    "oportunidade_v2_score": 61.2,
                    "ranking_posicao": 1,
                    "sinal_vazio": "vazio_detectado",
                    "versao_algoritmo": "v2.0",
                }
            ],
            "meta": {
                "competencia_referencia": "202604",
                "versao_dataset": "opportunity_v2",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    async def _noop(_request):
        return None

    monkeypatch.setattr("api.app.routers.ranking.aplicar_rate_limit", _noop)
    monkeypatch.setattr(
        "api.app.routers.ranking.listar_ranking_oportunidade_v2",
        fake_service,
    )
    try:
        response = client.get("/v1/rankings/municipio/oportunidade-v2", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["ranking_posicao"] == 1


def test_endpoints_fase2_meta_publico():
    response = client.get("/v1/meta/endpoints")

    assert response.status_code == 200
    assert any(
        endpoint["rota"] == "/v1/mercado/vazio-assistencial"
        for endpoint in response.json()["dados"]
    )
