from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_score_regulatorio_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_score(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "competencia": "202512",
                    "score_igr": 90.0,
                    "score_nip": 88.0,
                    "score_rn623": 80.0,
                    "score_prudencial": 78.0,
                    "score_taxa_resolutividade": 92.0,
                    "regime_especial_ativo": True,
                    "tipo_regime": "direcao_fiscal",
                    "situacao_inadequada": False,
                    "qt_portabilidade_entrada": 10,
                    "qt_portabilidade_saida": 3,
                    "saldo_portabilidade": 7,
                    "score_regulatorio_base": 87.0,
                    "score_regulatorio": 39.99,
                    "rating": "D",
                    "versao_regulatoria": "regulatorio_v2",
                }
            ],
            "meta": {
                "competencia_referencia": "202512",
                "versao_dataset": "score_regulatorio_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.routers.regulatorio_v2.detalhar_score_regulatorio_operadora",
        fake_score,
    )
    try:
        response = client.get(
            "/v1/operadoras/123456/score-regulatorio", headers={"X-API-Key": "ok"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["score_regulatorio"] == 39.99


def test_regime_especial_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_regime(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "trimestre": "2025T4",
                    "trimestre_fim": None,
                    "tipo_regime": "direcao_fiscal",
                    "ativo": True,
                    "duracao_trimestres": 2,
                    "data_inicio": "2025-10-01",
                    "data_fim": None,
                    "versao_dataset": "regime_especial_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "2025T4",
                "versao_dataset": "regime_especial_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.routers.regulatorio_v2.listar_regime_especial_operadora",
        fake_regime,
    )
    try:
        response = client.get("/v1/operadoras/123456/regime-especial", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["tipo_regime"] == "direcao_fiscal"


def test_portabilidade_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_portabilidade(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "competencia": "202603",
                    "competencia_data": "2026-03-01",
                    "modalidade_descricao": "Medicina de grupo",
                    "tipo_contratacao": "COLETIVO",
                    "qt_portabilidade_entrada": 10,
                    "qt_portabilidade_saida": 3,
                    "saldo_portabilidade": 7,
                    "fonte_publicacao": "demo",
                    "versao_dataset": "portabilidade_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "portabilidade_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.routers.regulatorio_v2.listar_portabilidade_operadora",
        fake_portabilidade,
    )
    try:
        response = client.get(
            "/v1/operadoras/123456/portabilidade", headers={"X-API-Key": "ok"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["saldo_portabilidade"] == 7
