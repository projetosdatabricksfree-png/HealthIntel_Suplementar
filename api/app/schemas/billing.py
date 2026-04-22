from pydantic import BaseModel, Field


class BillingFechamentoRequest(BaseModel):
    referencia: str = Field(..., description="Referencia mensal no formato YYYY-MM.")
    cliente_id: str | None = Field(default=None, description="Cliente especifico a consolidar.")
    ator: str = Field(default="sistema", description="Responsavel pelo fechamento.")
    origem: str = Field(default="manual", description="Origem da operacao.")


class BillingUpgradeRequest(BaseModel):
    cliente_id: str
    plano_destino_id: str
    motivo: str
    ator: str = Field(default="sistema")
    origem: str = Field(default="manual")
    rotacionar_chaves: bool = Field(default=False)
