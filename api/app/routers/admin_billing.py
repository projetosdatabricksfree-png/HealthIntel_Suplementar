from fastapi import APIRouter, Depends, Path, Query

from api.app.dependencia import verificar_admin
from api.app.middleware.autenticacao import validar_api_key
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.schemas.billing import (
    BillingFechamentoRequest,
    BillingUpgradeRequest,
    ChaveCriacaoRequest,
)
from api.app.services.billing import (
    criar_chave_api,
    fechar_ciclo_faturamento,
    listar_resumo_faturamento,
    registrar_upgrade_plano,
)

router = APIRouter(
    prefix="/admin/billing",
    tags=["admin-billing"],
    dependencies=[Depends(validar_api_key), Depends(verificar_admin), Depends(aplicar_rate_limit)],
)


@router.get("/resumo")
async def get_resumo_billing(
    referencia: str = Query(..., description="Referencia mensal no formato YYYY-MM."),
    cliente_id: str | None = Query(default=None),
) -> dict:
    return await listar_resumo_faturamento(referencia=referencia, cliente_id=cliente_id)


@router.post("/fechar-ciclo")
async def post_fechar_ciclo_billing(payload: BillingFechamentoRequest) -> dict:
    return await fechar_ciclo_faturamento(payload)


@router.post("/upgrade")
async def post_upgrade_plano(payload: BillingUpgradeRequest) -> dict:
    return await registrar_upgrade_plano(payload)


@router.post("/clientes/{cliente_id}/chaves", status_code=201)
async def post_criar_chave_cliente(
    payload: ChaveCriacaoRequest,
    cliente_id: str = Path(..., description="UUID do cliente."),
) -> dict:
    """Cria uma chave API para o cliente. A chave plain-text e retornada uma unica vez."""
    return await criar_chave_api(cliente_id, payload)
