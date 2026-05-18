"""Router público de contato comercial.

Recebe leads do site, persiste em `plataforma.lead_contato` e dispara email
para o destino configurado (EMAIL_CONTATO_DESTINO). Sem autenticação por
X-API-Key — é um formulário público. Tem rate limit por IP in-memory simples.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import deque

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.schemas.contato import LeadContatoIn, LeadContatoOut
from api.app.services.email_service import enviar_email_async, montar_email_lead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contato", tags=["contato"])

_RATE_LIMIT_JANELA_SEG = 60
_RATE_LIMIT_MAX = 10
_RATE_LIMIT_STORE: dict[str, deque] = {}


def _checar_rate_limit(ip: str) -> None:
    agora = time.monotonic()
    janela = _RATE_LIMIT_STORE.setdefault(ip, deque())
    while janela and janela[0] < agora - _RATE_LIMIT_JANELA_SEG:
        janela.popleft()
    if len(janela) >= _RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas solicitações deste IP. Tente novamente em alguns minutos.",
        )
    janela.append(agora)


@router.post(
    "/leads",
    response_model=LeadContatoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registra lead comercial e dispara email para a equipe.",
)
async def criar_lead(payload: LeadContatoIn, request: Request) -> LeadContatoOut:
    ip = request.client.host if request.client else "0.0.0.0"
    _checar_rate_limit(ip)

    # Honeypot: bots costumam preencher campos invisíveis. Retorna OK silencioso.
    if payload.honeypot:
        logger.info("Honeypot acionado para IP=%s, ignorando.", ip)
        return LeadContatoOut(ok=True, lead_id=None, email_status="desabilitado")

    lead_id = str(uuid.uuid4())
    persistido = False

    try:
        async with SessionLocal() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO plataforma.lead_contato (
                        id, criado_em, nome, email, empresa, perfil,
                        plano, mensagem, origem, ip_origem
                    ) VALUES (
                        :id, NOW(), :nome, :email, :empresa, :perfil,
                        :plano, :mensagem, :origem, CAST(:ip AS INET)
                    )
                    """
                ),
                {
                    "id": lead_id,
                    "nome": payload.nome,
                    "email": payload.email,
                    "empresa": payload.empresa,
                    "perfil": payload.perfil,
                    "plano": payload.plano,
                    "mensagem": payload.mensagem,
                    "origem": payload.origem,
                    "ip": ip,
                },
            )
            await session.commit()
            persistido = True
    except Exception as exc:  # pragma: no cover - logged but non-fatal
        logger.exception("Falha ao persistir lead em plataforma.lead_contato: %s", exc)

    # Dispara email em background-friendly (já é async, não bloqueia muito)
    subject, body_text, body_html = montar_email_lead(payload.model_dump())
    email_status = await enviar_email_async(subject, body_text, body_html)

    detalhe = None
    if not persistido and email_status != "enviado":
        # Nem persistiu nem enviou — falha real.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao registrar lead. Tente novamente em alguns instantes.",
        )
    if not persistido:
        detalhe = "Lead enviado por email; persistência local indisponível."

    return LeadContatoOut(
        ok=True,
        lead_id=lead_id if persistido else None,
        email_status=email_status,
        detalhe=detalhe,
    )
