from __future__ import annotations

import asyncio

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def main() -> None:
    async with SessionLocal() as session:
        operadora = await session.scalar(
            text(
                """
                select count(*)
                from bruto_ans.sib_beneficiario_operadora
                where competencia = 202501
                """
            )
        )
        municipio = await session.scalar(
            text(
                """
                select count(*)
                from bruto_ans.sib_beneficiario_municipio
                where competencia = 202501
                """
            )
        )
        lotes = await session.scalar(
            text(
                """
                select count(*)
                from plataforma.lote_ingestao
                where dataset in ('sib_operadora', 'sib_municipio')
                  and status in ('sucesso', 'sucesso_com_alertas', 'ignorado_duplicata')
                """
            )
        )
    if not operadora or not municipio or not lotes:
        raise SystemExit(
            {
                "erro": "smoke_sib_sem_dados",
                "operadora": operadora,
                "municipio": municipio,
                "lotes": lotes,
            }
        )
    print({"status": "ok", "operadora": operadora, "municipio": municipio, "lotes": lotes})


if __name__ == "__main__":
    asyncio.run(main())
