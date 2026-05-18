"""Inventário completo tabela a tabela do PostgreSQL HealthIntel.

Gera 3 arquivos:
  /opt/healthintel/auditoria_tabela_a_tabela.csv
  /opt/healthintel/relatorio_tabela_a_tabela.md
  /opt/healthintel/diagnostico_tabelas_finais_cliente.md

Estratégia de contagem:
  - n_live_tup > 1_000_000 → usa n_live_tup como estimativa (evita varredura de 42M+ linhas)
  - demais → COUNT(*) real

Read-only: apenas SELECTs. Não modifica nenhuma tabela.

Execução:
    cd /opt/healthintel && .venv/bin/python scripts/auditoria/gerar_inventario_completo.py
"""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

REPO = Path(__file__).resolve().parents[2]

DSN = os.environ.get(
    "POSTGRES_ADMIN_DSN",
    "postgresql://healthintel:healthintel@localhost:5432/healthintel",
)

LAYER_MAP = {
    "bruto_ans": "bronze",
    "nucleo_ans": "gold/núcleo",
    "api_ans": "serving/API",
    "consumo_ans": "serving/cliente",
    "ref_ans": "referência",
    "plataforma": "governança",
    "consumo_premium_ans": "premium",
    "quality_ans": "qualidade",
    "mdm_ans": "MDM público",
    "mdm_privado": "MDM privado",
    "bruto_cliente": "bronze cliente",
    "public": "sistema",
    "stg_ans": "staging",
    "int_ans": "intermediate",
    "stg_cliente": "staging cliente",
}

# Prioridade de coluna temporal para detecção de cobertura
TEMPORAL_PRIORITY = ["competencia", "trimestre", "mes", "periodo", "ano"]

# Threshold acima do qual usa estimativa em vez de COUNT(*)
COUNT_ESTIMATE_THRESHOLD = 1_000_000

# Causa provável para tabelas vazias por padrão de nome
CAUSA_VAZIA = [
    ("tiss", "Fonte TISS não carregada em bruto_ans"),
    ("sip", "Fonte SIB/SIP não carregada ou registro_ans=NULL no bruto"),
    ("cnes", "Fonte CNES não carregada em bruto_ans"),
    ("rede", "Fonte rede assistencial não carregada em bruto_ans"),
    ("fip", "Fonte FIP não carregada em bruto_ans"),
    ("vda", "Fonte VDA não carregada em bruto_ans"),
    ("ressarcimento", "Fonte ressarcimento não carregada em bruto_ans"),
    ("portabilidade", "Fonte portabilidade não carregada em bruto_ans"),
    ("cadop", "CADOP não carregado em bruto_ans"),
    ("beneficiario", "SIB beneficiário não materializado via dbt"),
    ("precificacao", "painel_precificacao: registro_ans=NULL em todos os registros brutos"),
    ("prestador", "produto_prestador: registro_ans=NULL em todos os registros brutos"),
    ("mapa_assistencial", "sip_mapa_assistencial: registro_ans=NULL em todos os registros brutos"),
    ("premium", "Schema premium/MDM não implementado nesta fase"),
    ("mdm", "MDM não carregado/implementado nesta fase"),
    ("quality", "Checks de qualidade não executados nesta fase"),
    ("glosa", "VDA/glosa: fonte VDA não carregada em bruto_ans"),
    ("financeiro", "fat_vda_operadora: fonte VDA não carregada em bruto_ans"),
]


def causa_provavel(schema: str, tabela: str) -> str:
    if schema in ("consumo_premium_ans", "mdm_ans", "mdm_privado", "quality_ans", "bruto_cliente"):
        return "Schema premium/MDM/quality não implementado nesta fase"
    nome = tabela.lower()
    for chave, causa in CAUSA_VAZIA:
        if chave in nome:
            return causa
    return "Fonte bruta ausente ou dbt model dependente de dado não carregado"


