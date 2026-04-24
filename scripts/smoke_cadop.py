from __future__ import annotations

import asyncio

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def main() -> None:
    async with SessionLocal() as session:
        cadop = await session.scalar(
            text("select count(*) from bruto_ans.cadop where competencia = 202501")
        )
        lotes = await session.scalar(
            text(
                """
                select count(*)
                from plataforma.lote_ingestao
                where dataset = 'cadop'
                  and status in ('sucesso', 'sucesso_com_alertas', 'ignorado_duplicata')
                """
            )
        )
    if not cadop or not lotes:
        raise SystemExit({"erro": "smoke_cadop_sem_dados", "cadop": cadop, "lotes": lotes})
    print({"status": "ok", "cadop": cadop, "lotes": lotes})


if __name__ == "__main__":
    asyncio.run(main())
