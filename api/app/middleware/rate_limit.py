from fastapi import HTTPException, Request, status

from api.app.core.config import get_settings
from api.app.core.redis_client import redis_client

settings = get_settings()


async def aplicar_rate_limit(request: Request) -> None:
    identificador = getattr(
        request.state,
        "chave_api_id",
        getattr(request.state, "chave_api", "anonimo"),
    )
    limite_rpm = getattr(request.state, "limite_rpm", settings.app_rate_limit_rpm)
    chave = f"rate_limit:{identificador}"
    try:
        total = await redis_client.incr(chave)
    except Exception:
        return

    if total == 1:
        await redis_client.expire(chave, 60)

    if total > limite_rpm:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"codigo": "LIMITE_EXCEDIDO", "mensagem": "Limite por minuto excedido."},
            headers={"Retry-After": "60"},
        )