@dataclass
class RegistroTabela:
    schema: str
    tabela: str
    tipo_relacao: str
    camada_medallion: str
    count_registros: int
    count_tipo: str  # 'real' ou 'estimado'
    status: str      # 'preenchida' | 'vazia' | 'erro'
    total_bytes: int
    data_bytes: int
    index_bytes: int
    num_colunas: int
    pk_colunas: str
    col_temporal: str
    min_periodo: str
    max_periodo: str
    periodos_distintos: int
    observacao: str


def conectar() -> psycopg2.extensions.connection:
    print(f"[inventario] Conectando: {DSN.split('@')[-1]}", file=sys.stderr)
    conn = psycopg2.connect(DSN)
    conn.set_session(readonly=True, autocommit=True)
    return conn


def buscar_tabelas(cur) -> list[dict]:
    cur.execute("""
        SELECT
            t.table_schema,
            t.table_name,
            t.table_type,
            COALESCE(s.n_live_tup, 0) AS n_live_tup,
            COALESCE(pg_total_relation_size(
                format('%I.%I', t.table_schema, t.table_name)), 0) AS total_bytes,
            COALESCE(pg_relation_size(
                format('%I.%I', t.table_schema, t.table_name)), 0) AS data_bytes,
            COALESCE(pg_indexes_size(
                format('%I.%I', t.table_schema, t.table_name)), 0) AS index_bytes,
            (SELECT COUNT(*) FROM information_schema.columns c
             WHERE c.table_schema = t.table_schema
               AND c.table_name = t.table_name) AS num_colunas
        FROM information_schema.tables t
        LEFT JOIN pg_stat_user_tables s
            ON s.schemaname = t.table_schema AND s.relname = t.table_name
        WHERE t.table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
        ORDER BY t.table_schema, t.table_name
    """)
    return cur.fetchall()


def buscar_pks(cur) -> dict[tuple, str]:
    cur.execute("""
        SELECT tc.table_schema, tc.table_name,
               string_agg(kcu.column_name, ', '
                   ORDER BY kcu.ordinal_position) AS pk_colunas
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
        GROUP BY tc.table_schema, tc.table_name
    """)
    return {(r["table_schema"], r["table_name"]): r["pk_colunas"] for r in cur.fetchall()}


def buscar_colunas_temporais(cur) -> dict[tuple, str]:
    cur.execute("""
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
          AND (
            column_name IN ('competencia','trimestre','mes','periodo','ano')
            OR column_name LIKE 'data%'
          )
        ORDER BY table_schema, table_name,
          CASE column_name
            WHEN 'competencia' THEN 1
            WHEN 'trimestre'   THEN 2
            WHEN 'mes'         THEN 3
            WHEN 'periodo'     THEN 4
            WHEN 'ano'         THEN 5
            ELSE 6
          END
    """)
    resultado: dict[tuple, str] = {}
    for r in cur.fetchall():
        chave = (r["table_schema"], r["table_name"])
        if chave not in resultado:
            resultado[chave] = r["column_name"]
    return resultado


def count_real(cur, schema: str, tabela: str) -> tuple[int, str]:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{tabela}"')
        return cur.fetchone()["count"], "real"
    except Exception as e:
        return -1, f"erro: {e}"


def cobertura_temporal(cur, schema: str, tabela: str, col: str) -> tuple[str, str, int]:
    try:
        cur.execute(
            f'SELECT MIN("{col}")::text, MAX("{col}")::text, '
            f'COUNT(DISTINCT "{col}") FROM "{schema}"."{tabela}"'
        )
        row = cur.fetchone()
        return (
            str(row["min"] or ""),
            str(row["max"] or ""),
            int(row["count_distinct"] or 0),
        )
    except Exception:
        return "", "", 0


