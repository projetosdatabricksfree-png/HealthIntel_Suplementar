from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_regulatorio_operadora_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_detalhar_regulatorio(*args, **kwargs):
        return {
            "dados": [
                {
                    "registro_ans": "123456",
                    "trimestre": "2025T4",
                    "nome": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "igr": 2.1,
                    "meta_igr": 2.4,
                    "atingiu_meta_excelencia": True,
                    "demandas_nip": 30,
                    "demandas_resolvidas": 27,
                    "taxa_intermediacao_resolvida": 90.0,
                    "taxa_resolutividade": 92.5,
                    "rn623_excelencia": True,
                    "rn623_reducao": False,
                    "faixa_risco_regulatorio": "baixo",
                    "status_rn623": "excelencia",
                    "versao_regulatoria": "regulatorio_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "2025T4",
                "versao_dataset": "igr_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr(
        "api.app.routers.operadora.detalhar_regulatorio_operadora",
        fake_detalhar_regulatorio,
    )
    try:
        response = client.get("/v1/operadoras/123456/regulatorio", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["status_rn623"] == "excelencia"


def test_rn623_lista_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_listar_rn623(**kwargs):
        return {
            "dados": [
                {
                    "trimestre": "2025T4",
                    "tipo_lista": "excelencia",
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "total_nip": 30,
                    "beneficiarios": 120000,
                    "igr": 2.1,
                    "meta_igr": 2.4,
                    "elegivel": True,
                    "observacao": "demo",
                }
            ],
            "meta": {
                "competencia_referencia": "2025T4",
                "versao_dataset": "rn623_lista_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 50,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.regulatorio.listar_rn623", fake_listar_rn623)
    try:
        response = client.get("/v1/regulatorio/rn623", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["tipo_lista"] == "excelencia"
