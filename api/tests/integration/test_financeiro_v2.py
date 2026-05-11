from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def test_financeiro_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_financeiro(*args, **kwargs):
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
                    "trimestre_referencia": "2026T1",
                    "ativo_total": 10.0,
                    "passivo_total": 5.0,
                    "patrimonio_liquido": 5.0,
                    "receita_total": 20.0,
                    "despesa_total": 15.0,
                    "resultado_periodo": 5.0,
                    "resultado_operacional": 5.0,
                    "provisao_tecnica": 1.0,
                    "margem_solvencia_calculada": 1.0,
                    "sinistro_total": 12.0,
                    "contraprestacao_total": 18.0,
                    "sinistralidade_bruta": 0.66,
                    "ressarcimento_sus": 0.5,
                    "evento_indenizavel": 1.0,
                    "sinistralidade_liquida": 0.6,
                    "taxa_sinistralidade_calculada": 0.67,
                    "indice_sinistralidade": 0.67,
                    "margem_liquida_pct": 25.0,
                    "cobertura_provisao": 1.1,
                    "resultado_operacional_bruto": 5.0,
                    "score_financeiro_base": 82.0,
                    "rating_financeiro": "B",
                    "vda_valor_devido": 100.0,
                    "vda_valor_pago": 90.0,
                    "vda_saldo_devedor": 10.0,
                    "vda_situacao_cobranca": "inadimplente",
                    "vda_inadimplente": True,
                    "vda_meses_inadimplente_consecutivos": 2,
                    "vda_data_vencimento": "2026-03-10",
                    "qt_glosa": 5,
                    "valor_glosa": 20.0,
                    "valor_faturado": 100.0,
                    "glosa_taxa_glosa_calculada": 0.2,
                    "severidade_glosa": "alta",
                    "tipos_glosa": "assistencial",
                    "versao_dataset": "financeiro_v2_v1",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "financeiro_v2_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.financeiro.detalhar_financeiro_operadora", fake_financeiro)
    try:
        response = client.get("/v1/operadoras/123456/financeiro", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["vda_saldo_devedor"] == 10.0


def test_score_v2_retorna_payload_com_override(monkeypatch) -> None:
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    async def fake_score_v2(*args, **kwargs):
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
                    "trimestre_financeiro": "2026T1",
                    "score_core": 80.0,
                    "score_regulatorio": 39.99,
                    "score_financeiro_trimestral": 75.0,
                    "inadimplente": True,
                    "saldo_devedor": 10.0,
                    "valor_devido": 100.0,
                    "valor_pago": 90.0,
                    "situacao_cobranca": "inadimplente",
                    "taxa_glosa_calculada": 0.2,
                    "valor_glosa_total": 20.0,
                    "valor_faturado_total": 100.0,
                    "penalizacao_vda": 5,
                    "penalizacao_glosa": 3,
                    "score_penalizacoes": 92.0,
                    "score_v2_base": 69.0,
                    "score_v2": 69.0,
                    "rating": "C",
                    "componentes": {
                        "score_core": 80.0,
                        "score_regulatorio": 39.99,
                        "score_financeiro_trimestral": 75.0,
                        "penalizacao_vda": 5.0,
                        "penalizacao_glosa": 3.0,
                        "score_penalizacoes": 92.0,
                    },
                    "versao_metodologia": "v2.0",
                }
            ],
            "meta": {
                "competencia_referencia": "202603",
                "versao_dataset": "score_v2_v1",
                "total": 1,
                "pagina": 1,
                "por_pagina": 1,
            },
        }

    app.dependency_overrides[validar_api_key] = fake_auth
    monkeypatch.setattr("api.app.routers.financeiro.detalhar_score_v2_operadora", fake_score_v2)
    try:
        response = client.get("/v1/operadoras/123456/score-v2", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dados"][0]["score_v2"] == 69.0