def fmt_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def gerar_inventario(conn) -> list[RegistroTabela]:
    registros: list[RegistroTabela] = []

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        print("[inventario] Buscando metadados de tabelas...", file=sys.stderr)
        tabelas = buscar_tabelas(cur)
        total = len(tabelas)
        print(f"[inventario] {total} tabelas encontradas.", file=sys.stderr)

        print("[inventario] Buscando PKs...", file=sys.stderr)
        pks = buscar_pks(cur)

        print("[inventario] Buscando colunas temporais...", file=sys.stderr)
        colunas_temporais = buscar_colunas_temporais(cur)

        for i, row in enumerate(tabelas, 1):
            schema = row["table_schema"]
            tabela = row["table_name"]
            tipo = row["table_type"]
            n_live = int(row["n_live_tup"] or 0)
            total_bytes = int(row["total_bytes"] or 0)
            data_bytes = int(row["data_bytes"] or 0)
            index_bytes = int(row["index_bytes"] or 0)
            num_colunas = int(row["num_colunas"] or 0)
            camada = LAYER_MAP.get(schema, schema)
            pk = pks.get((schema, tabela), "")
            col_temp = colunas_temporais.get((schema, tabela), "")

            # Contagem
            if n_live > COUNT_ESTIMATE_THRESHOLD:
                count = n_live
                count_tipo = "estimado"
            else:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur2:
                    count_val, count_tipo = count_real(cur2, schema, tabela)
                    count = count_val

            # Status
            if count_tipo.startswith("erro"):
                status = "erro"
                obs = count_tipo
            elif count > 0:
                status = "preenchida"
                obs = ""
            else:
                status = "vazia"
                obs = causa_provavel(schema, tabela)

            # Cobertura temporal
            min_p = max_p = ""
            periodos = 0
            if status == "preenchida" and col_temp:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur3:
                    try:
                        cur3.execute(
                            f'SELECT MIN("{col_temp}")::text AS min, '
                            f'MAX("{col_temp}")::text AS max, '
                            f'COUNT(DISTINCT "{col_temp}") AS count_distinct '
                            f'FROM "{schema}"."{tabela}"'
                        )
                        r = cur3.fetchone()
                        if r:
                            min_p = str(r["min"] or "")
                            max_p = str(r["max"] or "")
                            periodos = int(r["count_distinct"] or 0)
                    except Exception:
                        pass

            if i % 20 == 0 or i == total:
                print(f"[inventario] {i}/{total} — {schema}.{tabela} ({status})", file=sys.stderr)

            registros.append(RegistroTabela(
                schema=schema,
                tabela=tabela,
                tipo_relacao=tipo,
                camada_medallion=camada,
                count_registros=count,
                count_tipo=count_tipo,
                status=status,
                total_bytes=total_bytes,
                data_bytes=data_bytes,
                index_bytes=index_bytes,
                num_colunas=num_colunas,
                pk_colunas=pk,
                col_temporal=col_temp,
                min_periodo=min_p,
                max_periodo=max_p,
                periodos_distintos=periodos,
                observacao=obs,
            ))

    return registros


# ─── Geração dos arquivos de saída ────────────────────────────────────────────

def gerar_csv(registros: list[RegistroTabela], destino: Path) -> None:
    colunas = [
        "schema", "tabela", "tipo_relacao", "camada_medallion",
        "count_registros", "count_tipo", "status",
        "total_bytes", "data_bytes", "index_bytes",
        "num_colunas", "pk_colunas",
        "col_temporal", "min_periodo", "max_periodo", "periodos_distintos",
        "observacao",
    ]
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(colunas)
        for r in registros:
            w.writerow([
                r.schema, r.tabela, r.tipo_relacao, r.camada_medallion,
                r.count_registros, r.count_tipo, r.status,
                r.total_bytes, r.data_bytes, r.index_bytes,
                r.num_colunas, r.pk_colunas,
                r.col_temporal, r.min_periodo, r.max_periodo, r.periodos_distintos,
                r.observacao,
            ])
    print(f"[inventario] CSV: {destino} ({len(registros)} linhas)", file=sys.stderr)


