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
    "sandbox": {
        "nome": "Sandbox Tecnico",
        "plano_bd": "starter_local",
        "price_attr": "stripe_price_sandbox",
    },
    "piloto": {
        "nome": "Piloto Assistido",
        "plano_bd": "piloto",
        "price_attr": "stripe_price_piloto",
    },
    "core": {
        "nome": "Core API",
        "plano_bd": "essencial",
        "price_attr": "stripe_price_core_api",
    },
}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _metadata(session: Any) -> dict[str, Any]:
    raw = _get(session, "metadata", {}) or {}
    if isinstance(raw, dict):
        return raw
    return dict(raw)


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


async def criar_sessao_checkout(plano: str) -> dict:
    settings = _config_stripe_obrigatoria()
    plano_cfg = _plano_checkout(plano)
    price_id = (getattr(settings, plano_cfg["price_attr"]) or "").strip()
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "STRIPE_PRICE_NAO_CONFIGURADO",
                "mensagem": f"Price Stripe nao configurado para o plano '{plano}'.",
            },
        )

    stripe = _importar_stripe(settings)
    frontend_url = settings.frontend_public_url.rstrip("/")
    success_url = f"{frontend_url}/checkout/sucesso?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{frontend_url}/precos"

    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.create,
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            allow_promotion_codes=True,
            billing_address_collection="auto",
            customer_creation="always",
            metadata={
                "plano": plano,
                "plano_bd": plano_cfg["plano_bd"],
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
    if event_type != "checkout.session.completed":
        return {"dados": {"status": "ignorado", "evento": event_type}}

    session = _get(_get(event, "data", {}), "object", {})
    resultado = await provisionar_checkout_pago(session)
    return {"dados": resultado}


async def confirmar_checkout(session_id: str, plano_bd: str | None = None) -> dict:
    """Fallback compatível: confirma a sessão e dispara provisionamento sem expor a chave."""
    settings = _config_stripe_obrigatoria()
    stripe = _importar_stripe(settings)
    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.retrieve,
            session_id,
            expand=["customer_details"],
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

    provisionamento = await _persistir_provisionamento(session_id, plano, plano_bd, email, nome)
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
    session_id: str, plano: str, plano_bd: str, email: str, nome: str
) -> dict:
    prefixo = ("hi_" + secrets.token_urlsafe(7).replace("-", "x").replace("_", "y"))[:10]
    corpo = secrets.token_urlsafe(32)
    chave_plain = f"{prefixo}_{corpo}"
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
