import pytest

from api.app.services import regulatorio_v2 as service


@pytest.mark.asyncio
async def test_score_regulatorio_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.detalhar_score_regulatorio_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"


@pytest.mark.asyncio
async def test_regime_especial_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.listar_regime_especial_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"


@pytest.mark.asyncio
async def test_portabilidade_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.listar_portabilidade_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"