def gerar_relatorio_md(registros: list[RegistroTabela], destino: Path) -> None:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_tabelas = len(registros)
    total_preenchidas = sum(1 for r in registros if r.status == "preenchida")
    total_vazias = sum(1 for r in registros if r.status == "vazia")
    total_erros = sum(1 for r in registros if r.status == "erro")
    total_registros = sum(r.count_registros for r in registros if r.count_registros > 0)

    schemas_unicos = sorted({r.schema for r in registros})

    linhas = [
        f"# Relatório Tabela a Tabela — HealthIntel PostgreSQL",
        f"",
        f"**Gerado em:** {agora}  ",
        f"**Banco:** PostgreSQL 16 · Docker `healthintel_postgres`",
        f"",
        f"---",
        f"",
        f"## Resumo Executivo",
        f"",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| **Total de Tabelas** | {total_tabelas} |",
        f"| **Preenchidas** | {total_preenchidas} |",
        f"| **Vazias** | {total_vazias} |",
        f"| **Com Erro** | {total_erros} |",
        f"| **Total de Registros (estimado+real)** | {total_registros:,} |",
        f"| **Schemas** | {len(schemas_unicos)} |",
        f"",
        f"---",
        f"",
    ]

    # Sumário por schema
    linhas += [
        "## Sumário por Schema",
        "",
        "| Schema | Camada | Tabelas | Preenchidas | Vazias | Registros | Tamanho |",
        "|--------|--------|---------|-------------|--------|-----------|---------|",
    ]
    for schema in schemas_unicos:
        grupo = [r for r in registros if r.schema == schema]
        camada = grupo[0].camada_medallion if grupo else ""
        n_preen = sum(1 for r in grupo if r.status == "preenchida")
        n_vaz = sum(1 for r in grupo if r.status == "vazia")
        n_regs = sum(r.count_registros for r in grupo if r.count_registros > 0)
        tam = sum(r.total_bytes for r in grupo)
        linhas.append(
            f"| **{schema}** | {camada} | {len(grupo)} | {n_preen} | {n_vaz} "
            f"| {n_regs:,} | {fmt_bytes(tam)} |"
        )

    linhas += ["", "---", ""]

    # Detalhe por schema
    for schema in schemas_unicos:
        grupo = [r for r in registros if r.schema == schema]
        camada = grupo[0].camada_medallion if grupo else ""
        linhas += [
            f"## Schema: `{schema}` — {camada}",
            "",
            "| Tabela | Status | Registros | Tipo Count | Col. Temporal | Período (min→max) | Períodos | Tamanho |",
            "|--------|--------|-----------|-----------|---------------|-------------------|----------|---------|",
        ]
        for r in sorted(grupo, key=lambda x: (x.status != "preenchida", x.tabela)):
            periodo = f"{r.min_periodo} → {r.max_periodo}" if r.min_periodo else "—"
            icon = "✅" if r.status == "preenchida" else ("❌" if r.status == "erro" else "⬜")
            linhas.append(
                f"| `{r.tabela}` | {icon} {r.status} | {r.count_registros:,} | {r.count_tipo} "
                f"| {r.col_temporal or '—'} | {periodo} | {r.periodos_distintos or '—'} "
                f"| {fmt_bytes(r.total_bytes)} |"
            )
            if r.observacao:
                linhas.append(f"| | | | | | *{r.observacao}* | | |")
        linhas += [""]

    linhas += [
        "---",
        "",
        "## Legenda",
        "",
        "| Símbolo | Significado |",
        "|---------|-------------|",
        "| ✅ | Tabela preenchida com dados reais |",
        "| ⬜ | Tabela vazia — sem dados disponíveis |",
        "| ❌ | Erro ao consultar |",
        "| `count_tipo=real` | COUNT(*) executado |",
        "| `count_tipo=estimado` | n_live_tup usado (tabela > 1M linhas) |",
        "",
    ]

    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[inventario] Relatório MD: {destino}", file=sys.stderr)


