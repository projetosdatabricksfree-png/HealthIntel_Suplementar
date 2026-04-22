import pytest

from api.app.services import financeiro_v2 as service


@pytest.mark.asyncio
async def test_financeiro_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.detalhar_financeiro_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"


@pytest.mark.asyncio
async def test_score_v2_usa_cache(monkeypatch) -> None:
    payload = {"dados": [{"registro_ans": "123456"}], "meta": {"cache": "miss"}}

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.detalhar_score_v2_operadora("123456")

    assert response["dados"][0]["registro_ans"] == "123456"
    assert response["meta"]["cache"] == "hit"
