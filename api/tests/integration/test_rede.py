from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_endpoint_rede_operadora_retorna_payload(monkeypatch) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        if request is not None:
            request.state.chave_api_id = "rede-test"
            request.state.cliente_id = "cliente-test"
            request.state.plano_id = "plano-test"
            request.state.limite_rpm = 1000
            request.state.endpoint_permitido = ["/v1"]
        return "ok"

    async def fake_service(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "competencia": "202604",
                    "competencia_id": "202604",
                    "cd_municipio": "3550308",
                    "nm_municipio": "SAO PAULO",
                    "sg_uf": "SP",
                    "nm_regiao": "SUDESTE",
                    "segmento": "MEDICO",
                    "pop_estimada_ibge": 11451245,
                    "porte_municipio": "grande",
                    "qt_prestador": 32,
                    "qt_especialidade_disponivel": 18,
                    "beneficiario_total": 12000,
                    "qt_prestador_por_10k_beneficiarios": 26.67,
                    "limiar_prestador_por_10k": 1.2,
                    "limiar_especialidade_por_10k": 1.8,
                    "tem_cobertura": True,
                    "cobertura_minima_atendida": True,
                    "qt_municipio_coberto": 10,
                    "qt_uf_coberto": 3,
                    "pct_municipios_cobertos": 66.67,
                    "pct_ufs_cobertos": 50.0,
                    "score_rede": 72.0,
                    "versao_dataset": "rede_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202604",
                "versao_dataset": "rede_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.operadora.detalhar_rede_operadora", fake_service)
    try:
        response = client.get("/v1/operadoras/123456/rede", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["score_rede"] == 72.0


def test_endpoint_rede_municipio_retorna_payload(monkeypatch) -> None:
    async def fake_auth(request=None, x_api_key: str | None = None):
        if request is not None:
            request.state.chave_api_id = "rede-test"
            request.state.cliente_id = "cliente-test"
            request.state.plano_id = "plano-test"
            request.state.limite_rpm = 1000
            request.state.endpoint_permitido = ["/v1"]
        return "ok"

    async def fake_service(*args, **kwargs):
        return {
            "dados": [
                {
                    "operadora_id": 1,
                    "registro_ans": "123456",
                    "nome": "OPERADORA EXEMPLO",
                    "nome_fantasia": "OPERADORA EXEMPLO",
                    "modalidade": "MEDICINA_DE_GRUPO",
                    "uf_sede": "SP",
                    "competencia": "202604",
                    "competencia_id": "202604",
                    "cd_municipio": "3550308",
                    "nm_municipio": "SAO PAULO",
                    "sg_uf": "SP",
                    "nm_regiao": "SUDESTE",
                    "segmento": "MEDICO",
                    "pop_estimada_ibge": 11451245,
                    "porte_municipio": "grande",
                    "qt_prestador": 32,
                    "qt_especialidade_disponivel": 18,
                    "beneficiario_total": 12000,
                    "qt_prestador_por_10k_beneficiarios": 26.67,
                    "limiar_prestador_por_10k": 1.2,
                    "limiar_especialidade_por_10k": 1.8,
                    "tem_cobertura": True,
                    "cobertura_minima_atendida": True,
                    "qt_municipio_coberto": 10,
                    "qt_uf_coberto": 3,
                    "pct_municipios_cobertos": 66.67,
                    "pct_ufs_cobertos": 50.0,
                    "score_rede": 72.0,
                    "versao_dataset": "rede_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202604",
                "versao_dataset": "rede_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.rede.listar_rede_municipio", fake_service)
    try:
        response = client.get("/v1/rede/municipio/3550308", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["cd_municipio"] == "3550308"
