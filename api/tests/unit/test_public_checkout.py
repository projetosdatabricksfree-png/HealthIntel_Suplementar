from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from api.app.services import public_checkout


def _settings(**overrides):
    base = {
        "stripe_secret_key": "sk_test",
        "stripe_webhook_secret": "whsec_test",
        "stripe_price_starter": "price_starter",
        "stripe_price_pro": "price_pro",
        "stripe_price_max": "price_max",
        "stripe_price_sandbox": "price_sandbox",
        "stripe_price_piloto": "price_piloto",
        "stripe_price_core_api": "price_core",
        "frontend_public_url": "https://app.healthintel.test",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.mark.asyncio
async def test_criar_sessao_checkout_usa_price_e_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    class FakeSession:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return {"id": "cs_test_sandbox", "url": "https://checkout.stripe.test/session"}

    fake_stripe = SimpleNamespace(checkout=SimpleNamespace(Session=FakeSession), api_key=None)
    monkeypatch.setitem(sys.modules, "stripe", fake_stripe)
    monkeypatch.setattr(public_checkout, "get_settings", lambda: _settings())

    result = await public_checkout.criar_sessao_checkout("starter")

    assert result["dados"]["checkout_url"] == "https://checkout.stripe.test/session"
    assert captured["mode"] == "subscription"
    assert captured["line_items"] == [{"price": "price_starter", "quantity": 1}]
    assert captured["metadata"] == {"plano": "starter", "plano_bd": "starter"}
    assert captured["subscription_data"] == {
        "metadata": {"plano": "starter", "plano_bd": "starter"}
    }
    assert captured["success_url"].startswith("https://app.healthintel.test/checkout/sucesso")
    assert captured["cancel_url"] == "https://app.healthintel.test/precos"


@pytest.mark.asyncio
async def test_criar_sessao_checkout_rejeita_plano_invalido(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(public_checkout, "get_settings", lambda: _settings())

    with pytest.raises(HTTPException) as exc:
        await public_checkout.criar_sessao_checkout("enterprise")

    assert exc.value.status_code == 422
    assert exc.value.detail["codigo"] == "PLANO_CHECKOUT_INVALIDO"


@pytest.mark.asyncio
async def test_webhook_exige_assinatura(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(public_checkout, "get_settings", lambda: _settings())

    with pytest.raises(HTTPException) as exc:
        await public_checkout.processar_webhook_checkout(b"{}", None)

    assert exc.value.status_code == 400
    assert exc.value.detail["codigo"] == "STRIPE_ASSINATURA_AUSENTE"


@pytest.mark.asyncio
async def test_webhook_checkout_completed_provisiona(monkeypatch: pytest.MonkeyPatch) -> None:
    session = {"id": "cs_test", "payment_status": "paid"}

    class FakeWebhook:
        @staticmethod
        def construct_event(payload, signature, secret):
            assert payload == b"{}"
            assert signature == "sig"
            assert secret == "whsec_test"
            return {"type": "checkout.session.completed", "data": {"object": session}}

    fake_stripe = SimpleNamespace(Webhook=FakeWebhook, api_key=None)
    monkeypatch.setitem(sys.modules, "stripe", fake_stripe)
    monkeypatch.setattr(public_checkout, "get_settings", lambda: _settings())

    async def fake_provisionar(sess):
        assert sess is session
        return {"status": "provisionado", "email_status": "enviado"}

    monkeypatch.setattr(public_checkout, "provisionar_checkout_pago", fake_provisionar)

    result = await public_checkout.processar_webhook_checkout(b"{}", "sig")

    assert result == {"dados": {"status": "provisionado", "email_status": "enviado"}}
