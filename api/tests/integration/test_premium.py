from fastapi import Request
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

client = TestClient(app)


def _fake_auth_premium(tenant: str = "cliente-premium"):
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "premium-test"
        request.state.cliente_id = tenant
        request.state.plano_id = "plano-premium"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
        return "ok"
    return fake_auth


def _fake_auth_nao_premium():
    async def fake_auth(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "free-test"
        request.state.cliente_id = "cliente-free"
        request.state.plano_id = "plano-piloto"
        request.state.limite_rpm = 100
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro"]
        return "ok"
    return fake_auth


async def _fake_log_uso(*args, **kwargs):
    return None


# ---------------------------------------------------------------------------
# Mock payloads
# ---------------------------------------------------------------------------


def _payload_operadora() -> dict:
    return {
        "dados": [
            {
                "competencia": "202501",
                "registro_ans": "123456",
                "razao_social": "OPERADORA TESTE",
                "nome_fantasia": "OPERADORA TESTE",
                "modalidade": "MEDICINA_DE_GRUPO",
                "uf": "SP",
                "qt_beneficiarios": 1000,
                "variacao_12m_pct": 0.1,
                "score_total": 88.0,
                "componente_core": 90.0,
                "componente_regulatorio": 80.0,
                "componente_financeiro": 85.0,
                "componente_rede": 87.0,
                "componente_estrutural": 92.0,
                "versao_metodologia": "score_v3",
                "cnpj_normalizado": "11222333000181",
                "registro_ans_formato_valido": True,
                "cnpj_digito_valido": True,
                "documento_quality_status": "VALIDO",
                "motivo_invalidade_documento": None,
                "quality_score_documental": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_operadora_360_validado",
            "competencia": "202501",
            "versao_dataset": "operadora_360_validado_v1",
            "total": 1,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


def _payload_tiss(pagina: int = 1, por_pagina: int = 50) -> dict:
    return {
        "dados": [
            {
                "trimestre": "2025T1",
                "registro_ans": "123456",
                "operadora_master_id": "md5hash123456",
                "razao_social": "OPERADORA TESTE",
                "cd_procedimento_tuss": "12345678",
                "grupo_desc": "CONSULTAS",
                "subgrupo_procedimento": "CONSULTA MEDICA",
                "qt_procedimentos": 100,
                "vl_total": 50000.0,
                "custo_medio_procedimento": 500.0,
                "sinistralidade_pct": 0.15,
                "rank_por_valor": 1,
                "status_mdm": "ATIVO",
                "mdm_confidence_score": 0.98,
                "procedimento_quality_status": "VALIDO",
                "quality_score_procedimento": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_tiss_procedimento_tuss_validado",
            "competencia": "2025T1",
            "versao_dataset": "tiss_procedimento_tuss_validado_v1",
            "total": 1,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "cache": "miss",
        },
    }


def _payload_contrato() -> dict:
    return {
        "dados": [
            {
                "contrato_master_id": "md5hashcontrato",
                "tenant_id": "cliente-premium",
                "operadora_master_id": "md5hash123456",
                "numero_contrato_canonico": "CT-001",
                "numero_contrato_normalizado": "CT001",
                "registro_ans_canonico": "123456",
                "cnpj_operadora_canonico": "11222333000181",
                "tipo_contrato": "EMPRESARIAL",
                "vigencia_inicio": "2024-01-01",
                "vigencia_fim": "2025-12-31",
                "status_contrato": "ATIVO",
                "is_operadora_mdm_resolvida": True,
                "is_cnpj_operadora_estrutural_valido": True,
                "has_excecao_bloqueante": False,
                "mdm_confidence_score": 0.98,
                "mdm_status": "ATIVO",
                "dt_processamento": "2025-03-01T00:00:00",
            }
        ],
        "meta": {
            "fonte": "api_premium_contrato_validado",
            "competencia": "todas",
            "versao_dataset": "contrato_validado_v1",
            "total": 1,
            "pagina": 1,
            "por_pagina": 50,
            "cache": "miss",
        },
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_premium_operadoras_retorna_payload(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_operadora(dataset, **kw):
        return _payload_operadora()
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_operadora
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/operadoras?competencia=202501", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "dados" in response.json()
    assert response.json()["dados"][0]["registro_ans"] == "123456"


def test_premium_cnes_estabelecimentos_retorna_payload(monkeypatch) -> None:
    payload = {
        "dados": [{
            "competencia": "202501", "cnes": "1234567", "cnes_normalizado": "1234567",
            "cnpj_normalizado": "11222333000181", "razao_social": "ESTAB TESTE",
            "nome_fantasia": None, "sg_uf": "SP", "cd_municipio": "3550308",
            "nm_municipio": "SAO PAULO", "tipo_unidade": "HOSPITAL",
            "tipo_unidade_desc": "Hospital", "cnes_formato_valido": True,
            "cnpj_digito_valido": True, "documento_quality_status": "VALIDO",
            "motivo_invalidade_documento": None, "quality_score_cnes": 100.0,
        }],
        "meta": {"fonte": "api_premium_cnes", "competencia": "202501", "versao_dataset": "v1", "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss"},
    }
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_cnes(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_cnes
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(
            "/v1/premium/cnes/estabelecimentos?competencia=202501",
            headers={"X-API-Key": "ok"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dados"][0]["cnes"] == "1234567"


def test_premium_tiss_procedimentos_retorna_payload(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_tiss(dataset, **kw):
        return _payload_tiss()
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_tiss
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(
            "/v1/premium/tiss/procedimentos?trimestre=2025T1",
            headers={"X-API-Key": "ok"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dados"][0]["cd_procedimento_tuss"] == "12345678"


def test_premium_tuss_procedimentos_retorna_payload(monkeypatch) -> None:
    payload = {
        "dados": [{
            "codigo_tuss": "12345678", "descricao_tuss": "CONSULTA MEDICA",
            "grupo": "CONSULTAS", "subgrupo": "CONSULTA MEDICA",
            "capitulo": None, "vigencia_inicio": "2020-01-01",
            "vigencia_fim": None, "versao_tuss": "5.0",
            "is_tuss_vigente": True, "rol_segmento": "MEDICO",
            "rol_obrigatorio_medico": True, "rol_obrigatorio_odonto": False,
            "rol_carencia_dias": 0, "rol_vigencia_inicio": "2020-01-01",
            "rol_vigencia_fim": None, "quality_score_tuss": 100.0,
            "dt_processamento": None,
        }],
        "meta": {"fonte": "api_premium_tuss", "competencia": "todas", "versao_dataset": "v1", "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss"},
    }
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_tuss(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_tuss
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/tuss/procedimentos", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dados"][0]["codigo_tuss"] == "12345678"


def test_premium_mdm_operadoras_retorna_payload(monkeypatch) -> None:
    payload = {
        "dados": [{
            "operadora_master_id": "md5operadora", "registro_ans_canonico": "123456",
            "cnpj_canonico": "11222333000181", "razao_social_canonica": "OPERADORA TESTE",
            "nome_fantasia_canonico": None, "modalidade_canonica": "MEDICINA_DE_GRUPO",
            "uf_canonica": "SP", "municipio_sede_canonico": "SAO PAULO",
            "documento_quality_status": "VALIDO", "status_mdm": "ATIVO",
            "mdm_confidence_score": 0.98, "mdm_created_at": "2025-01-01T00:00:00",
            "mdm_updated_at": None,
        }],
        "meta": {"fonte": "api_premium_mdm_operadora", "competencia": "todas", "versao_dataset": "v1", "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss"},
    }
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_mdm_op(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_mdm_op
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/mdm/operadoras", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dados"][0]["registro_ans_canonico"] == "123456"


def test_premium_mdm_prestadores_retorna_payload(monkeypatch) -> None:
    payload = {
        "dados": [{
            "prestador_master_id": "md5prestador", "estabelecimento_master_id": "md5estab",
            "operadora_master_id": "md5operadora", "cnes_canonico": "1234567",
            "cnpj_canonico": "11222333000181", "nome_prestador_canonico": "DR TESTE",
            "tipo_prestador_canonico": "MEDICO", "cd_municipio_canonico": "3550308",
            "uf_canonica": "SP", "documento_quality_status": "VALIDO",
            "status_mdm": "ATIVO", "mdm_confidence_score": 0.98,
            "mdm_created_at": "2025-01-01T00:00:00", "mdm_updated_at": None,
        }],
        "meta": {"fonte": "api_premium_mdm_prestador", "competencia": "todas", "versao_dataset": "v1", "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss"},
    }
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_mdm_pr(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_mdm_pr
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/mdm/prestadores", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dados"][0]["cnes_canonico"] == "1234567"


def test_premium_contratos_exige_tenant(monkeypatch) -> None:
    # Sem tenant_id no request.state, deve falhar
    async def fake_auth_sem_tenant(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "premium-test"
        request.state.cliente_id = None  # sem tenant
        request.state.plano_id = "plano-premium"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
        return "ok"

    app.dependency_overrides[validar_api_key] = fake_auth_sem_tenant
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/contratos", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403


def test_premium_subfaturas_exige_tenant(monkeypatch) -> None:
    async def fake_auth_sem_tenant(request: Request, x_api_key: str | None = None):
        request.state.chave_api_id = "premium-test"
        request.state.cliente_id = None
        request.state.plano_id = "plano-premium"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1"]
        request.state.camadas_permitidas = ["ouro", "prata", "bronze", "premium"]
        return "ok"

    app.dependency_overrides[validar_api_key] = fake_auth_sem_tenant
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/subfaturas", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403


def test_premium_plano_nao_premium_retorna_403(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth_nao_premium()
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/operadoras?competencia=202501", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403


def test_premium_nao_altera_endpoint_legado(monkeypatch) -> None:
    # Testa que um endpoint público legado continua funcionando
    app.dependency_overrides[validar_api_key] = _fake_auth_nao_premium()
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/operadora/360", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    # Endpoint pode retornar 200 ou 403 (plano sem acesso) — o importante é não retornar 500/erro novo
    assert response.status_code in (200, 403, 404)


def test_premium_envelope_possui_meta_qualidade(monkeypatch) -> None:
    payload = {
        "dados": [
            {
                "fonte_documento": "operadora",
                "documento_quality_status": "VALIDO",
                "total_registro": 10, "total_fonte": 10,
                "total_valido": 10, "total_invalido": 0,
                "taxa_valido": 1.0, "quality_score_documental": 100.0,
            }
        ],
        "meta": {
            "fonte": "api_premium_quality_dataset",
            "competencia": "todas",
            "versao_dataset": "quality_dataset_v1",
            "total": 1, "pagina": 1, "por_pagina": 50, "cache": "miss",
        },
    }
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_quality(dataset, **kw):
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_quality
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get("/v1/premium/quality/datasets", headers={"X-API-Key": "ok"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    json_data = response.json()
    assert "dados" in json_data
    assert "meta" in json_data
    assert "quality_score_documental" in json_data["dados"][0]


def test_premium_paginacao_obrigatoria(monkeypatch) -> None:
    app.dependency_overrides[validar_api_key] = _fake_auth_premium()
    async def _mock_buscar_premium_paginacao(dataset, **kw):
        pagina = kw.get("pagina", 1)
        limite = kw.get("limite", 50)
        payload = _payload_operadora()
        payload["meta"]["pagina"] = pagina
        payload["meta"]["por_pagina"] = limite
        return payload
    monkeypatch.setattr(
        "api.app.routers.premium.buscar_premium", _mock_buscar_premium_paginacao
    )
    monkeypatch.setattr("api.app.middleware.log_requisicao.registrar_log_uso", _fake_log_uso)
    try:
        response = client.get(
            "/v1/premium/operadoras?competencia=202501&pagina=2&limite=10",
            headers={"X-API-Key": "ok"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["pagina"] == 2
    assert meta["por_pagina"] == 10