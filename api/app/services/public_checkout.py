from __future__ import annotations

import asyncio
import json
import logging
import secrets
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.security import gerar_hash_sha256
from api.app.services.email_service import (
    enviar_email_async,
    montar_email_api_key,
)

logger = logging.getLogger(__name__)

PLANOS_CHECKOUT = {
    "starter": {
        "nome": "STARTER",
        "plano_bd": "starter",
        "price_attr_mensal": "stripe_price_starter",
        "price_attr_anual": "stripe_price_starter_anual",
    },
    "pro": {
        "nome": "PRO",
        "plano_bd": "pro",
        "price_attr_mensal": "stripe_price_pro",
        "price_attr_anual": "stripe_price_pro_anual",
    },
    "max": {
        "nome": "MAX",
        "plano_bd": "max",
        "price_attr_mensal": "stripe_price_max",
        "price_attr_anual": "stripe_price_max_anual",
    },
}

CICLOS_VALIDOS = {"mensal", "anual"}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _metadata(session: Any) -> dict[str, Any]:
    raw = _get(session, "metadata", {}) or {}
    if isinstance(raw, dict):
        return raw
    return dict(raw)


def _id_stripe(valor: Any) -> str:
    if not valor:
        return ""
    if isinstance(valor, str):
        return valor
    return str(_get(valor, "id", "") or "")


def _plano_checkout(plano: str) -> dict[str, str]:
    try:
        return PLANOS_CHECKOUT[plano]
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "PLANO_CHECKOUT_INVALIDO",
                "mensagem": "Plano de checkout invalido.",
            },
        ) from exc


def _mapa_price_para_plano(settings: Any) -> dict[str, str]:
    """Mapa reverso price_id -> plano_bd, cobrindo ciclos mensal e anual."""
    mapa: dict[str, str] = {}
    for cfg in PLANOS_CHECKOUT.values():
        for attr in (cfg["price_attr_mensal"], cfg["price_attr_anual"]):
            price_id = (getattr(settings, attr, "") or "").strip()
            if price_id:
                mapa[price_id] = cfg["plano_bd"]
    return mapa


async def _plano_bd_por_line_items(session_id: str, settings: Any) -> str:
    """Resolve plano_bd pelo price_id dos line items (fallback p/ Payment Links sem metadata)."""
    if not session_id:
        return ""
    mapa = _mapa_price_para_plano(settings)
    if not mapa:
        return ""
    stripe = _importar_stripe(settings)
    try:
        line_items = await asyncio.to_thread(
            stripe.checkout.Session.list_line_items, session_id, limit=10
        )
    except Exception as exc:  # pragma: no cover - chamada de runtime
        logger.warning("Falha ao listar line items da sessao %s: %s", session_id, exc)
        return ""
    for item in _get(line_items, "data", []) or []:
        price_id = _id_stripe(_get(item, "price"))
        if price_id in mapa:
            return mapa[price_id]
    return ""


def _normalizar_ciclo(ciclo: str | None) -> str:
    valor = (ciclo or "mensal").strip().lower()
    if valor not in CICLOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "CICLO_INVALIDO",
                "mensagem": "Ciclo de cobranca invalido. Use 'mensal' ou 'anual'.",
            },
        )
    return valor


def _config_stripe_obrigatoria() -> Any:
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "STRIPE_NAO_CONFIGURADO",
                "mensagem": "Checkout nao disponivel neste ambiente.",
            },
        )
    return settings


def _importar_stripe(settings: Any) -> Any:
    try:
        import stripe as _stripe
    except Exception as exc:  # pragma: no cover - dependencia de runtime
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "STRIPE_INDISPONIVEL", "mensagem": str(exc)},
        ) from exc

    _stripe.api_key = settings.stripe_secret_key
    return _stripe


def _extrair_customer_details(session: Any) -> tuple[str, str]:
    customer_details = _get(session, "customer_details")
    email = (_get(customer_details, "email", "") or "").strip() if customer_details else ""
    nome = (_get(customer_details, "name", "") or "").strip() if customer_details else ""
    customer_email = (_get(session, "customer_email", "") or "").strip()
    if not email:
        email = customer_email
    if not nome and email:
        nome = email.split("@")[0]
    return email, nome


