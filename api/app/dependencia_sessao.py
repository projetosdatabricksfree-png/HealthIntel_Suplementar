"""Dependência de sessão para endpoints /v1/portal/* e /v1/me/* (exceto /v1/me/uso).

Paralela a validar_chave — não substitui, não interfere.
"""

from __future__ import annotations

import jwt
from fastapi import Header, HTTPException, Request, status


def _extrair_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    partes = authorization.split(" ", 1)
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return None
    return partes[1]


async def obter_usuario_sessao(
    request: Request,
    authorization: str | None = Header(default=None),
) -> str:
    """Valida JWT de sessão e popula request.state com usuario_id, tenant_ativo_id, role."""
    from api.app.core.security import decodificar_access_token

    token = _extrair_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "TOKEN_AUSENTE", "mensagem": "Header Authorization Bearer ausente."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decodificar_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "TOKEN_EXPIRADO", "mensagem": "Token expirado."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "TOKEN_INVALIDO", "mensagem": "Token inválido."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.usuario_id = payload["sub"]
    request.state.tenant_ativo_id = payload.get("tenant")
    request.state.role = payload.get("role", "viewer")
    return payload["sub"]


def verificar_role(*roles_permitidos: str):
    """Closure dep: autentica JWT e garante que o usuário tenha um dos roles informados."""
    from fastapi import Depends

    async def _verificar(
        request: Request,
        usuario_id: str = Depends(obter_usuario_sessao),
    ) -> str:
        role: str = getattr(request.state, "role", "viewer")
        if role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "codigo": "ROLE_INSUFICIENTE",
                    "mensagem": f"Acesso restrito a: {', '.join(roles_permitidos)}.",
                },
            )
        return usuario_id

    return _verificar
