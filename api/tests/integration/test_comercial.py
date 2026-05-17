from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _override_auth():
    async def _auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "teste"
        request.state.cliente_id = "cliente-teste"
        request.state.plano_id = "plano-teste"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["bronze", "prata", "ouro"]
        request.state.is_admin = False
        return "ok"

    return _auth


def _make_payload(dados: list, versao: str, ref: str = "202412") -> dict:
    return {
        "dados": dados,
        "meta": {
            "competencia_referencia": ref,
            "versao_dataset": versao,
            "total": len(dados),
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


# --- produtos-planos ---

def test_produtos_planos_exige_api_key() -> None:
    assert client.get("/v1/produtos-planos").status_code == 401


def test_produtos_planos_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"registro_ans": "123456", "codigo_produto": "P001"}], "consumo_produto_plano_v1")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_produtos_planos", _svc)
    try:
        r = client.get("/v1/produtos-planos", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert "dados" in r.json()
    assert "meta" in r.json()


# --- historico-planos ---

def test_historico_planos_exige_api_key() -> None:
    assert client.get("/v1/historico-planos").status_code == 401


def test_historico_planos_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"registro_ans": "123456", "codigo_plano": "PL001"}], "consumo_historico_plano_v1")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_historico_planos", _svc)
    try:
        r = client.get("/v1/historico-planos", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert "dados" in r.json()


# --- regulatorio ---

def test_regulatorio_exige_api_key() -> None:
    assert client.get("/v1/regulatorio").status_code == 401


def test_regulatorio_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"trimestre": "1T2024", "registro_ans": "123456"}], "consumo_regulatorio_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_regulatorio", _svc)
    try:
        r = client.get("/v1/regulatorio", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["dados"][0]["trimestre"] == "1T2024"


# --- igr ---

def test_igr_exige_api_key() -> None:
    assert client.get("/v1/igr").status_code == 401


def test_igr_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"trimestre": "1T2024", "registro_ans": "123456", "igr": 0.95}], "consumo_igr_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_igr", _svc)
    try:
        r = client.get("/v1/igr", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1


# --- nip ---

def test_nip_exige_api_key() -> None:
    assert client.get("/v1/nip").status_code == 401


def test_nip_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"trimestre": "1T2024", "registro_ans": "123456", "taxa_resolutividade": 0.8}], "consumo_nip_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_nip", _svc)
    try:
        r = client.get("/v1/nip", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert "dados" in r.json()


# --- idss ---

def test_idss_exige_api_key() -> None:
    assert client.get("/v1/idss").status_code == 401


def test_idss_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"ano_base": 2023, "registro_ans": "123456", "idss_total": 0.72}], "consumo_idss_v1", "2023")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_idss", _svc)
    try:
        r = client.get("/v1/idss", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["dados"][0]["idss_total"] == 0.72


# --- financeiro ---

def test_financeiro_exige_api_key() -> None:
    assert client.get("/v1/financeiro").status_code == 401


def test_financeiro_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"trimestre": "1T2024", "registro_ans": "123456", "receita_total": 1000000.0}], "consumo_financeiro_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_financeiro", _svc)
    try:
        r = client.get("/v1/financeiro", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert "dados" in r.json()


# --- prudencial ---

def test_prudencial_exige_api_key() -> None:
    assert client.get("/v1/prudencial").status_code == 401


def test_prudencial_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"registro_ans": "123456", "trimestre": "1T2024", "situacao_prudencial": "adequada"}], "api_prudencial_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_prudencial", _svc)
    try:
        r = client.get("/v1/prudencial", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["dados"][0]["situacao_prudencial"] == "adequada"


# --- regime-especial ---

def test_regime_especial_exige_api_key() -> None:
    assert client.get("/v1/regime-especial").status_code == 401


def test_regime_especial_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"registro_ans": "123456", "trimestre": "1T2024", "tipo_regime": "LIQUIDACAO_EXTRAJUDICIAL"}], "api_regime_especial_v1", "1T2024")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_regime_especial", _svc)
    try:
        r = client.get("/v1/regime-especial", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert "dados" in r.json()


# --- glosa ---

def test_glosa_exige_api_key() -> None:
    assert client.get("/v1/glosa").status_code == 401


def test_glosa_retorna_payload_com_override(monkeypatch) -> None:
    fake = _make_payload([{"registro_ans": "123456", "competencia": 202412, "qt_glosa": 10}], "api_glosa_v1")

    async def _svc(**kw):
        return fake

    app.dependency_overrides[validar_api_key] = _override_auth()
    monkeypatch.setattr("api.app.routers.comercial.listar_glosa", _svc)
    try:
        r = client.get("/v1/glosa", headers={"X-API-Key": "qualquer"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["dados"][0]["qt_glosa"] == 10
