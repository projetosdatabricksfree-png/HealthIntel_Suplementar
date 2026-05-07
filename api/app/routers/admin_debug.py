from fastapi import APIRouter, Depends

from api.app.core.config import get_settings
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit

router = APIRouter(
    prefix="/admin",
    tags=["admin-debug"],
    include_in_schema=False,
    dependencies=[Depends(validar_api_key), Depends(aplicar_rate_limit)],
)


@router.post("/_debug/raise")
async def debug_raise() -> dict:
    """Dispara excecao artificial para validar integracao com Sentry. Disponivel apenas em ambientes nao-prod."""
    settings = get_settings()
    if settings.app_env.lower() == "prod":
        from fastapi import HTTPException

        raise HTTPException(status_code=404)
    raise RuntimeError("debug: excecao artificial para teste de Sentry — healthintel")
