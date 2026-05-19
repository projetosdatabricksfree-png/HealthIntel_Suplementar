from fastapi import APIRouter, Depends, Request

from api.app.dependencia import validar_chave
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services.me_service import get_uso

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/uso")
async def uso_cliente(
    request: Request,
    periodo: str = "7d",
    _: str = Depends(validar_chave),
) -> dict:
    await aplicar_rate_limit(request)
    chave_id = request.state.chave_api_id
    plano_nome = request.state.plano_nome
    return await get_uso(chave_id=chave_id, periodo=periodo, plano_nome=plano_nome)
