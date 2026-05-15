"""
Backfill DIOPS financeiro para os 3 anos anteriores (2023-2025).

A funcao executar_ingestao_diops_operadora aceita o ano via competencia (YYYYMM)
e baixa TODOS os trimestres do ano de uma vez. Runs idempotentes — trimestres
ja carregados retornam status ignorado_duplicata.

Uso:
    python scripts/backfill_diops_historico.py
    python scripts/backfill_diops_historico.py --anos 2022 2023 2024 2025
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date

sys.path.insert(0, "/workspace")


async def backfill(anos: list[int]) -> None:
    from ingestao.app.ingestao_delta_ans import executar_ingestao_diops_operadora

    for ano in anos:
        competencia = f"{ano}01"
        print(f"\n{'='*60}")
        print(f"  DIOPS {ano} (competencia={competencia})")
        print(f"{'='*60}")
        try:
            resultado = await executar_ingestao_diops_operadora(competencia)
            status = resultado.get("status", "?")
            arquivos = resultado.get("arquivos", 0)
            total = resultado.get("total_registros", 0)
            print(f"  status={status}  arquivos={arquivos}  registros={total:,}")
            if resultado.get("resultados"):
                for r in resultado["resultados"]:
                    nome = r.get("arquivo_origem", r.get("fonte", "?"))
                    st = r.get("status", "?")
                    n = r.get("total_registros", 0)
                    print(f"    {nome}: {st} ({n:,} linhas)")
        except Exception as exc:
            print(f"  ERRO no ano {ano}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill DIOPS trimestral")
    hoje = date.today()
    anos_default = [hoje.year - 3, hoje.year - 2, hoje.year - 1]
    parser.add_argument(
        "--anos",
        nargs="+",
        type=int,
        default=anos_default,
        help=f"Anos a carregar (default: {anos_default})",
    )
    args = parser.parse_args()

    print(f"Iniciando backfill DIOPS para anos: {args.anos}")
    asyncio.run(backfill(args.anos))
    print("\nBackfill DIOPS concluido.")


if __name__ == "__main__":
    main()
