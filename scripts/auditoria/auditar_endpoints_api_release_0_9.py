#!/usr/bin/env python3
"""Auditor de endpoints API para Release 0.9 Core ANS Comercial.

Cruza routers FastAPI com inventario de tabelas vazias e emite decisao
de publicar/ocultar por router e por endpoint individual.

Uso:
    python scripts/auditoria/auditar_endpoints_api_release_0_9.py \\
        --evidencia docs/evidencias/release_0_9/evidencia_api_release_0_9.md

Saida:
    - exit 0 se todos os endpoints publicaveis tem tabela origem populada;
    - exit 1 se algum endpoint publicavel aponta para tabela vazia.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROUTERS_DIR = REPO / "api" / "app" / "routers"
SERVICES_DIR = REPO / "api" / "app" / "services"
MAIN_PY = REPO / "api" / "app" / "main.py"
INVENTARIO_CSV = REPO / "docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv"

ROUTER_DECORATOR_RE = re.compile(
    r"@router\.(get|post|put|delete|patch)\s*\(\s*[\"']([^\"']+)[\"']",
    re.MULTILINE,
)
TABELA_REF_RE = re.compile(
    r"(?:from\s+|FROM\s+|\"tabela\":\s*\"|dataset_origem\":\s*\")"
    r"(api_ans|nucleo_ans|consumo_ans)\.([a-z_0-9]+)",
)
INCLUDE_ROUTER_RE = re.compile(
    r"app\.include_router\(\s*([a-z_0-9]+)\.router",
)


@dataclass
class Endpoint:
    router: str
    method: str
    path: str
    tabelas: set[str] = field(default_factory=set)
    decisao: str = "pendente"
    motivo: str = ""


def load_inventario() -> dict[str, int]:
    """Retorna mapping schema.tabela -> row_count_real."""
    if not INVENTARIO_CSV.exists():
        print(f"AVISO: inventario nao encontrado em {INVENTARIO_CSV}", file=sys.stderr)
        return {}
    mapping: dict[str, int] = {}
    with INVENTARIO_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            schema = row["schema"]
            table = row["tabela"]
            try:
                count = int(row.get("row_count_real") or 0)
            except ValueError:
                count = 0
            mapping[f"{schema}.{table}"] = count
    return mapping


def listar_routers_ativos() -> list[str]:
    """Le main.py e retorna lista de routers includes."""
    if not MAIN_PY.exists():
        return []
    texto = MAIN_PY.read_text(encoding="utf-8")
    return INCLUDE_ROUTER_RE.findall(texto)


def extrair_endpoints_router(router_name: str) -> list[Endpoint]:
    """Le arquivo do router e extrai @router.<verb>(path)."""
    router_path = ROUTERS_DIR / f"{router_name}.py"
    if not router_path.exists():
        return []
    texto = router_path.read_text(encoding="utf-8")
    endpoints: list[Endpoint] = []
    for match in ROUTER_DECORATOR_RE.finditer(texto):
        method, path = match.group(1), match.group(2)
        endpoints.append(Endpoint(router=router_name, method=method.upper(), path=path))
    return endpoints


def mapear_tabelas_router(router_name: str) -> set[str]:
    """Combina referencias de tabelas no router e no service equivalente."""
    tabelas: set[str] = set()
    for path in (ROUTERS_DIR / f"{router_name}.py", SERVICES_DIR / f"{router_name}.py"):
        if not path.exists():
            continue
        texto = path.read_text(encoding="utf-8")
        for match in TABELA_REF_RE.finditer(texto):
            schema, tabela = match.group(1), match.group(2)
            tabelas.add(f"{schema}.{tabela}")
    # Outros services correlatos
    for extra in (
        SERVICES_DIR / f"{router_name}_v2.py",
        SERVICES_DIR / "meta.py" if router_name == "meta" else None,
    ):
        if extra and extra.exists():
            texto = extra.read_text(encoding="utf-8")
            for match in TABELA_REF_RE.finditer(texto):
                schema, tabela = match.group(1), match.group(2)
                tabelas.add(f"{schema}.{tabela}")
    return tabelas


def decidir(endpoint: Endpoint, inventario: dict[str, int]) -> None:
    """Decide publicar vs ocultar baseado em tabelas referenciadas."""
    if not endpoint.tabelas:
        # endpoints sem tabela (saude, prontidao, meta-only): publicar
        endpoint.decisao = "publicar"
        endpoint.motivo = "endpoint sem tabela de dados (utilitario/meta)"
        return
    rows_por_tabela = {
        t: inventario.get(t, -1) for t in sorted(endpoint.tabelas)
    }
    tabelas_populadas = [t for t, c in rows_por_tabela.items() if c > 0]
    tabelas_vazias = [t for t, c in rows_por_tabela.items() if c == 0]
    tabelas_desconhecidas = [t for t, c in rows_por_tabela.items() if c < 0]

    if tabelas_populadas and not tabelas_vazias and not tabelas_desconhecidas:
        endpoint.decisao = "publicar"
        endpoint.motivo = f"todas tabelas populadas: {', '.join(tabelas_populadas)}"
    elif tabelas_vazias and not tabelas_populadas:
        endpoint.decisao = "ocultar"
        endpoint.motivo = f"todas tabelas zeradas: {', '.join(tabelas_vazias)}"
    elif tabelas_populadas and tabelas_vazias:
        endpoint.decisao = "publicar_parcial"
        endpoint.motivo = (
            f"populadas: {', '.join(tabelas_populadas)}; "
            f"zeradas: {', '.join(tabelas_vazias)}"
        )
    else:
        endpoint.decisao = "publicar"
        endpoint.motivo = (
            f"tabelas nao mapeadas no inventario: {', '.join(tabelas_desconhecidas)} "
            "(presumir publicar; revisar manualmente)"
        )


def decidir_router_global(endpoints: list[Endpoint]) -> str:
    """Decide se router inteiro deve ser ocultado."""
    if not endpoints:
        return "sem_endpoints"
    decisoes = {e.decisao for e in endpoints}
    if decisoes == {"ocultar"}:
        return "ocultar_router_inteiro"
    if "ocultar" in decisoes or "publicar_parcial" in decisoes:
        return "filtrar_por_endpoint"
    return "publicar_router_inteiro"


def gerar_relatorio(
    path: Path,
    endpoints_por_router: dict[str, list[Endpoint]],
    inventario: dict[str, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_router_decision = {
        r: decidir_router_global(eps) for r, eps in endpoints_por_router.items()
    }
    total_endpoints = sum(len(eps) for eps in endpoints_por_router.values())
    total_ocultar = sum(
        1 for eps in endpoints_por_router.values() for e in eps if e.decisao == "ocultar"
    )
    total_publicar = sum(
        1 for eps in endpoints_por_router.values() for e in eps if e.decisao == "publicar"
    )
    total_parcial = sum(
        1
        for eps in endpoints_por_router.values()
        for e in eps
        if e.decisao == "publicar_parcial"
    )

    linhas = [
        "# Evidencia — Auditoria API Release 0.9",
        "",
        f"- Gerado em: {datetime.now(timezone.utc).isoformat()}",
        f"- Repo: `{REPO}`",
        f"- Routers analisados: {len(endpoints_por_router)}",
        f"- Endpoints totais: {total_endpoints}",
        f"- Decisao **publicar**: {total_publicar}",
        f"- Decisao **publicar_parcial**: {total_parcial}",
        f"- Decisao **ocultar**: {total_ocultar}",
        "",
        "## Resumo por router",
        "",
        "| router | n_endpoints | decisao | tabelas referenciadas |",
        "|---|---:|---|---|",
    ]
    for router, eps in sorted(endpoints_por_router.items()):
        tabelas_router: set[str] = set()
        for e in eps:
            tabelas_router.update(e.tabelas)
        tabelas_str = ", ".join(
            f"`{t}` ({inventario.get(t, '?')})" for t in sorted(tabelas_router)
        ) or "—"
        linhas.append(
            f"| `{router}` | {len(eps)} | **{by_router_decision[router]}** | {tabelas_str} |"
        )

    linhas.extend(["", "## Endpoints detalhados", ""])
    for router, eps in sorted(endpoints_por_router.items()):
        linhas.append(f"### `{router}.py` — {by_router_decision[router]}")
        linhas.append("")
        linhas.append("| method | path | decisao | motivo |")
        linhas.append("|---|---|---|---|")
        for e in eps:
            linhas.append(
                f"| {e.method} | `{e.path}` | **{e.decisao}** | {e.motivo} |"
            )
        linhas.append("")

    # Lista de instrucoes acionaveis
    linhas.extend([
        "## Acoes recomendadas",
        "",
        "Routers a ocultar inteiramente do Swagger (include_in_schema=False no include_router):",
        "",
    ])
    for router, decisao in sorted(by_router_decision.items()):
        if decisao == "ocultar_router_inteiro":
            linhas.append(f"- `app.include_router({router}.router, ..., include_in_schema=False)`")

    linhas.extend([
        "",
        "Routers que precisam filtro por endpoint (alguns publicar, outros ocultar):",
        "",
    ])
    for router, decisao in sorted(by_router_decision.items()):
        if decisao == "filtrar_por_endpoint":
            linhas.append(f"- `{router}.py`:")
            for e in endpoints_por_router[router]:
                if e.decisao == "ocultar":
                    linhas.append(
                        f"    - adicionar `include_in_schema=False` em `{e.method} {e.path}`"
                    )

    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidencia",
        type=Path,
        default=REPO / "docs/evidencias/release_0_9/evidencia_api_release_0_9.md",
        help="Caminho da evidencia Markdown a gerar.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Falha (exit 1) se houver decisoes 'ocultar' ou 'publicar_parcial' nao tratadas.",
    )
    args = parser.parse_args()

    inventario = load_inventario()
    if not inventario:
        print("ERRO: inventario nao carregado", file=sys.stderr)
        return 2

    routers = listar_routers_ativos()
    if not routers:
        print("ERRO: nenhum router encontrado em main.py", file=sys.stderr)
        return 2

    endpoints_por_router: dict[str, list[Endpoint]] = defaultdict(list)
    for router_name in routers:
        tabelas_router = mapear_tabelas_router(router_name)
        for ep in extrair_endpoints_router(router_name):
            ep.tabelas = tabelas_router  # heuristica: todas as tabelas do router
            decidir(ep, inventario)
            endpoints_por_router[router_name].append(ep)

    gerar_relatorio(args.evidencia, endpoints_por_router, inventario)
    print(f"Evidencia gerada: {args.evidencia}")

    if args.strict:
        problemas = [
            (r, e)
            for r, eps in endpoints_por_router.items()
            for e in eps
            if e.decisao in {"ocultar", "publicar_parcial"}
        ]
        if problemas:
            print(f"FALHA strict: {len(problemas)} endpoints precisam de tratamento")
            for r, e in problemas[:20]:
                print(f"  - {r}: {e.method} {e.path} -> {e.decisao}")
            return 1

    print("SUCESSO auditoria API release 0.9")
    return 0


if __name__ == "__main__":
    sys.exit(main())
