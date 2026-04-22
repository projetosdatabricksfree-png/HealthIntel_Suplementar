from datetime import UTC, datetime

from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.core.security import hash_ip


async def registrar_log_uso(
    *,
    chave_id: str,
    cliente_id: str,
    plano_id: str,
    endpoint: str,
    rota: str | None,
    metodo: str,
    codigo_status: int,
    latencia_ms: int,
    cache_hit: bool,
    ip_cliente: str | None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.log_uso (
                    chave_id,
                    cliente_id,
                    plano_id,
                    endpoint,
                    rota,
                    metodo,
                    codigo_status,
                    latencia_ms,
                    cache_hit,
                    timestamp_req,
                    hash_ip
                ) values (
                    :chave_id,
                    :cliente_id,
                    :plano_id,
                    :endpoint,
                    :rota,
                    :metodo,
                    :codigo_status,
                    :latencia_ms,
                    :cache_hit,
                    :timestamp_req,
                    :hash_ip
                )
                """
            ),
            {
                "chave_id": chave_id,
                "cliente_id": cliente_id,
                "plano_id": plano_id,
                "endpoint": endpoint,
                "rota": rota,
                "metodo": metodo,
                "codigo_status": codigo_status,
                "latencia_ms": latencia_ms,
                "cache_hit": cache_hit,
                "timestamp_req": datetime.now(tz=UTC),
                "hash_ip": hash_ip(ip_cliente),
            },
        )
        await session.commit()
