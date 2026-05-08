#!/usr/bin/env python3
"""Extrai objetos esperados do manifest.json do dbt para auditoria.

O script nao consulta banco e nao altera artefatos dbt. Ele transforma o
manifest resolvido por `dbt parse` em CSVs pequenos usados pela auditoria SQL.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_RESOURCE_TYPES = {"model", "seed", "snapshot"}


def _as_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() not in {"0", "false", "no", "off"}
    return bool(value)


def _count_disabled(disabled: Any) -> int:
    if isinstance(disabled, dict):
        total = 0
        for value in disabled.values():
            if isinstance(value, list):
                total += len(value)
            elif value:
                total += 1
        return total
    if isinstance(disabled, list):
        return len(disabled)
    return 0


def _normalizar_tags(node: dict[str, Any]) -> str:
    tags = node.get("tags")
    if tags is None:
        tags = (node.get("config") or {}).get("tags") or []
    return "|".join(str(tag) for tag in tags)


def _iter_nodes(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return list((manifest.get("nodes") or {}).values())


def extrair_objetos(
    manifest: dict[str, Any],
    expected_schemas: set[str],
    target_name: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    ignored_counts = {
        "ephemeral": 0,
        "disabled": _count_disabled(manifest.get("disabled")),
        "tests": 0,
        "sources": len(manifest.get("sources") or {}),
        "exposures": len(manifest.get("exposures") or {}),
        "macros": len(manifest.get("macros") or {}),
        "docs": len(manifest.get("docs") or {}),
    }

    expected_rows: list[dict[str, str]] = []
    expected_by_resource_type = {"model": 0, "seed": 0, "snapshot": 0}

    for node in _iter_nodes(manifest):
        resource_type = str(node.get("resource_type") or "")
        config = node.get("config") or {}
        materialized = str(config.get("materialized") or "")
        enabled = _as_bool(config.get("enabled", node.get("enabled")), default=True)

        if resource_type == "test":
            ignored_counts["tests"] += 1
            continue

        if not enabled:
            ignored_counts["disabled"] += 1
            continue

        if resource_type == "model" and materialized == "ephemeral":
            ignored_counts["ephemeral"] += 1
            continue

        if resource_type not in EXPECTED_RESOURCE_TYPES:
            continue

        schema_name = str(node.get("schema") or "")
        object_name = str(node.get("alias") or node.get("name") or "")
        database_name = str(node.get("database") or "")
        original_file_path = str(node.get("original_file_path") or "")
        unique_id = str(node.get("unique_id") or "")

        if not schema_name or not object_name:
            continue

        expected_rows.append(
            {
                "database_name": database_name,
                "schema_name": schema_name,
                "object_name": object_name,
                "resource_type": resource_type,
                "materialized": materialized,
                "original_file_path": original_file_path,
                "tags": _normalizar_tags(node),
                "enabled": "true",
                "target_name": target_name,
                "unique_id": unique_id,
                "schema_in_scope": "true" if schema_name in expected_schemas else "false",
            }
        )
        expected_by_resource_type[resource_type] += 1

    out_of_scope_rows = [
        row for row in expected_rows if row["schema_in_scope"] == "false"
    ]
    out_of_scope_schemas = sorted({row["schema_name"] for row in out_of_scope_rows})

    summary = {
        "considered_count": len(expected_rows),
        "expected_by_resource_type": expected_by_resource_type,
        "ignored_counts": ignored_counts,
        "expected_schemas": sorted(expected_schemas),
        "out_of_scope_schemas": out_of_scope_schemas,
        "out_of_scope_objects_count": len(out_of_scope_rows),
    }
    return expected_rows, summary


def escrever_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--expected-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--out-of-scope-out", required=True, type=Path)
    parser.add_argument("--schemas", required=True)
    parser.add_argument("--target-name", default="")
    args = parser.parse_args()

    with args.manifest.open(encoding="utf-8") as fp:
        manifest = json.load(fp)

    expected_schemas = {
        item.strip()
        for item in args.schemas.split(",")
        if item.strip()
    }
    expected_rows, summary = extrair_objetos(
        manifest=manifest,
        expected_schemas=expected_schemas,
        target_name=args.target_name,
    )

    expected_fieldnames = [
        "database_name",
        "schema_name",
        "object_name",
        "resource_type",
        "materialized",
        "original_file_path",
        "tags",
        "enabled",
        "target_name",
        "unique_id",
        "schema_in_scope",
    ]
    escrever_csv(args.expected_out, expected_rows, expected_fieldnames)

    out_of_scope_rows = [
        row for row in expected_rows if row["schema_in_scope"] == "false"
    ]
    escrever_csv(args.out_of_scope_out, out_of_scope_rows, expected_fieldnames)

    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_out.open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, ensure_ascii=False, indent=2, sort_keys=True)
        fp.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
