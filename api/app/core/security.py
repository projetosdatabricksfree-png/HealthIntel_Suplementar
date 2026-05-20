from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import bcrypt
import jwt

from api.app.core.config import get_settings


def gerar_hash_sha256(valor: str) -> str:
    return sha256(valor.encode("utf-8")).hexdigest()


def hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return gerar_hash_sha256(ip)


def hash_senha(senha: str) -> str:
    settings = get_settings()
    return bcrypt.hashpw(
        senha.encode("utf-8"), bcrypt.gensalt(rounds=settings.auth_bcrypt_rounds)
    ).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
    except Exception:
        return False


def gerar_token_aleatorio() -> tuple[str, str]:
    """Retorna (token_plain, hash_sha256) — armazenar apenas o hash."""
    token = secrets.token_urlsafe(32)
    return token, gerar_hash_sha256(token)


def gerar_access_token(usuario_id: str, cliente_id: str | None, role: str) -> str:
    settings = get_settings()
    agora = datetime.now(UTC)
    payload = {
        "sub": usuario_id,
        "tenant": cliente_id,
        "role": role,
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.auth_jwt_access_ttl_min),
    }
    return jwt.encode(payload, settings.auth_jwt_secret, algorithm=settings.auth_jwt_algo)


def decodificar_access_token(token: str) -> dict:
    """Levanta jwt.ExpiredSignatureError ou jwt.InvalidTokenError em falha."""
    settings = get_settings()
    return jwt.decode(token, settings.auth_jwt_secret, algorithms=[settings.auth_jwt_algo])
