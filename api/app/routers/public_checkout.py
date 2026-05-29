from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field

from api.app.services.public_checkout import (
    confirmar_checkout,
    criar_sessao_checkout,
    processar_webhook_checkout,
)

router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutConfirmarRequest(BaseModel):
    session_id: str = Field(..., description="Stripe Checkout Session ID.")
    plano_bd: str | None = Field(
        default=None, description="Nome do plano em plataforma.plano (fallback legado)."
    )


class CheckoutSessaoRequest(BaseModel):
    plano: str = Field(..., description="Slug do plano publico: starter, pro ou max.")
    ciclo: str | None = Field(
        default="mensal",
        description="Ciclo de cobranca: 'mensal' (padrao) ou 'anual' (2 meses gratis).",
    )


@router.post("/confirmar", status_code=201)
async def post_confirmar_checkout(payload: CheckoutConfirmarRequest) -> dict:
    """Fallback: verifica pagamento Stripe e provisiona chave API sem expor a chave."""
    return await confirmar_checkout(payload.session_id, payload.plano_bd)


@router.post("/sessao", status_code=201)
async def post_criar_sessao_checkout(payload: CheckoutSessaoRequest) -> dict:
    """Cria uma Stripe Checkout Session para o plano e ciclo informados."""
    return await criar_sessao_checkout(payload.plano, payload.ciclo)


@router.post("/webhook", include_in_schema=False)
async def post_checkout_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
) -> dict:
    """Recebe eventos Stripe assinados e provisiona acesso quando o pagamento conclui."""
    payload = await request.body()
    return await processar_webhook_checkout(payload, stripe_signature)
