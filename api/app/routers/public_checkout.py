from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.app.services.public_checkout import confirmar_checkout

router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutConfirmarRequest(BaseModel):
    session_id: str = Field(..., description="Stripe Checkout Session ID.")
    plano_bd: str = Field(..., description="Nome do plano em plataforma.plano (ex: starter_local).")


@router.post("/confirmar", status_code=201)
async def post_confirmar_checkout(payload: CheckoutConfirmarRequest) -> dict:
    """Verifica pagamento Stripe e provisiona chave API. Idempotente por session_id."""
    return await confirmar_checkout(payload.session_id, payload.plano_bd)
