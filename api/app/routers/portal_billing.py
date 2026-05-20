"""Portal: billing — resumo do plano, Customer Portal Stripe, invoices."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.dependencia_sessao import obter_usuario_sessao

router = APIRouter(prefix="/portal/billing", tags=["portal-billing"])


def _stripe_lib() -> Any:
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "STRIPE_NAO_CONFIGURADO", "mensagem": "Stripe não configurado neste ambiente."},
        )
    try:
        import stripe as _stripe
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "STRIPE_NAO_INSTALADO", "mensagem": "Biblioteca stripe não disponível."},
        ) from exc
    _stripe.api_key = settings.stripe_secret_key
    return _stripe


async def _tenant_e_cliente(request: Request, usuario_id: str) -> tuple[str, dict]:
    tid = getattr(request.state, "tenant_ativo_id", None)
    if not tid:
        raise HTTPException(status_code=403, detail={"codigo": "SEM_TENANT", "mensagem": "Nenhum tenant ativo na sessão."})
    async with SessionLocal() as db:
        row = (await db.execute(
            text("""
                select c.id, c.nome, c.email, p.nome as plano_nome, p.limite_rpm,
                       p.endpoint_permitido, p.limite_api_keys
                from plataforma.cliente c
                join plataforma.plano p on p.id = c.plano_id
                where c.id = :cid
            """),
            {"cid": tid},
        )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail={"codigo": "TENANT_NAO_ENCONTRADO", "mensagem": "Tenant não encontrado."})
    return str(tid), dict(row)


@router.get("/resumo")
async def resumo_billing(
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    cliente_id, cliente = await _tenant_e_cliente(request, usuario_id)

    async with SessionLocal() as db:
        assinatura = (await db.execute(
            text("""
                select status, stripe_subscription_id, stripe_customer_id,
                       current_period_start, current_period_end, cancel_at_period_end
                from plataforma.assinatura
                where cliente_id = :cid
                order by criado_em desc limit 1
            """),
            {"cid": cliente_id},
        )).mappings().first()

        uso_hoje = (await db.execute(
            text("""
                select count(*) as total
                from plataforma.log_uso lu
                join plataforma.chave_api ca on ca.id = lu.chave_id
                where ca.cliente_id = :cid
                  and date(lu.timestamp_req) = current_date
            """),
            {"cid": cliente_id},
        )).scalar_one()

        chaves_ativas = (await db.execute(
            text("select count(*) from plataforma.chave_api where cliente_id = :cid and status = 'ativo'"),
            {"cid": cliente_id},
        )).scalar_one()

    return {
        "dados": {
            "plano": {
                "nome": cliente["plano_nome"],
                "limite_rpm": cliente["limite_rpm"],
                "limite_api_keys": cliente["limite_api_keys"],
            },
            "assinatura": {
                "status": assinatura["status"] if assinatura else None,
                "stripe_subscription_id": assinatura["stripe_subscription_id"] if assinatura else None,
                "current_period_end": assinatura["current_period_end"].isoformat() if (assinatura and assinatura["current_period_end"]) else None,
                "cancel_at_period_end": bool(assinatura["cancel_at_period_end"]) if assinatura else False,
            } if assinatura else None,
            "uso_hoje": uso_hoje,
            "chaves_ativas": chaves_ativas,
        }
    }


@router.post("/customer-portal")
async def customer_portal(
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    cliente_id, cliente = await _tenant_e_cliente(request, usuario_id)

    async with SessionLocal() as db:
        assinatura = (await db.execute(
            text("select stripe_customer_id from plataforma.assinatura where cliente_id = :cid order by criado_em desc limit 1"),
            {"cid": cliente_id},
        )).mappings().first()

    if not assinatura or not assinatura["stripe_customer_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"codigo": "SEM_ASSINATURA_STRIPE", "mensagem": "Nenhuma assinatura Stripe encontrada para este cliente."},
        )

    stripe = _stripe_lib()
    settings = get_settings()
    return_url = f"{settings.app_url}/app/billing" if hasattr(settings, "app_url") and settings.app_url else "https://www.healthintel.com.br/app/billing"

    try:
        session = await asyncio.to_thread(
            stripe.billing_portal.Session.create,
            customer=assinatura["stripe_customer_id"],
            return_url=return_url,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"codigo": "STRIPE_ERRO", "mensagem": str(exc)},
        ) from exc

    return {"dados": {"url": session.url}}


@router.get("/faturas")
async def listar_faturas(
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
    limit: int = 10,
) -> dict:
    cliente_id, _ = await _tenant_e_cliente(request, usuario_id)

    async with SessionLocal() as db:
        assinatura = (await db.execute(
            text("select stripe_customer_id from plataforma.assinatura where cliente_id = :cid order by criado_em desc limit 1"),
            {"cid": cliente_id},
        )).mappings().first()

    if not assinatura or not assinatura["stripe_customer_id"]:
        return {"dados": []}

    stripe = _stripe_lib()
    try:
        invoices = await asyncio.to_thread(
            stripe.Invoice.list,
            customer=assinatura["stripe_customer_id"],
            limit=min(limit, 24),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"codigo": "STRIPE_ERRO", "mensagem": str(exc)},
        ) from exc

    def _fmt(inv: Any) -> dict:
        return {
            "id": inv.id,
            "numero": inv.number,
            "data": inv.created,
            "valor_centavos": inv.amount_paid,
            "moeda": inv.currency,
            "status": inv.status,
            "pdf_url": inv.invoice_pdf,
            "descricao": inv.lines.data[0].description if inv.lines and inv.lines.data else None,
        }

    return {"dados": [_fmt(inv) for inv in invoices.data]}