async def criar_sessao_checkout(plano: str, ciclo: str | None = None) -> dict:
    settings = _config_stripe_obrigatoria()
    plano_cfg = _plano_checkout(plano)
    ciclo_norm = _normalizar_ciclo(ciclo)
    price_attr = (
        plano_cfg["price_attr_anual"] if ciclo_norm == "anual" else plano_cfg["price_attr_mensal"]
    )
    price_id = (getattr(settings, price_attr, "") or "").strip()
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "STRIPE_PRICE_NAO_CONFIGURADO",
                "mensagem": f"Price Stripe nao configurado para '{plano}' ciclo '{ciclo_norm}'.",
            },
        )

    stripe = _importar_stripe(settings)
    frontend_url = settings.frontend_public_url.rstrip("/")
    success_url = f"{frontend_url}/checkout/sucesso?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{frontend_url}/precos"

    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.create,
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            allow_promotion_codes=True,
            billing_address_collection="auto",
            metadata={
                "plano": plano,
                "plano_bd": plano_cfg["plano_bd"],
                "ciclo": ciclo_norm,
            },
            subscription_data={
                "metadata": {
                    "plano": plano,
                    "plano_bd": plano_cfg["plano_bd"],
                    "ciclo": ciclo_norm,
                }
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"codigo": "STRIPE_SESSAO_NAO_CRIADA", "mensagem": str(exc)},
        ) from exc

    return {
        "dados": {
            "checkout_url": _get(session, "url"),
            "session_id": _get(session, "id"),
            "plano": plano,
            "ciclo": ciclo_norm,
        }
    }


async def processar_webhook_checkout(payload: bytes, stripe_signature: str | None) -> dict:
    settings = _config_stripe_obrigatoria()
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "STRIPE_WEBHOOK_NAO_CONFIGURADO",
                "mensagem": "Webhook Stripe nao configurado neste ambiente.",
            },
        )
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"codigo": "STRIPE_ASSINATURA_AUSENTE", "mensagem": "Assinatura ausente."},
        )

    stripe = _importar_stripe(settings)
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"codigo": "STRIPE_WEBHOOK_INVALIDO", "mensagem": str(exc)},
        ) from exc

    event_type = _get(event, "type")
    objeto = _get(_get(event, "data", {}), "object", {})
    if event_type == "checkout.session.completed":
        resultado = await provisionar_checkout_pago(objeto)
        return {"dados": resultado}
    if event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        resultado = await sincronizar_assinatura_stripe(objeto, event_type)
        return {"dados": resultado}
    if event_type in {"invoice.payment_succeeded", "invoice.payment_failed"}:
        resultado = await sincronizar_fatura_stripe(objeto, event_type)
        return {"dados": resultado}

    return {"dados": {"status": "ignorado", "evento": event_type}}


async def confirmar_checkout(session_id: str, plano_bd: str | None = None) -> dict:
    """Fallback compatível: confirma a sessão e dispara provisionamento sem expor a chave."""
    settings = _config_stripe_obrigatoria()
    stripe = _importar_stripe(settings)
    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.retrieve,
            session_id,
            expand=["customer_details", "customer", "subscription"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"codigo": "STRIPE_SESSAO_INVALIDA", "mensagem": str(exc)},
        ) from exc

    resultado = await provisionar_checkout_pago(session, plano_bd_fallback=plano_bd)
    return {"dados": resultado}


