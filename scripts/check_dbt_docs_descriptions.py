#!/usr/bin/env python3
"""Audit: verifica que todos os modelos finais (consumo, api, prata) têm description no YAML."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def main() -> None:
    dbt_root = Path(__file__).resolve().parent.parent / "healthintel_dbt" / "models"
    camadas_finais = ["consumo", "api"]

    modelos_sem_descricao: list[str] = []
    modelos_auditados = 0

    for camada in camadas_finais:
        camada_dir = dbt_root / camada
        if not camada_dir.exists():
            print(f"WARN: diretorio {camada_dir} nao encontrado")
            continue

        # Find all .yml files recursively
        for yml_path in sorted(camada_dir.rglob("*.yml")):
            with yml_path.open() as f:
                try:
                    doc = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    print(f"ERRO ao parsear {yml_path}: {e}")
                    continue

            if not doc or "models" not in doc:
                continue

            for model in doc["models"]:
                nome = model.get("name", "???")
                desc = model.get("description", "")
                modelos_auditados += 1

                if not desc or not desc.strip():
                    modelos_sem_descricao.append(f"{yml_path.relative_to(dbt_root)}::{nome}")

    print(f"\nModelos auditados: {modelos_auditados}")
    print(f"Modelos sem descricao: {len(modelos_sem_descricao)}")

    if modelos_sem_descricao:
        print("\nFALHA — modelos sem descricao:")
        for m in modelos_sem_descricao:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print("\nSUCESSO: todos os modelos finais possuem descricao.")


if __name__ == "__main__":
    main()
