from __future__ import annotations

import asyncio
import os

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def main() -> None:
    usuario = os.environ["CLIENTE_POSTGRES_USER"]
    senha = os.environ["CLIENTE_POSTGRES_PASSWORD"]
    if not usuario.replace("_", "").isalnum():
        raise SystemExit("CLIENTE_POSTGRES_USER deve conter apenas letras, numeros e underscore.")
    async with SessionLocal() as session:
        await session.execute(
            text(f'create user "{usuario}" login password :senha'),
            {"senha": senha},
        )
        await session.execute(text(f'grant healthintel_cliente_reader to "{usuario}"'))
        await session.commit()
    print({"status": "ok", "usuario": usuario})


if __name__ == "__main__":
    asyncio.run(main())