async def provisionar_checkout_pago(session: Any, plano_bd_fallback: str | None = None) -> dict:
    session_id = _get(session, "id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"codigo": "STRIPE_SESSAO_SEM_ID", "mensagem": "Sessao Stripe sem id."},
        )

    if _get(session, "payment_status") != "paid":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "codigo": "PAGAMENTO_NAO_CONFIRMADO",
                "mensagem": "Pagamento ainda nao confirmado no Stripe.",
            },
        )

    metadata = _metadata(session)
    plano = str(metadata.get("plano") or "").strip()
    plano_bd = str(metadata.get("plano_bd") or plano_bd_fallback or "").strip()
    subscription_id = _id_stripe(_get(session, "subscription"))
    customer_id = _id_stripe(_get(session, "customer"))
    if not plano_bd:
        # Payment Links estaticos nao carregam metadata.plano_bd: resolve pelo price_id.
        plano_bd = await _plano_bd_por_line_items(str(session_id), get_settings())
    if not plano_bd:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "PLANO_AUSENTE",
                "mensagem": "Plano nao encontrado na sessao Stripe.",
            },
        )

    email, nome = _extrair_customer_details(session)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "EMAIL_AUSENTE",
                "mensagem": "Email nao encontrado na sessao Stripe.",
            },
        )

    provisionamento = await _persistir_provisionamento(
        session_id=session_id,
        plano=plano,
        plano_bd=plano_bd,
        email=email,
        nome=nome,
        customer_id=customer_id,
        subscription_id=subscription_id,
        payment_status=str(_get(session, "payment_status", "") or ""),
    )
    if provisionamento["status"] == "ja_processado":
        return provisionamento

    email_status = await _enviar_email_api_key(
        email=email,
        nome=nome,
        plano=plano or plano_bd,
        chave_api=provisionamento["chave_api"],
        criado_em=provisionamento["criado_em"],
    )
    await _atualizar_email_status(session_id, email_status)

    return {
        "status": "provisionado",
        "email": email,
        "plano": plano or plano_bd,
        "email_status": email_status,
        "chave_id": provisionamento["chave_id"],
    }


async def _persistir_provisionamento(
    *,
    session_id: str,
    plano: str,
    plano_bd: str,
    email: str,
    nome: str,
    customer_id: str,
    subscription_id: str,
    payment_status: str,
) -> dict:
    corpo = secrets.token_urlsafe(40).replace("-", "x").replace("_", "y")
    chave_plain = f"hi_live_{corpo}"
    prefixo = chave_plain[:10]
    hash_chave = gerar_hash_sha256(chave_plain)
    criado_em = datetime.now(tz=UTC).isoformat()

    async with SessionLocal() as db:
        audit_row = await db.execute(
            text(
                "SELECT id, payload FROM plataforma.auditoria_cobranca "
                "WHERE payload->>'session_id' = :sid AND evento = 'checkout_stripe' LIMIT 1"
            ),
            {"sid": session_id},
        )
        audit_rec = audit_row.mappings().first()
        if audit_rec:
            payload = audit_rec.get("payload") or {}
            return {
                "status": "ja_processado",
                "email": email,
                "plano": plano or plano_bd,
                "email_status": payload.get("email_status"),
                "chave_id": payload.get("chave_id"),
            }

        plano_row = await db.execute(
            text("SELECT id FROM plataforma.plano WHERE nome = :nome LIMIT 1"),
            {"nome": plano_bd},
        )
        plano_rec = plano_row.mappings().first()
        if not plano_rec:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "codigo": "PLANO_NAO_ENCONTRADO",
                    "mensagem": f"Plano '{plano_bd}' nao cadastrado em plataforma.plano.",
                },
            )
        plano_id = str(plano_rec["id"])

        existing = await db.execute(
            text("SELECT id FROM plataforma.cliente WHERE email = :email LIMIT 1"),
            {"email": email},
        )
        cliente_rec = existing.mappings().first()
        if cliente_rec:
            cliente_id = str(cliente_rec["id"])
            await db.execute(
                text(
                    "UPDATE plataforma.cliente SET plano_id = cast(:plano_id as uuid), "
                    "status = 'ativo' WHERE id = cast(:cliente_id as uuid)"
                ),
                {"plano_id": plano_id, "cliente_id": cliente_id},
            )
        else:
            cliente_id = str(uuid4())
            await db.execute(
                text(
                    "INSERT INTO plataforma.cliente (id, nome, email, status, plano_id, criado_em) "
                    "VALUES (cast(:id as uuid), :nome, :email, 'ativo', "
                    "cast(:plano_id as uuid), now())"
                ),
                {"id": cliente_id, "nome": nome, "email": email, "plano_id": plano_id},
            )

        chave_id = str(uuid4())
        await db.execute(
            text(
                """
                INSERT INTO plataforma.chave_api
                  (id, cliente_id, plano_id, hash_chave, prefixo_chave, status, criado_em)
                VALUES (
                  cast(:chave_id as uuid), cast(:cliente_id as uuid), cast(:plano_id as uuid),
                  :hash_chave, :prefixo, 'ativo', now()
                )
                """
            ),
            {
                "chave_id": chave_id,
                "cliente_id": cliente_id,
                "plano_id": plano_id,
                "hash_chave": hash_chave,
                "prefixo": prefixo,
            },
        )

        await db.execute(
            text(
                """
                INSERT INTO plataforma.auditoria_cobranca
                  (id, evento, cliente_id, ator, origem, payload, criado_em)
                VALUES (
                  gen_random_uuid(), 'checkout_stripe', cast(:cliente_id as uuid),
                  :ator, 'stripe_checkout', cast(:payload as jsonb), now()
                )
                """
            ),
            {
                "cliente_id": cliente_id,
                "ator": email,
                "payload": json.dumps(
                    {
                        "session_id": session_id,
                        "customer_id": customer_id,
                        "subscription_id": subscription_id,
                        "payment_status": payment_status,
                        "plano": plano,
                        "plano_bd": plano_bd,
                        "chave_id": chave_id,
                        "email": email,
                        "email_status": "pendente",
                    }
                ),
            },
        )
        await db.commit()

    return {
        "status": "provisionado",
        "chave_api": chave_plain,
        "chave_id": chave_id,
        "email": email,
        "plano": plano or plano_bd,
        "criado_em": criado_em,
    }


