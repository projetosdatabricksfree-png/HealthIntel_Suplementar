from fastapi.testclient import TestClient

from api.app.main import app


client = TestClient(app)


def _headers() -> dict[str, str]:
    return {"X-API-Key": "qualquer"}


def test_core_ans_meta_exige_api_key() -> None:
    response = client.get("/v1/meta/endpoints")
    assert response.status_code == 401


def test_core_ans_meta_endpoints_publica_somente_core(cliente_autenticado) -> None:
    response = client.get("/v1/meta/endpoints", headers=_headers())
    assert response.status_code == 200
    dados = response.json()["dados"]

    disponiveis = {item["path"] for item in dados if item["status"] == "disponivel"}
    em_validacao = {item["path"] for item in dados if item["status"] == "em_validacao"}

    assert "/v1/operadoras" in disponiveis
    assert "/v1/produtos/planos" in disponiveis
    assert "/v1/tuss/procedimentos" in disponiveis
    assert "/v1/operadoras/{registro_ans}/financeiro" in disponiveis
    assert "/v1/cnes/municipio/{cd_municipio}" in em_validacao
    assert not any(item["path"].startswith("/v1/bronze") for item in dados)
    assert not any(item["path"].startswith("/v1/premium") for item in dados)


def test_core_ans_meta_dataset_mvp(cliente_autenticado) -> None:
    response = client.get("/v1/meta/dataset", headers=_headers())
    assert response.status_code == 200
    datasets = {item["nome"]: item for item in response.json()["dados"]}

    for nome in [
        "cadop_operadora",
        "produto_plano",
        "historico_plano",
        "tuss_procedimento_vigente",
        "sib_beneficiario_operadora",
        "sib_beneficiario_municipio",
        "idss",
        "igr",
        "nip",
        "diops",
        "financeiro_periodo",
        "glosa",
        "prudencial",
        "regime_especial",
        "taxa_resolutividade",
    ]:
        assert datasets[nome]["status"] == "publicado"
        assert datasets[nome]["row_count"] > 0


def test_core_ans_endpoints_basicos(cliente_autenticado) -> None:
    assert client.get("/saude").status_code == 200

    for path in [
        "/v1/operadoras?per_page=1",
        "/v1/operadoras/000515",
        "/v1/produtos/planos?per_page=1",
        "/v1/produtos/planos/00",
        "/v1/produtos/historico?per_page=1",
        "/v1/tuss/procedimentos?per_page=1",
        "/v1/tuss/procedimentos/0",
        "/v1/operadoras/006246/regulatorio",
        "/v1/operadoras/000515/financeiro",
        "/v1/mercado/municipio?per_page=1",
    ]:
        response = client.get(path, headers=_headers())
        assert response.status_code == 200, path
        payload = response.json()
        assert "dados" in payload
        assert "meta" in payload
