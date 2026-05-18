from typing import Literal

from pydantic import BaseModel, Field

_EMAIL_RE = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"


class LeadContatoIn(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=200, pattern=_EMAIL_RE)
    empresa: str = Field(..., min_length=1, max_length=160)
    perfil: str = Field(..., min_length=1, max_length=80)
    plano: str | None = Field(default=None, max_length=40)
    mensagem: str = Field(..., min_length=4, max_length=2000)
    origem: str | None = Field(default=None, max_length=80)
    honeypot: str | None = Field(default=None, max_length=200)


class LeadContatoOut(BaseModel):
    ok: bool
    lead_id: str | None = None
    email_status: Literal["enviado", "fila_local", "desabilitado"] | None = None
    detalhe: str | None = None
