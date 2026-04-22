from __future__ import annotations

import json
from collections.abc import Sequence

from fastapi import Header, HTTPException, Request, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.core.security import gerar_hash_sha256

settings = get_settings()


async def _obter_cache_chave(hash_chave: str) -> dict | None:
    try:
        valor = await redis_client.get(f"api_key:{hash_chave}")
    except Exception:
        return None
    if not valor:
        return None
    return json.loads(valor)


async def _salvar_cache_chave(hash_chave: str, payload: dict) -> None:
    try:
        await redis_client.set(
            f"api_key:{hash_chave}",
            json.dumps(payload),
            ex=settings.app_cache_ttl_segundos,
        )
    except Exception:
        return


def _extrair_erros(row: dict) -> dict:
    return {
        "chave_id": row["chave_id"],
        "cliente_id": row["cliente_id"],
        "plano_id": row["plano_id"],
        "prefixo_chave": row["prefixo_chave"],
        "status_chave": row["status_chave"],
        "status_cliente": row["status_cliente"],
        "limite_rpm": row["limite_rpm"],
        "endpoint_permitido": row["endpoint_permitido"],
    }


async def validar_chave(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "CHAVE_INVALIDA", "mensagem": "Header X-API-Key ausente."},
        )

    hash_chave = gerar_hash_sha256(x_api_key)
    cached = await _obter_cache_chave(hash_chave)
    if cached:
        row = cached
    else:
        async with SessionLocal() as session:
            result = await session.execute(
                text(
                    """
                    select
                        chave.id as chave_id,
                        chave.cliente_id,
                        chave.plano_id,
                        chave.prefixo_chave,
                        chave.status as status_chave,
                        cliente.status as status_cliente,
                        plano.limite_rpm,
                        plano.endpoint_permitido
                    from plataforma.chave_api chave
                    inner join plataforma.cliente cliente
                        on chave.cliente_id = cliente.id
                    inner join plataforma.plano plano
                        on chave.plano_id = plano.id
                    where chave.hash_chave = :hash_chave
                    limit 1
                    """
                ),
                {"hash_chave": hash_chave},
            )
            row = result.mappings().first()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"codigo": "CHAVE_INVALIDA", "mensagem": "Chave de API invalida."},
                )
            row = {
                "chave_id": str(row["chave_id"]),
                "cliente_id": str(row["cliente_id"]),
                "plano_id": str(row["plano_id"]),
                "prefixo_chave": str(row["prefixo_chave"]),
                "status_chave": str(row["status_chave"]),
                "status_cliente": str(row["status_cliente"]),
                "limite_rpm": int(row["limite_rpm"]),
                "endpoint_permitido": list(row["endpoint_permitido"] or []),
            }
            await _salvar_cache_chave(hash_chave, row)

    if row["status_chave"] != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"codigo": "CHAVE_INATIVA", "mensagem": "Chave de API inativa."},
        )
    if row["status_cliente"] != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"codigo": "CLIENTE_SUSPENSO", "mensagem": "Cliente sem acesso ao produto."},
        )

    endpoints_permitidos = list(row["endpoint_permitido"] or [])
    request.state.chave_api = str(row["prefixo_chave"]).strip()
    request.state.chave_api_id = str(row["chave_id"])
    request.state.cliente_id = str(row["cliente_id"])
    request.state.plano_id = str(row["plano_id"])
    request.state.limite_rpm = int(row["limite_rpm"])
    request.state.endpoint_permitido = endpoints_permitidos
    request.state.auth_cache = "hit" if cached else "miss"
    return x_api_key


async def verificar_plano(request: Request) -> None:
    endpoints_permitidos: Sequence[str] = getattr(request.state, "endpoint_permitido", [])
    if not endpoints_permitidos:
        return
    rota = request.url.path
    if not any(rota.startswith(prefixo) for prefixo in endpoints_permitidos):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "codigo": "PLANO_SEM_ACESSO",
                "mensagem": "Plano sem acesso a este endpoint.",
            },
        )
