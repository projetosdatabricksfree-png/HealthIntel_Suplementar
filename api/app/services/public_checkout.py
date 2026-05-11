import asyncio
import json
import secrets
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.security import gerar_hash_sha256


async def confirmar_checkout(session_id: str, plano_bd: str) -> dict:
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "STRIPE_NAO_CONFIGURADO", "mensagem": "Checkout nao disponivel neste ambiente."},  # noqa: E501
        )

    try:
        import stripe as _stripe

        _stripe.api_key = settings.stripe_secret_key
        session = await asyncio.to_thread(
            _stripe.checkout.Session.retrieve,
            session_id,
            expand=["customer_details"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"codigo": "STRIPE_SESSAO_INVALIDA", "mensagem": str(exc)},
        ) from exc

    if getattr(session, "payment_status", None) != "paid":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"codigo": "PAGAMENTO_NAO_CONFIRMADO", "mensagem": "Pagamento ainda nao confirmado no Stripe."},  # noqa: E501
        )

    customer_details = getattr(session, "customer_details", None)
    email = (getattr(customer_details, "email", None) or "").strip() if customer_details else ""
    nome = (getattr(customer_details, "name", None) or "").strip() if customer_details else ""
    if not nome:
        nome = email.split("@")[0]

    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"codigo": "EMAIL_AUSENTE", "mensagem": "Email nao encontrado na sessao Stripe."},  # noqa: E501
        )

    prefixo = ("hi_" + secrets.token_urlsafe(7).replace("-", "x").replace("_", "y"))[:10]
    corpo = secrets.token_urlsafe(32)
    chave_plain = f"{prefixo}_{corpo}"
    hash_chave = gerar_hash_sha256(chave_plain)

    async with SessionLocal() as db:
        audit_row = await db.execute(
            text(
                "SELECT id FROM plataforma.auditoria_cobranca "
                "WHERE payload->>'session_id' = :sid AND evento = 'checkout_stripe' LIMIT 1"
            ),
            {"sid": session_id},
        )
        if audit_row.mappings().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo": "SESSAO_JA_PROCESSADA",
                    "mensagem": "Esta sessao Stripe ja foi processada. Acesse o portal com sua chave existente.",  # noqa: E501
                },
            )

        plano_row = await db.execute(
            text("SELECT id FROM plataforma.plano WHERE nome = :nome LIMIT 1"),
            {"nome": plano_bd},
        )
        plano_rec = plano_row.mappings().first()
        if not plano_rec:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"codigo": "PLANO_NAO_ENCONTRADO", "mensagem": f"Plano '{plano_bd}' nao cadastrado em plataforma.plano."},  # noqa: E501
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
                    "UPDATE plataforma.cliente SET plano_id = cast(:plano_id as uuid), status = 'ativo' "  # noqa: E501
                    "WHERE id = cast(:cliente_id as uuid)"
                ),
                {"plano_id": plano_id, "cliente_id": cliente_id},
            )
        else:
            cliente_id = str(uuid4())
            await db.execute(
                text(
                    "INSERT INTO plataforma.cliente (id, nome, email, status, plano_id, criado_em) "
                    "VALUES (cast(:id as uuid), :nome, :email, 'ativo', cast(:plano_id as uuid), now())"  # noqa: E501
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
                "payload": json.dumps({"session_id": session_id, "plano_bd": plano_bd, "chave_id": chave_id}),  # noqa: E501
            },
        )
        await db.commit()

    return {
        "dados": {
            "chave_api": chave_plain,
            "prefixo": prefixo,
            "email": email,
            "plano": plano_bd,
            "criado_em": datetime.now(tz=UTC).isoformat(),
        },
        "meta": {
            "aviso": "Salve a chave_api agora. Ela nao sera exibida novamente.",
        },
    }