async def sincronizar_assinatura_stripe(subscription: Any, event_type: str) -> dict:
    subscription_id = _id_stripe(subscription)
    customer_id = _id_stripe(_get(subscription, "customer"))
    status_stripe = str(_get(subscription, "status", "") or "")
    metadata = _metadata(subscription)
    plano_bd = str(metadata.get("plano_bd") or metadata.get("plano") or "").strip()
    status_cobranca = _status_cobranca_por_assinatura(status_stripe, event_type)
    payload = {
        "event_type": event_type,
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "status_stripe": status_stripe,
        "status_cobranca": status_cobranca,
        "plano_bd": plano_bd,
        "cancel_at_period_end": bool(_get(subscription, "cancel_at_period_end", False)),
        "current_period_end": _get(subscription, "current_period_end"),
    }
    return await _atualizar_cliente_por_stripe(
        evento="stripe_subscription",
        ator=subscription_id or customer_id or "stripe",
        subscription_id=subscription_id,
        customer_id=customer_id,
        status_cobranca=status_cobranca,
        plano_bd=plano_bd,
        payload=payload,
    )


async def sincronizar_fatura_stripe(invoice: Any, event_type: str) -> dict:
    subscription_id = _id_stripe(_get(invoice, "subscription"))
    customer_id = _id_stripe(_get(invoice, "customer"))
    status_cobranca = "em_dia" if event_type == "invoice.payment_succeeded" else "inadimplente"
    payload = {
        "event_type": event_type,
        "invoice_id": _id_stripe(invoice),
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "status_stripe": str(_get(invoice, "status", "") or ""),
        "status_cobranca": status_cobranca,
        "amount_paid": _get(invoice, "amount_paid"),
        "amount_due": _get(invoice, "amount_due"),
        "hosted_invoice_url": _get(invoice, "hosted_invoice_url"),
        "invoice_pdf": _get(invoice, "invoice_pdf"),
    }
    return await _atualizar_cliente_por_stripe(
        evento="stripe_invoice",
        ator=_id_stripe(invoice) or subscription_id or customer_id or "stripe",
        subscription_id=subscription_id,
        customer_id=customer_id,
        status_cobranca=status_cobranca,
        plano_bd="",
        payload=payload,
    )


def _status_cobranca_por_assinatura(status_stripe: str, event_type: str) -> str:
    if event_type == "customer.subscription.deleted" or status_stripe == "canceled":
        return "cancelado"
    if status_stripe in {"active", "trialing"}:
        return "em_dia"
    if status_stripe in {"past_due", "unpaid", "incomplete", "incomplete_expired"}:
        return "inadimplente"
    return "pendente"


