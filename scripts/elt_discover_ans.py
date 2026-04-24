from __future__ import annotations

import argparse
import asyncio
import json

from ingestao.app.elt.orchestrator import executar_elt_discovery


def main() -> None:
    parser = argparse.ArgumentParser(description="Descobre fontes públicas ANS em /FTP/PDA/.")
    parser.add_argument("--escopo", choices=["sector_core", "all_ftp"], default="sector_core")
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args()
    resultado = asyncio.run(executar_elt_discovery(escopo=args.escopo, max_depth=args.max_depth))
    print(json.dumps(resultado, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