def gerar_diagnostico_cliente_md(registros: list[RegistroTabela], destino: Path) -> None:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    api = [r for r in registros if r.schema == "api_ans"]
    consumo = [r for r in registros if r.schema == "consumo_ans"]

    api_prontas = [r for r in api if r.status == "preenchida"]
    api_vazias = [r for r in api if r.status == "vazia"]
    consumo_prontas = [r for r in consumo if r.status == "preenchida"]
    consumo_vazias = [r for r in consumo if r.status == "vazia"]

    total_api_regs = sum(r.count_registros for r in api_prontas)
    total_consumo_regs = sum(r.count_registros for r in consumo_prontas)

    # Domínios para api_ans
    DOMINIOS = [
        ("operadora", ["operadora", "cadop"]),
        ("score/ranking", ["score", "ranking", "oportunidade"]),
        ("regulatório", ["regulatorio", "igr", "idss", "nip", "glosa", "taxa", "prudencial", "regime"]),
        ("financeiro", ["diops", "financeiro", "fip"]),
        ("mercado/beneficiários", ["market_share", "sib", "municipio", "metrica"]),
        ("produtos/planos", ["produto", "plano", "historico", "tuss", "precificacao"]),
        ("rede prestadora", ["rede", "prestador", "cnes", "hospitalar", "hospitalar"]),
        ("premium/MDM", ["premium", "mdm", "quality"]),
        ("outros", []),
    ]

    def dominio_tabela(tabela: str) -> str:
        nome = tabela.lower()
        for dom, chaves in DOMINIOS[:-1]:
            if any(c in nome for c in chaves):
                return dom
        return "outros"

    linhas = [
        "# Diagnóstico: Tabelas Finais de Cliente — HealthIntel",
        "",
        f"**Gerado em:** {agora}  ",
        f"**Objetivo:** Identificar o que está pronto para uso comercial em `api_ans` e `consumo_ans`.",
        "",
        "---",
        "",
        "## Resumo Executivo",
        "",
        "| Schema | Prontas | Vazias | Total | Registros Prontos |",
        "|--------|---------|--------|-------|-------------------|",
        f"| **api_ans** | {len(api_prontas)} | {len(api_vazias)} | {len(api)} | {total_api_regs:,} |",
        f"| **consumo_ans** | {len(consumo_prontas)} | {len(consumo_vazias)} | {len(consumo)} | {total_consumo_regs:,} |",
        "",
        "---",
        "",
        "## `api_ans` — Tabelas PRONTAS para uso comercial",
        "",
        f"**{len(api_prontas)} tabelas populadas** com {total_api_regs:,} registros totais.",
        "",
        "| Domínio | Tabela | Registros | Período Coberto | Períodos Distintos |",
        "|---------|--------|-----------|-----------------|-------------------|",
    ]
    for r in sorted(api_prontas, key=lambda x: dominio_tabela(x.tabela)):
        dom = dominio_tabela(r.tabela)
        periodo = f"{r.min_periodo} → {r.max_periodo}" if r.min_periodo else "sem coluna temporal"
        linhas.append(
            f"| {dom} | `{r.tabela}` | {r.count_registros:,} "
            f"| {periodo} | {r.periodos_distintos or '—'} |"
        )

    linhas += [
        "",
        "---",
        "",
        "## `api_ans` — Tabelas VAZIAS (causa provável)",
        "",
        f"**{len(api_vazias)} tabelas sem dados** — detalhamento por domínio:",
        "",
        "| Domínio | Tabela | Causa Provável |",
        "|---------|--------|----------------|",
    ]
    for r in sorted(api_vazias, key=lambda x: dominio_tabela(x.tabela)):
        dom = dominio_tabela(r.tabela)
        linhas.append(f"| {dom} | `{r.tabela}` | {r.observacao} |")

    linhas += [
        "",
        "---",
        "",
        "## `consumo_ans` — Tabelas PRONTAS",
        "",
        f"**{len(consumo_prontas)} tabelas populadas** com {total_consumo_regs:,} registros.",
        "",
        "| Tabela | Registros | Período Coberto | Períodos Distintos |",
        "|--------|-----------|-----------------|-------------------|",
    ]
    for r in sorted(consumo_prontas, key=lambda x: x.tabela):
        periodo = f"{r.min_periodo} → {r.max_periodo}" if r.min_periodo else "sem coluna temporal"
        linhas.append(
            f"| `{r.tabela}` | {r.count_registros:,} "
            f"| {periodo} | {r.periodos_distintos or '—'} |"
        )

    linhas += [
        "",
        "---",
        "",
        "## `consumo_ans` — Tabelas VAZIAS",
        "",
        "| Tabela | Causa Provável |",
        "|--------|----------------|",
    ]
    for r in sorted(consumo_vazias, key=lambda x: x.tabela):
        linhas.append(f"| `{r.tabela}` | {r.observacao} |")

    linhas += [
        "",
        "---",
        "",
        "## Cobertura por Domínio (api_ans)",
        "",
        "| Domínio | Prontas | Vazias | Status |",
        "|---------|---------|--------|--------|",
    ]
    for dom, _ in DOMINIOS:
        prontas_dom = [r for r in api_prontas if dominio_tabela(r.tabela) == dom]
        vazias_dom = [r for r in api_vazias if dominio_tabela(r.tabela) == dom]
        if not prontas_dom and not vazias_dom:
            continue
        if vazias_dom and not prontas_dom:
            status_icon = "❌ Nenhuma pronta"
        elif prontas_dom and not vazias_dom:
            status_icon = "✅ Completo"
        else:
            status_icon = "⚠️ Parcial"
        linhas.append(f"| {dom} | {len(prontas_dom)} | {len(vazias_dom)} | {status_icon} |")

    linhas += [
        "",
        "---",
        "",
        "## Próximos Passos para Completar a Cobertura",
        "",
        "1. **Carregar CADOP** (`make dag-run-real-cadop COMPETENCIA=202605`) → desbloqueia modelos de operadora enriquecida",
        "2. **Corrigir `registro_ans=NULL`** em `painel_precificacao`, `produto_prestador_hospitalar`, `sip_mapa_assistencial` na ingestion → 75M registros desbloqueados",
        "3. **Carregar CNES** → desbloqueia tabelas de rede prestadora",
        "4. **Carregar FIP/VDA** → desbloqueia tabelas financeiras (`financeiro_operadora`, `glosa_vda`)",
        "5. **Carregar TISS** → desbloqueia tabelas de procedimentos TISS",
        "6. **Carregar SIB completo** (beneficiários) → desbloqueia `fat_beneficiario_operadora`",
        "",
    ]

    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[inventario] Diagnóstico cliente MD: {destino}", file=sys.stderr)


