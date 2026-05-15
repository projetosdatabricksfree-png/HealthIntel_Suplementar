"""
Backfill Glosa mensal para meses anteriores.

Itera por competencia (YYYYMM) e baixa o arquivo de glosa de cada mes.
Runs idempotentes — competencias ja carregadas retornam ignorado_duplicata.

Requer ANS_ANOS_CARGA_HOT >= cobertura desejada. Para carregar 2023, use:
    ANS_ANOS_CARGA_HOT=4 python scripts/backfill_glosa_historico.py

Uso:
    ANS_ANOS_CARGA_HOT=4 python scripts/backfill_glosa_historico.py
    ANS_ANOS_CARGA_HOT=4 python scripts/backfill_glosa_historico.py --inicio 202301 --fim 202412
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date

sys.path.insert(0, "/workspace")


def _gerar_competencias(inicio: str, fim: str) -> list[str]:
    """Retorna lista de YYYYMM entre inicio e fim, inclusive."""
    competencias = []
    ano_i, mes_i = int(inicio[:4]), int(inicio[4:])
    ano_f, mes_f = int(fim[:4]), int(fim[4:])
    ano, mes = ano_i, mes_i
    while (ano, mes) <= (ano_f, mes_f):
        competencias.append(f"{ano}{mes:02d}")
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    return competencias


async def backfill(inicio: str, fim: str) -> None:
    from ingestao.app.ingestao_delta_ans import executar_ingestao_glosa_operadora

    competencias = _gerar_competencias(inicio, fim)
    print(f"Competencias a processar: {competencias[0]} → {competencias[-1]} ({len(competencias)} meses)")

    for competencia in competencias:
        print(f"\n{'='*60}")
        print(f"  Glosa competencia={competencia}")
        print(f"{'='*60}")
        try:
            resultado = await executar_ingestao_glosa_operadora(competencia)
            status = resultado.get("status", "?")
            arquivos = resultado.get("arquivos", 0)
            total = resultado.get("total_registros", 0)
            ignorados = resultado.get("total_ignorados", 0)
            print(f"  status={status}  arquivos={arquivos}  registros={total:,}  ignorados={ignorados:,}")
            if resultado.get("resultados"):
                for r in resultado["resultados"]:
                    nome = r.get("arquivo_origem", r.get("fonte", "?"))
                    st = r.get("status", "?")
                    n = r.get("total_registros", 0)
                    print(f"    {nome}: {st} ({n:,} linhas)")
        except Exception as exc:
            print(f"  ERRO em {competencia}: {exc}")


def main() -> None:
    hoje = date.today()
    # Default: 24 meses anteriores ao mes corrente
    ano_fim = hoje.year - 1
    fim_default = f"{ano_fim}12"
    inicio_default = f"{ano_fim - 1}01"

    parser = argparse.ArgumentParser(description="Backfill Glosa mensal")
    parser.add_argument("--inicio", default=inicio_default, help=f"Competencia inicial YYYYMM (default: {inicio_default})")
    parser.add_argument("--fim", default=fim_default, help=f"Competencia final YYYYMM (default: {fim_default})")
    args = parser.parse_args()

    print(f"Iniciando backfill Glosa: {args.inicio} → {args.fim}")
    asyncio.run(backfill(args.inicio, args.fim))
    print("\nBackfill Glosa concluido.")


if __name__ == "__main__":
    main()
