from collections.abc import Sequence

from fastapi import Header, HTTPException, Request, status
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.core.security import gerar_hash_sha256


async def validar_api_key(request: Request, x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo_erro": "CHAVE_INVALIDA", "mensagem": "Header X-API-Key ausente."},
        )

    hash_chave = gerar_hash_sha256(x_api_key)
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
                detail={"codigo_erro": "CHAVE_INVALIDA", "mensagem": "Chave de API invalida."},
            )
        if row["status_chave"] != "ativo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"codigo_erro": "CHAVE_INATIVA", "mensagem": "Chave de API inativa."},
            )
        if row["status_cliente"] != "ativo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "codigo_erro": "CLIENTE_SUSPENSO",
                    "mensagem": "Cliente sem acesso ao produto.",
                },
            )

        endpoints_permitidos = list(row["endpoint_permitido"] or [])
        if endpoints_permitidos and not _endpoint_permitido(request.url.path, endpoints_permitidos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "codigo_erro": "PLANO_SEM_ACESSO",
                    "mensagem": "Plano sem acesso a este endpoint.",
                },
            )

        await session.execute(
            text(
                """
                update plataforma.chave_api
                set ultimo_uso_em = now()
                where id = :chave_id
                """
            ),
            {"chave_id": row["chave_id"]},
        )
        await session.commit()

    request.state.chave_api = row["prefixo_chave"].strip()
    request.state.chave_api_id = str(row["chave_id"])
    request.state.cliente_id = str(row["cliente_id"])
    request.state.plano_id = str(row["plano_id"])
    request.state.limite_rpm = int(row["limite_rpm"])
    request.state.endpoint_permitido = endpoints_permitidos
    return x_api_key


def _endpoint_permitido(endpoint: str, permitidos: Sequence[str]) -> bool:
    return any(endpoint.startswith(prefixo) for prefixo in permitidos)
