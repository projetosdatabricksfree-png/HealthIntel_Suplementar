from fastapi import APIRouter, Depends, Query

from api.app.middleware.autenticacao import validar_api_key
from api.app.schemas.billing import BillingFechamentoRequest, BillingUpgradeRequest
from api.app.services.billing import (
    fechar_ciclo_faturamento,
    listar_resumo_faturamento,
    registrar_upgrade_plano,
)

router = APIRouter(
    prefix="/admin/billing",
    tags=["admin-billing"],
    dependencies=[Depends(validar_api_key)],
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
