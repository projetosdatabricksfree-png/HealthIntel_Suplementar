from __future__ import annotations

import argparse
import asyncio
import json

from ingestao.app.elt.orchestrator import executar_elt_all


def _familias(valor: str) -> list[str] | None:
    familias = [item.strip() for item in valor.split(",") if item.strip()]
    return familias or None


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa discovery, extract e load da ELT ANS.")
    parser.add_argument("--escopo", choices=["sector_core", "all_ftp"], default="sector_core")
    parser.add_argument("--familias", default="")
    parser.add_argument("--limite", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args()
    resultado = asyncio.run(
        executar_elt_all(
            escopo=args.escopo,
            familias=_familias(args.familias),
            limite=args.limite,
            max_depth=args.max_depth,
        )
    )
    print(json.dumps(resultado, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
