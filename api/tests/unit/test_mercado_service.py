import pytest

from api.app.services import mercado as service


@pytest.mark.asyncio
async def test_vazio_assistencial_usa_cache(monkeypatch) -> None:
    payload = {
        "dados": [{"cd_municipio": "3550308", "segmento": "MEDICO"}],
        "meta": {"cache": "miss"},
    }

    async def fake_get(_chave: str) -> dict:
        return payload

    monkeypatch.setattr(service, "_obter_cache", fake_get)

    response = await service.listar_vazios_assistenciais()

    assert response["dados"][0]["cd_municipio"] == "3550308"
    assert response["meta"]["cache"] == "hit"
