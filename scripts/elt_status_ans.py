from __future__ import annotations

import asyncio
import json

from ingestao.app.elt.manifest import resumo_elt_ans


def main() -> None:
    resultado = asyncio.run(resumo_elt_ans())
    print(json.dumps(resultado, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
