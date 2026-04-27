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
    rota = request.url.path
    if rota.startswith("/v1/bronze"):
        peso = 3
        camada = "bronze"
    elif rota.startswith("/v1/prata"):
        peso = 2
        camada = "prata"
    elif rota.startswith("/v1/premium"):
        peso = 2
        camada = "premium"
    else:
        peso = 1
        camada = "ouro"
    chave = f"rate_limit:{identificador}"
    try:
        total = await redis_client.incrby(chave, peso)
    except Exception:
        return

    if total == peso:
        await redis_client.expire(chave, 60)

    if total > limite_rpm:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"codigo": "LIMITE_EXCEDIDO", "mensagem": "Limite por minuto excedido."},
            headers={"Retry-After": "60"},
        )

    request.state.camada = camada