def main() -> None:
    conn = conectar()
    try:
        registros = gerar_inventario(conn)
    finally:
        conn.close()

    csv_dest = REPO / "auditoria_tabela_a_tabela.csv"
    relatorio_dest = REPO / "relatorio_tabela_a_tabela.md"
    diagnostico_dest = REPO / "diagnostico_tabelas_finais_cliente.md"

    gerar_csv(registros, csv_dest)
    gerar_relatorio_md(registros, relatorio_dest)
    gerar_diagnostico_cliente_md(registros, diagnostico_dest)

    # Sumário final no stderr
    total = len(registros)
    preen = sum(1 for r in registros if r.status == "preenchida")
    vazias = sum(1 for r in registros if r.status == "vazia")
    regs = sum(r.count_registros for r in registros if r.count_registros > 0)
    print(f"\n[inventario] CONCLUÍDO", file=sys.stderr)
    print(f"  Tabelas: {total} | Preenchidas: {preen} | Vazias: {vazias}", file=sys.stderr)
    print(f"  Registros totais: {regs:,}", file=sys.stderr)
    print(f"  CSV:        {csv_dest}", file=sys.stderr)
    print(f"  Relatório:  {relatorio_dest}", file=sys.stderr)
    print(f"  Diagnóstico: {diagnostico_dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
