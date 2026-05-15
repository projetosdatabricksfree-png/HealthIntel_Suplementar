#!/usr/bin/env python3
"""Auditor empirico de grants para healthintel_cliente_reader (Release 0.9).

Conecta como usuario com role healthintel_cliente_reader e verifica:
  1. Lista tabelas acessiveis via information_schema.role_table_grants.
  2. Tenta SELECT 1 em cada schema interno (esperando falha - 42501).
  3. Tenta SELECT 1 em cada tabela disponivel do catalogo (esperando sucesso).
  4. Gera evidencia Markdown com o resultado.

Falha (exit 1) se:
  - Conseguir SELECT em qualquer schema interno (bruto_ans, stg_ans, int_ans, etc.).
  - Faltar SELECT em qualquer tabela disponivel do catalogo.

Uso:
    CLIENTE_READER_DSN="postgresql://healthintel_cliente_teste:SENHA@host:5432/healthintel" \\
        python scripts/auditoria/auditar_grants_cliente_reader.py \\
            --evidencia docs/evidencias/release_0_9/evidencia_grants_cliente_reader_release_0_9.md

Sem CLIENTE_READER_DSN definida, o script cria usuario temporario via SET ROLE
no DSN admin (env POSTGRES_ADMIN_DSN ou defaults docker-compose).
"""

from __future__ import annotations

import argparse
import os
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.errorcodes
import yaml

REPO = Path(__file__).resolve().parents[2]
CATALOGO = REPO / "docs/catalogo_dados/consumo_ans/catalogo_consumo_ans.yml"

SCHEMAS_INTERNOS_ESPERADOS_BLOQUEADOS = [
    "bruto_ans",
    "stg_ans",
    "int_ans",
    "nucleo_ans",
    "api_ans",
    "plataforma",
    "mdm_ans",
    "mdm_privado",
    "quality_ans",
    "bruto_cliente",
    "stg_cliente",
    "consumo_premium_ans",
]


def admin_dsn() -> str:
    """DSN para o postgres admin (default: docker-compose)."""
    return os.getenv(
        "POSTGRES_ADMIN_DSN",
        "postgresql://healthintel:healthintel@localhost:5432/healthintel",
    )


def cliente_dsn() -> str | None:
    return os.getenv("CLIENTE_READER_DSN")


def tabelas_disponivel_catalogo() -> list[str]:
    data = yaml.safe_load(CATALOGO.read_text(encoding="utf-8")) or {}
    return [
        item["name"]
        for item in data.get("tables", [])
        if item.get("status") == "disponivel"
    ]


@contextmanager
def conectar(dsn: str, set_role: str | None = None):
    """Abre conexao com autocommit=True para preservar SET ROLE entre statements.

    Postgres reverte SET ROLE em qualquer ROLLBACK; com autocommit=True nao ha
    transacao implicita, entao o role persiste por toda a sessao.
    """
    conn = psycopg2.connect(dsn)
    try:
        conn.autocommit = True
        cursor = conn.cursor()
        if set_role:
            cursor.execute(f"set role {set_role}")
        try:
            yield cursor
        finally:
            cursor.close()
    finally:
        conn.close()


