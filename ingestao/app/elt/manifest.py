from __future__ import annotations

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def resumo_elt_ans() -> dict:
    async with SessionLocal() as session:
        fontes = await session.execute(
            text(
                """
                select familia, count(*) as total
                from plataforma.fonte_dado_ans
                group by familia
                order by total desc, familia
                """
            )
        )
        arquivos = await session.execute(
            text(
                """
                select status, count(*) as total, coalesce(sum(tamanho_bytes), 0) as bytes
                from plataforma.arquivo_fonte_ans
                group by status
                order by status
                """
            )
        )
        erros = await session.execute(
            text(
                """
                select dataset_codigo, familia, url, status, erro_mensagem
                from plataforma.arquivo_fonte_ans
                where status like 'erro_%'
                order by updated_at desc
                limit 10
                """
            )
        )
        return {
            "fontes_por_familia": [dict(row._mapping) for row in fontes],
            "arquivos_por_status": [dict(row._mapping) for row in arquivos],
            "ultimos_erros": [dict(row._mapping) for row in erros],
        }
