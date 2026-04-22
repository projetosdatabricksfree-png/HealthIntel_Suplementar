from hmac import compare_digest

from fastapi import Header, HTTPException, status

from mongo_layout_service.app.core.config import get_settings

settings = get_settings()


async def validar_service_token(x_service_token: str | None = Header(default=None)) -> str:
    if not x_service_token or not compare_digest(x_service_token, settings.service_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "codigo_erro": "SERVICE_TOKEN_INVALIDO",
                "mensagem": "Acesso interno nao autorizado ao layout registry.",
            },
        )
    return x_service_token