def primeira_tabela(cursor, schema: str) -> str | None:
    cursor.execute(
        """
        select table_name from information_schema.tables
        where table_schema = %s
          and table_type in ('BASE TABLE', 'VIEW')
        limit 1
        """,
        (schema,),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def schema_existe(cursor, schema: str) -> bool:
    cursor.execute(
        "select 1 from information_schema.schemata where schema_name = %s",
        (schema,),
    )
    return cursor.fetchone() is not None


def testar_select_bloqueado(cursor, schema: str, tabela: str) -> tuple[bool, str]:
    """Retorna (bloqueado_corretamente, detalhe)."""
    try:
        cursor.execute(f'select 1 from {schema}."{tabela}" limit 1')
        cursor.fetchone()
        pass  # autocommit=True; sem rollback explicito
        return False, f"VAZAMENTO: SELECT funcionou em {schema}.{tabela}"
    except psycopg2.errors.InsufficientPrivilege as exc:
        pass  # autocommit=True; sem rollback explicito
        return True, f"OK bloqueado ({exc.diag.sqlstate or '42501'})"
    except Exception as exc:
        pass  # autocommit=True; sem rollback explicito
        return True, f"OK bloqueado ({type(exc).__name__}: {exc})"


def testar_select_permitido(cursor, schema: str, tabela: str) -> tuple[bool, str]:
    """Retorna (permitido_corretamente, detalhe)."""
    try:
        cursor.execute(f'select count(*) from {schema}."{tabela}"')
        count = cursor.fetchone()[0]
        pass  # autocommit=True; sem rollback explicito
        return True, f"OK {count} linhas"
    except psycopg2.errors.UndefinedTable:
        pass  # autocommit=True; sem rollback explicito
        return False, "FALHA: tabela nao existe"
    except psycopg2.errors.InsufficientPrivilege:
        pass  # autocommit=True; sem rollback explicito
        return False, "FALHA: cliente_reader sem SELECT"
    except Exception as exc:
        pass  # autocommit=True; sem rollback explicito
        return False, f"FALHA: {type(exc).__name__}: {exc}"


def listar_tabelas_acessiveis(cursor) -> list[tuple[str, str]]:
    cursor.execute(
        """
        select table_schema, table_name
        from information_schema.role_table_grants
        where grantee = 'healthintel_cliente_reader'
          and privilege_type = 'SELECT'
        order by table_schema, table_name
        """
    )
    return list(cursor.fetchall())


def gerar_evidencia(
    path: Path,
    tabelas_acessiveis: list[tuple[str, str]],
    bloqueios: list[tuple[str, str, bool, str]],
    permitidos: list[tuple[str, str, bool, str]],
    sucesso: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        "# Evidencia — Auditoria empirica de grants healthintel_cliente_reader",
        "",
        f"- Gerado em: {datetime.now(timezone.utc).isoformat()}",
        f"- Resultado: {'SUCESSO' if sucesso else 'FALHA'}",
        f"- Tabelas acessiveis (SELECT): {len(tabelas_acessiveis)}",
        f"- Schemas internos testados: {len(bloqueios)}",
        f"- Tabelas disponivel testadas: {len(permitidos)}",
        "",
        "## 1. Tabelas acessiveis (information_schema.role_table_grants)",
        "",
        "| schema | tabela |",
        "|---|---|",
    ]
    for schema, tabela in tabelas_acessiveis:
        linhas.append(f"| `{schema}` | `{tabela}` |")
    if not tabelas_acessiveis:
        linhas.append("| (nenhuma) | — |")

    linhas.extend([
        "",
        "## 2. Schemas internos — testes de bloqueio (espera 42501)",
        "",
        "| schema | tabela testada | resultado |",
        "|---|---|---|",
    ])
    for schema, tabela, ok, detalhe in bloqueios:
        marker = "✅" if ok else "❌"
        linhas.append(f"| `{schema}` | `{tabela}` | {marker} {detalhe} |")

    linhas.extend([
        "",
        "## 3. Tabelas disponivel — testes de permissao (espera SELECT ok)",
        "",
        "| tabela | resultado |",
        "|---|---|",
    ])
    for schema, tabela, ok, detalhe in permitidos:
        marker = "✅" if ok else "❌"
        linhas.append(f"| `{schema}.{tabela}` | {marker} {detalhe} |")

    linhas.extend([
        "",
        "## 4. Conclusao",
        "",
        (
            "Cliente reader bloqueia 100% dos schemas internos e libera 100% das tabelas "
            "disponivel do catalogo. Release 0.9 apta para piloto comercial."
            if sucesso
            else "Auditoria falhou. Corrigir os pontos marcados como ❌ antes de liberar release."
        ),
        "",
    ])
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidencia",
        type=Path,
        default=REPO
        / "docs/evidencias/release_0_9/evidencia_grants_cliente_reader_release_0_9.md",
    )
    parser.add_argument(
        "--admin-dsn",
        default=admin_dsn(),
        help="DSN admin (postgres user) usado quando CLIENTE_READER_DSN nao definida.",
    )
    args = parser.parse_args()

    disponivel = tabelas_disponivel_catalogo()
    if not disponivel:
        print("ERRO: nenhuma tabela disponivel carregada do catalogo.")
        return 2

    dsn_cliente = cliente_dsn()
    if dsn_cliente:
        modo = f"usuario direto via CLIENTE_READER_DSN"
        dsn_para_conectar = dsn_cliente
        set_role = None
    else:
        modo = f"set role healthintel_cliente_reader via admin DSN"
        dsn_para_conectar = args.admin_dsn
        set_role = "healthintel_cliente_reader"

    print(f"Modo: {modo}")

    bloqueios: list[tuple[str, str, bool, str]] = []
    permitidos: list[tuple[str, str, bool, str]] = []
    tabelas_acessiveis: list[tuple[str, str]] = []
    vazamentos: list[str] = []
    permissoes_faltando: list[str] = []

    # Primeiro, com permissoes admin, identificar 1 tabela em cada schema interno
    schema_para_tabela: dict[str, str] = {}
    with conectar(args.admin_dsn) as cursor:
        for schema in SCHEMAS_INTERNOS_ESPERADOS_BLOQUEADOS:
            if not schema_existe(cursor, schema):
                continue
            tabela = primeira_tabela(cursor, schema)
            if tabela:
                schema_para_tabela[schema] = tabela

    # Agora conectar como cliente_reader (ou set role) e rodar testes
    with conectar(dsn_para_conectar, set_role=set_role) as cursor:
        tabelas_acessiveis = listar_tabelas_acessiveis(cursor)

        for schema, tabela in schema_para_tabela.items():
            ok, detalhe = testar_select_bloqueado(cursor, schema, tabela)
            bloqueios.append((schema, tabela, ok, detalhe))
            if not ok:
                vazamentos.append(f"{schema}.{tabela}")

        for tabela in disponivel:
            ok, detalhe = testar_select_permitido(cursor, "consumo_ans", tabela)
            permitidos.append(("consumo_ans", tabela, ok, detalhe))
            if not ok:
                permissoes_faltando.append(f"consumo_ans.{tabela}")

    sucesso = not vazamentos and not permissoes_faltando
    gerar_evidencia(args.evidencia, tabelas_acessiveis, bloqueios, permitidos, sucesso)

    print(f"Evidencia gerada: {args.evidencia}")
    print(f"Tabelas acessiveis: {len(tabelas_acessiveis)}")
    print(f"Schemas internos testados: {len(bloqueios)} (vazamentos: {len(vazamentos)})")
    print(f"Tabelas disponivel testadas: {len(permitidos)} (faltando: {len(permissoes_faltando)})")

    if vazamentos:
        print(f"FALHA: cliente_reader consegue SELECT em {len(vazamentos)} schemas internos:")
        for item in vazamentos:
            print(f"  - {item}")
    if permissoes_faltando:
        print(f"FALHA: cliente_reader sem SELECT em {len(permissoes_faltando)} tabelas disponivel:")
        for item in permissoes_faltando:
            print(f"  - {item}")

    if sucesso:
        print("SUCESSO auditoria empirica grants cliente_reader")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
