#!/usr/bin/env python3
"""Hard gate comercial da camada consumo_ans.

Valida o catalogo comercial versionado, documentacao dbt/Markdown e,
quando conectado ao banco, contagem real das tabelas publicadas.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
CATALOGO = REPO / "docs/catalogo_dados/consumo_ans/catalogo_consumo_ans.yml"
CONSUMO_DIR = REPO / "healthintel_dbt/models/consumo"
CONSUMO_YML = CONSUMO_DIR / "_consumo.yml"
DOCKER_COMPOSE = REPO / "infra/docker-compose.yml"
ALLOWED_STATUS = {"disponivel", "parcial", "fora_do_escopo", "vazia_bloqueada"}
ALLOWED_OUT_OF_SCOPE = {"tiss", "sib", "sib_historico"}
SIB_DOMAINS = {"sib", "sib_historico"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as arquivo:
        data = yaml.safe_load(arquivo)
    return data or {}


def consumo_sql_models() -> set[str]:
    return {path.stem for path in CONSUMO_DIR.glob("*.sql")}


def dbt_models() -> dict[str, dict[str, Any]]:
    doc = load_yaml(CONSUMO_YML)
    return {item["name"]: item for item in doc.get("models", [])}


def has_minimum_test(model: dict[str, Any]) -> bool:
    if model.get("tests") or model.get("data_tests"):
        return True
    for column in model.get("columns", []):
        if column.get("tests") or column.get("data_tests"):
            return True
    return False


def psql(sql: str) -> str:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE),
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "healthintel",
        "-d",
        "healthintel",
        "-A",
        "-F|",
        "-t",
        "-q",
        "-c",
        sql,
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
    return resultado.stdout.strip()


def count_table(schema: str, table: str) -> int:
    regclass = psql(f"select to_regclass('{schema}.{table}') is not null;")
    if regclass.lower() != "t":
        return -1
    out = psql(f'select count(*) from "{schema}"."{table}";')
    return int(out)


def doc_contains_table(doc_path: Path, table_name: str) -> bool:
    if not doc_path.exists():
        return False
    texto = doc_path.read_text(encoding="utf-8")
    return table_name in texto


def validate(skip_db: bool, evidence_path: Path | None) -> int:
    catalog = load_yaml(CATALOGO)
    schema = catalog.get("schema", "consumo_ans")
    tables = catalog.get("tables", [])
    catalog_by_name = {item["name"]: item for item in tables}
    dbt_by_name = dbt_models()
    sql_models = consumo_sql_models()
    errors: list[str] = []
    counts: dict[str, int | None] = {}

    missing_catalog = sorted(sql_models - set(catalog_by_name))
    extra_catalog = sorted(set(catalog_by_name) - sql_models)
    if missing_catalog:
        errors.append("Modelos consumo sem catalogo comercial: " + ", ".join(missing_catalog))
    if extra_catalog:
        errors.append("Catalogo referencia modelos inexistentes: " + ", ".join(extra_catalog))

    for item in tables:
        name = item["name"]
        status = item.get("status")
        dominio = item.get("dominio")
        fonte = str(item.get("fonte_ans") or "").strip()
        doc_path = REPO / str(item.get("doc_path") or "")

        if status not in ALLOWED_STATUS:
            errors.append(f"{name}: status invalido {status!r}")
            continue
        if status == "fora_do_escopo" and dominio not in ALLOWED_OUT_OF_SCOPE:
            errors.append(f"{name}: fora_do_escopo so permitido para TISS/SIB")
        if dominio in ALLOWED_OUT_OF_SCOPE and status == "disponivel":
            errors.append(f"{name}: TISS/SIB nao podem ser marcados como disponivel")
        if dominio in SIB_DOMAINS and item.get("publicar_catalogo_comercial", True):
            errors.append(f"{name}: dependencia SIB deve ficar fora do catalogo comercial")
        if status != "fora_do_escopo" and not fonte:
            errors.append(f"{name}: fonte ANS nao declarada")
        if status in {"disponivel", "parcial"}:
            if not doc_contains_table(doc_path, name):
                errors.append(f"{name}: documentacao Markdown ausente ou incompleta")
        if status == "disponivel":
            model = dbt_by_name.get(name)
            if not model:
                errors.append(f"{name}: ausente em _consumo.yml")
            elif not has_minimum_test(model):
                errors.append(f"{name}: sem teste dbt minimo")
        if not skip_db and (status == "disponivel" or evidence_path):
            try:
                row_count = count_table(schema, name)
                counts[name] = row_count
            except Exception as exc:
                if status == "disponivel":
                    errors.append(f"{name}: falha ao contar linhas: {exc}")
                counts[name] = None
                continue
            if row_count <= 0:
                if status == "disponivel":
                    errors.append(f"{name}: tabela disponivel com {row_count} linhas")

    if evidence_path:
        write_evidence(evidence_path, schema, tables, counts, errors, skip_db)

    if errors:
        print("FALHA hard gate consumo_ans comercial")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SUCESSO hard gate consumo_ans comercial")
    return 0


def write_evidence(
    path: Path,
    schema: str,
    tables: list[dict[str, Any]],
    counts: dict[str, int | None],
    errors: list[str],
    skip_db: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_status = Counter(item.get("status") for item in tables)
    by_domain: dict[str, Counter] = defaultdict(Counter)
    for item in tables:
        by_domain[item.get("dominio", "desconhecido")][item.get("status")] += 1

    linhas = [
        "# Evidencia - hard gate consumo_ans comercial",
        "",
        f"- Validado em: {datetime.now(timezone.utc).isoformat()}",
        f"- Schema: `{schema}`",
        f"- Banco consultado: {'nao' if skip_db else 'sim'}",
        f"- Resultado: {'FALHA' if errors else 'SUCESSO'}",
        "",
        "## Resumo por status",
        "",
        "| status | tabelas |",
        "|---|---:|",
    ]
    for status, total in sorted(by_status.items()):
        linhas.append(f"| {status} | {total} |")

    linhas.extend(["", "## Status por dominio", "", "| dominio | status | tabelas |", "|---|---|---:|"])
    for dominio in sorted(by_domain):
        for status, total in sorted(by_domain[dominio].items()):
            linhas.append(f"| {dominio} | {status} | {total} |")

    linhas.extend(["", "## Tabelas", "", "| tabela | dominio | status | linhas |", "|---|---|---|---:|"])
    for item in tables:
        name = item["name"]
        count = counts.get(name)
        count_text = "n/a" if count is None else str(count)
        linhas.append(
            f"| `{schema}.{name}` | {item.get('dominio')} | {item.get('status')} | {count_text} |"
        )

    if errors:
        linhas.extend(["", "## Falhas", ""])
        linhas.extend(f"- {error}" for error in errors)

    linhas.extend([
        "",
        "## Conclusao comercial",
        "",
        (
            "Catalogo comercial bloqueado ate sanar as falhas acima."
            if errors
            else "Catalogo comercial apto para entrega honesta a clientes de BI/analytics."
        ),
        "",
    ])
    path.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sem-db",
        action="store_true",
        help="Valida catalogo/documentacao sem consultar contagens no Postgres.",
    )
    parser.add_argument(
        "--evidencia",
        type=Path,
        help="Caminho do Markdown de evidencia a gerar.",
    )
    args = parser.parse_args()
    return validate(args.sem_db, args.evidencia)


if __name__ == "__main__":
    sys.exit(main())
