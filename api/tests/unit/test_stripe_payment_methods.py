from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from api.app.services import stripe_payment_methods


def _settings(**overrides):
    base = {"stripe_restricted_key": "rk_test"}
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.mark.asyncio
async def test_consultar_metodo_pagamento_sanitiza_cartao(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    class FakePaymentMethod:
        @staticmethod
        def retrieve(payment_method_id):
            captured["payment_method_id"] = payment_method_id
            return {
                "id": "pm_live_123",
                "type": "card",
                "livemode": True,
                "created": 1779190000,
                "customer": "cus_live_123",
                "billing_details": {
                    "name": "Cliente PRD",
                    "email": "cliente@example.com",
                    "phone": "+5511999999999",
                    "address": {"country": "BR", "postal_code": "01000-000"},
                },
                "card": {
                    "brand": "visa",
                    "country": "BR",
                    "exp_month": 12,
                    "exp_year": 2030,
                    "funding": "credit",
                    "last4": "4242",
                    "checks": {
                        "address_line1_check": "pass",
                        "address_postal_code_check": "pass",
                        "cvc_check": "pass",
                    },
                    "networks": {"available": ["visa"], "preferred": None},
                },
            }

    fake_stripe = SimpleNamespace(PaymentMethod=FakePaymentMethod, api_key=None)
    monkeypatch.setitem(sys.modules, "stripe", fake_stripe)
    monkeypatch.setattr(stripe_payment_methods, "get_settings", lambda: _settings())

    result = await stripe_payment_methods.consultar_metodo_pagamento_stripe("pm_live_123")

    assert captured["payment_method_id"] == "pm_live_123"
    assert fake_stripe.api_key == "rk_test"
    assert result["dados"]["customer_id"] == "cus_live_123"
    assert result["dados"]["card"]["last4"] == "4242"
    assert "number" not in result["dados"]["card"]
    assert "cvc" not in result["dados"]["card"]


@pytest.mark.asyncio
async def test_consultar_metodo_pagamento_exige_rk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        stripe_payment_methods,
        "get_settings",
        lambda: _settings(stripe_restricted_key=None),
    )

    with pytest.raises(HTTPException) as exc:
        await stripe_payment_methods.consultar_metodo_pagamento_stripe("pm_live_123")

    assert exc.value.status_code == 503
    assert exc.value.detail["codigo"] == "STRIPE_RESTRICTED_KEY_AUSENTE"


@pytest.mark.asyncio
async def test_listar_metodos_pagamento_cliente(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    class FakePaymentMethod:
        @staticmethod
        def list(**kwargs):
            captured.update(kwargs)
            return {
                "has_more": False,
                "data": [
                    {
                        "id": "pm_live_123",
                        "type": "card",
                        "customer": kwargs["customer"],
                        "card": {"brand": "mastercard", "last4": "4444"},
                    }
                ],
            }

    fake_stripe = SimpleNamespace(PaymentMethod=FakePaymentMethod, api_key=None)
    monkeypatch.setitem(sys.modules, "stripe", fake_stripe)
    monkeypatch.setattr(stripe_payment_methods, "get_settings", lambda: _settings())

    result = await stripe_payment_methods.listar_metodos_pagamento_cliente_stripe(
        "cus_live_123",
        "card",
    )

    assert captured == {"customer": "cus_live_123", "type": "card"}
    assert result["meta"]["total"] == 1
    assert result["dados"][0]["card"]["last4"] == "4444"


@pytest.mark.asyncio
async def test_rejeita_ids_invalidos() -> None:
    with pytest.raises(HTTPException) as exc:
        await stripe_payment_methods.consultar_metodo_pagamento_stripe("cus_live_123")

    assert exc.value.status_code == 422
    assert exc.value.detail["codigo"] == "STRIPE_PAYMENT_METHOD_INVALIDO"
