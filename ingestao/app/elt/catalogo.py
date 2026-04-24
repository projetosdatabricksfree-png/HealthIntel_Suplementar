from __future__ import annotations

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def salvar_fontes_descobertas(fontes: list[dict]) -> int:
    if not fontes:
        return 0
    sql = text(
        """
        insert into plataforma.fonte_dado_ans (
            dataset_codigo, familia, url, diretorio_origem, nome_arquivo,
            extensao, tipo_arquivo, tamanho_bytes, last_modified, ativo,
            prioridade, escopo, status_catalogacao, atualizado_em
        ) values (
            :dataset_codigo, :familia, :url, :diretorio_origem, :nome_arquivo,
            :extensao, :tipo_arquivo, :tamanho_bytes, :last_modified, :ativo,
            :prioridade, :escopo, 'descoberto', now()
        )
        on conflict (url) do update set
            dataset_codigo = excluded.dataset_codigo,
            familia = excluded.familia,
            diretorio_origem = excluded.diretorio_origem,
            nome_arquivo = excluded.nome_arquivo,
            extensao = excluded.extensao,
            tipo_arquivo = excluded.tipo_arquivo,
            tamanho_bytes = excluded.tamanho_bytes,
            last_modified = excluded.last_modified,
            ativo = excluded.ativo,
            prioridade = excluded.prioridade,
            escopo = excluded.escopo,
            status_catalogacao = excluded.status_catalogacao,
            atualizado_em = now()
        """
    )
    async with SessionLocal() as session:
        await session.execute(sql, fontes)
        await session.commit()
    return len(fontes)


async def listar_fontes_para_download(
    *,
    escopo: str,
    familias: list[str] | None = None,
    limite: int | None = None,
) -> list[dict]:
    where = ["ativo is true"]
    params: dict[str, object] = {}
    if escopo != "all_ftp":
        where.append("escopo = :escopo")
        params["escopo"] = escopo
    if familias:
        where.append("familia = any(:familias)")
        params["familias"] = familias
    limit_sql = "limit :limite" if limite else ""
    if limite:
        params["limite"] = limite
    sql = text(
        f"""
        select
            id, dataset_codigo, familia, url, diretorio_origem, nome_arquivo,
            extensao, tipo_arquivo, tamanho_bytes, last_modified, prioridade, escopo
        from plataforma.fonte_dado_ans
        where {" and ".join(where)}
        order by prioridade, familia, url
        {limit_sql}
        """
    )
    async with SessionLocal() as session:
        result = await session.execute(sql, params)
        return [dict(row._mapping) for row in result]


async def listar_arquivos_para_carga(
    *,
    escopo: str,
    familias: list[str] | None = None,
    limite: int | None = None,
) -> list[dict]:
    where = ["a.status in ('baixado', 'baixado_sem_parser')"]
    params: dict[str, object] = {}
    if escopo != "all_ftp":
        where.append("coalesce(f.escopo, :escopo) = :escopo")
        params["escopo"] = escopo
    if familias:
        where.append("a.familia = any(:familias)")
        params["familias"] = familias
    limit_sql = "limit :limite" if limite else ""
    if limite:
        params["limite"] = limite
    sql = text(
        f"""
        select
            a.id, a.fonte_id, a.dataset_codigo, a.familia, a.url,
            a.caminho_landing, a.nome_arquivo, a.hash_arquivo, a.tamanho_bytes,
            a.last_modified_origem, a.status, coalesce(f.tipo_arquivo, '') as tipo_arquivo,
            coalesce(f.extensao, '') as extensao
        from plataforma.arquivo_fonte_ans a
        left join plataforma.fonte_dado_ans f on f.id = a.fonte_id
        where {" and ".join(where)}
        order by a.created_at
        {limit_sql}
        """
    )
    async with SessionLocal() as session:
        result = await session.execute(sql, params)
        return [dict(row._mapping) for row in result]
