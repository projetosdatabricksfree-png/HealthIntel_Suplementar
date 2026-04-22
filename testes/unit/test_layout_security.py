import pytest
from fastapi import HTTPException

from mongo_layout_service.app.core.config import get_settings
from mongo_layout_service.app.core.security import validar_service_token

settings = get_settings()

pytestmark = pytest.mark.asyncio


async def test_validar_service_token_aceita_valor_configurado() -> None:
    resultado = await validar_service_token(settings.service_token)
    assert resultado == settings.service_token


async def test_validar_service_token_rejeita_valor_invalido() -> None:
    with pytest.raises(HTTPException) as exc:
        await validar_service_token("invalido")

    assert exc.value.status_code == 401