async def _atualizar_cliente_por_stripe(
    *,
    evento: str,
    ator: str,
    subscription_id: str,
    customer_id: str,
    status_cobranca: str,
    plano_bd: str,
    payload: dict[str, Any],
) -> dict:
    if not subscription_id and not customer_id:
        return {"status": "ignorado", "motivo": "stripe_id_ausente", "evento": evento}

    async with SessionLocal() as db:
        audit_row = await db.execute(
            text(
                """
                SELECT cliente_id
                FROM plataforma.auditoria_cobranca
                WHERE evento = 'checkout_stripe'
                  AND (
                    (:subscription_id <> '' AND payload->>'subscription_id' = :subscription_id)
                    OR (:customer_id <> '' AND payload->>'customer_id' = :customer_id)
                  )
                ORDER BY criado_em DESC
                LIMIT 1
                """
            ),
            {"subscription_id": subscription_id, "customer_id": customer_id},
        )
        audit_rec = audit_row.mappings().first()
        if not audit_rec or not audit_rec.get("cliente_id"):
            return {"status": "ignorado", "motivo": "cliente_nao_encontrado", "evento": evento}

        cliente_id = str(audit_rec["cliente_id"])
        plano_id = None
        if plano_bd:
            plano_row = await db.execute(
                text("SELECT id FROM plataforma.plano WHERE nome = :nome LIMIT 1"),
                {"nome": plano_bd},
            )
            plano_rec = plano_row.mappings().first()
            plano_id = str(plano_rec["id"]) if plano_rec else None

        if plano_id:
            await db.execute(
                text(
                    """
                    UPDATE plataforma.cliente
                    SET status_cobranca = :status_cobranca,
                        status = CASE WHEN :status_cobranca = 'cancelado' THEN 'cancelado' ELSE status END,
                        plano_id = cast(:plano_id as uuid)
                    WHERE id = cast(:cliente_id as uuid)
                    """
                ),
                {
                    "cliente_id": cliente_id,
                    "status_cobranca": status_cobranca,
                    "plano_id": plano_id,
                },
            )
        else:
            await db.execute(
                text(
                    """
                    UPDATE plataforma.cliente
                    SET status_cobranca = :status_cobranca,
                        status = CASE WHEN :status_cobranca = 'cancelado' THEN 'cancelado' ELSE status END
                    WHERE id = cast(:cliente_id as uuid)
                    """
                ),
                {"cliente_id": cliente_id, "status_cobranca": status_cobranca},
            )

        await db.execute(
            text(
                """
                INSERT INTO plataforma.auditoria_cobranca
                  (id, evento, cliente_id, ator, origem, payload, criado_em)
                VALUES (
                  gen_random_uuid(), :evento, cast(:cliente_id as uuid),
                  :ator, 'stripe_webhook', cast(:payload as jsonb), now()
                )
                """
            ),
            {
                "evento": evento,
                "cliente_id": cliente_id,
                "ator": ator,
                "payload": json.dumps(payload),
            },
        )
        await db.commit()

    return {
        "status": "sincronizado",
        "evento": evento,
        "cliente_id": cliente_id,
        "status_cobranca": status_cobranca,
    }


async def _enviar_email_api_key(
    *, email: str, nome: str, plano: str, chave_api: str, criado_em: str
) -> str:
    subject, body_text, body_html = montar_email_api_key(
        {
            "nome": nome,
            "email": email,
            "plano": plano,
            "chave_api": chave_api,
            "criado_em": criado_em,
        }
    )
    return await enviar_email_async(subject, body_text, body_html, to_email=email)


async def _atualizar_email_status(session_id: str, email_status: str) -> None:
    try:
        async with SessionLocal() as db:
            await db.execute(
                text(
                    """
                    UPDATE plataforma.auditoria_cobranca
                    SET payload = jsonb_set(
                        payload, '{email_status}', to_jsonb(cast(:status as text)), true
                    )
                    WHERE evento = 'checkout_stripe' AND payload->>'session_id' = :sid
                    """
                ),
                {"status": email_status, "sid": session_id},
            )
            await db.commit()
    except Exception as exc:  # pragma: no cover - auditoria auxiliar
        logger.exception("Falha ao atualizar status de email do checkout: %s", exc)
