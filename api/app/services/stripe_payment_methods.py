from __future__ import annotations

import asyncio
from typing import Any

from fastapi import HTTPException, status

from api.app.core.config import get_settings


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_dict(obj: Any) -> dict[str, Any]:
    if not obj:
        return {}
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {}


def _id_stripe(valor: Any) -> str:
    if not valor:
        return ""
    if isinstance(valor, str):
        return valor
    return str(_get(valor, "id", "") or "")


def _config_stripe_restrita() -> Any:
    settings = get_settings()
    if not settings.stripe_restricted_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "STRIPE_RESTRICTED_KEY_AUSENTE",
                "mensagem": "Chave restrita Stripe nao configurada neste ambiente.",
            },
        )
    return settings


def _importar_stripe_restrito(settings: Any) -> Any:
    try:
        import stripe as _stripe
    except Exception as exc:  # pragma: no cover - dependencia de runtime
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "STRIPE_INDISPONIVEL", "mensagem": str(exc)},
        ) from exc

    _stripe.api_key = settings.stripe_restricted_key
    return _stripe


def _validar_payment_method_id(payment_method_id: str) -> str:
    valor = payment_method_id.strip()
    if not valor.startswith("pm_") or len(valor) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "STRIPE_PAYMENT_METHOD_INVALIDO",
                "mensagem": "Payment Method ID invalido.",
            },
        )
    return valor


def _validar_customer_id(customer_id: str) -> str:
    valor = customer_id.strip()
    if not valor.startswith("cus_") or len(valor) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "STRIPE_CUSTOMER_INVALIDO",
                "mensagem": "Customer ID invalido.",
            },
        )
    return valor


def _sanitizar_billing_details(details: Any) -> dict[str, Any]:
    dados = _as_dict(details)
    address = _as_dict(dados.get("address"))
    return {
        "name": dados.get("name"),
        "email": dados.get("email"),
        "phone": dados.get("phone"),
        "address": {
            "city": address.get("city"),
            "country": address.get("country"),
            "line1": address.get("line1"),
            "line2": address.get("line2"),
            "postal_code": address.get("postal_code"),
            "state": address.get("state"),
        },
    }


def _sanitizar_card(card: Any) -> dict[str, Any]:
    dados = _as_dict(card)
    checks = _as_dict(dados.get("checks"))
    networks = _as_dict(dados.get("networks"))
    return {
        "brand": dados.get("brand"),
        "country": dados.get("country"),
        "exp_month": dados.get("exp_month"),
        "exp_year": dados.get("exp_year"),
        "funding": dados.get("funding"),
        "last4": dados.get("last4"),
        "checks": {
            "address_line1_check": checks.get("address_line1_check"),
            "address_postal_code_check": checks.get("address_postal_code_check"),
            "cvc_check": checks.get("cvc_check"),
        },
        "networks": {
            "available": networks.get("available") or [],
            "preferred": networks.get("preferred"),
        },
    }


def _sanitizar_payment_method(payment_method: Any) -> dict[str, Any]:
    tipo = str(_get(payment_method, "type", "") or "")
    dados = {
        "id": _id_stripe(payment_method),
        "type": tipo,
        "livemode": bool(_get(payment_method, "livemode", False)),
        "created": _get(payment_method, "created"),
        "customer_id": _id_stripe(_get(payment_method, "customer")) or None,
        "billing_details": _sanitizar_billing_details(_get(payment_method, "billing_details")),
    }
    if tipo == "card":
        dados["card"] = _sanitizar_card(_get(payment_method, "card"))
    return dados


def _stripe_error(exc: Exception) -> HTTPException:
    status_code = getattr(exc, "http_status", None) or status.HTTP_422_UNPROCESSABLE_ENTITY
    code = getattr(exc, "code", None) or exc.__class__.__name__
    message = getattr(exc, "user_message", None) or str(exc)
    return HTTPException(
        status_code=status_code,
        detail={
            "codigo": "STRIPE_ERRO",
            "stripe_code": code,
            "mensagem": message,
        },
    )


async def consultar_metodo_pagamento_stripe(payment_method_id: str) -> dict[str, Any]:
    pm_id = _validar_payment_method_id(payment_method_id)
    settings = _config_stripe_restrita()
    stripe = _importar_stripe_restrito(settings)
    try:
        payment_method = await asyncio.to_thread(stripe.PaymentMethod.retrieve, pm_id)
    except Exception as exc:
        raise _stripe_error(exc) from exc

    return {"dados": _sanitizar_payment_method(payment_method)}


async def listar_metodos_pagamento_cliente_stripe(
    customer_id: str,
    tipo: str = "card",
) -> dict[str, Any]:
    customer = _validar_customer_id(customer_id)
    tipo_normalizado = tipo.strip() or "card"
    settings = _config_stripe_restrita()
    stripe = _importar_stripe_restrito(settings)
    try:
        result = await asyncio.to_thread(
            stripe.PaymentMethod.list,
            customer=customer,
            type=tipo_normalizado,
        )
    except Exception as exc:
        raise _stripe_error(exc) from exc

    itens = [_sanitizar_payment_method(item) for item in (_get(result, "data", []) or [])]
    return {
        "dados": itens,
        "meta": {
            "customer_id": customer,
            "type": tipo_normalizado,
            "total": len(itens),
            "has_more": bool(_get(result, "has_more", False)),
        },
    }
