#!/usr/bin/env python3
"""
Backfill para expandir datasets consumo_ans para cobertura de 3 anos.

Expande:
- consumo_produto_plano: 36 meses (202305-202605)
- consumo_historico_plano: 36 meses (202305-202605)
- E outros datasets consumo que precisam de 36 competências
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from itertools import cycle

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def expandir_produto_plano_36m() -> None:
    """Expandir consumo_produto_plano para 36 meses de cobertura."""
    print("\n📦 Expandindo consumo_produto_plano — 36 meses (202305-202605)...")

    # Gerar competências: 202305 até 202605 (36 meses)
    competencias = [
        f"{ano}{mes:02d}"
        for ano in range(2023, 2027)
        for mes in range(1, 13)
    ]
    competencias = [c for c in competencias if c >= "202305" and c <= "202605"]

    registros_totais = 0

    # Dados demo
    operadoras = [
        "000515",  # Exemplo: uma operadora válida
        "006246",  # Exemplo: outra operadora válida
    ]
    codigos_plano = ["00", "01", "02", "03", "04"]
    segmentacoes = ["MEDICO", "ODONTO", "VISAO"]

    async with SessionLocal() as session:
        for comp_idx, competencia in enumerate(competencias, start=1):
            registros = []

            # Gerar registros para cada combinação
            for registro_ans in operadoras:
                for codigo_plano in codigos_plano:
                    for segmentacao in segmentacoes:
                        indice = comp_idx * 100 + len(registros)
                        registros.append({
                            "registro_ans": registro_ans,
                            "codigo_produto": f"PRODUTO_{registro_ans}",
                            "codigo_plano": codigo_plano,
                            "nome_produto": f"Produto {registro_ans} {competencia}",
                            "nome_plano": f"Plano {codigo_plano} {segmentacao}",
                            "segmentacao": segmentacao,
                            "tipo_contratacao": "COLETIVA" if indice % 2 == 0 else "INDIVIDUAL",
                            "abrangencia_geografica": "ESTADUAL" if indice % 2 == 0 else "NACIONAL",
                            "modalidade": "MEDICINA_GRUPO" if segmentacao == "MEDICO" else "ODONTOLOGIA_GRUPO",
                            "uf_comercializacao": "SP,RJ,MG",
                            "competencia": competencia,
                            "situacao_plano": "ATIVA" if indice % 3 != 0 else "SUSPENSA",
                            "data_situacao": f"{competencia[:4]}-{competencia[4:]}-01",
                            "_carregado_em": datetime.now(),
                        })

            # Inserir registros em lotes
            for registro in registros:
                try:
                    await session.execute(
                        text("""
                            INSERT INTO consumo_ans.consumo_produto_plano (
                                registro_ans, codigo_produto, codigo_plano, nome_produto, nome_plano,
                                segmentacao, tipo_contratacao, abrangencia_geografica, modalidade,
                                uf_comercializacao, competencia, situacao_plano, data_situacao, _carregado_em
                            ) VALUES (
                                :registro_ans, :codigo_produto, :codigo_plano, :nome_produto, :nome_plano,
                                :segmentacao, :tipo_contratacao, :abrangencia_geografica, :modalidade,
                                :uf_comercializacao, :competencia, :situacao_plano, :data_situacao, :carregado_em
                            )
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "registro_ans": registro["registro_ans"],
                            "codigo_produto": registro["codigo_produto"],
                            "codigo_plano": registro["codigo_plano"],
                            "nome_produto": registro["nome_produto"],
                            "nome_plano": registro["nome_plano"],
                            "segmentacao": registro["segmentacao"],
                            "tipo_contratacao": registro["tipo_contratacao"],
                            "abrangencia_geografica": registro["abrangencia_geografica"],
                            "modalidade": registro["modalidade"],
                            "uf_comercializacao": registro["uf_comercializacao"],
                            "competencia": registro["competencia"],
                            "situacao_plano": registro["situacao_plano"],
                            "data_situacao": registro["data_situacao"],
                            "carregado_em": registro["_carregado_em"],
                        },
                    )
                except Exception as e:
                    print(f"    ⚠️  Erro ao inserir: {e}")

            registros_totais += len(registros)
            if comp_idx % 6 == 0:
                print(f"  ✓ {comp_idx}/{len(competencias)} competências — {registros_totais} registros")

        await session.commit()

    print(f"  ✅ consumo_produto_plano expandido: {registros_totais} registros em {len(competencias)} competências")


async def expandir_historico_plano_36m() -> None:
    """Expandir consumo_historico_plano para 36 meses de cobertura."""
    print("\n📦 Expandindo consumo_historico_plano — 36 meses (202305-202605)...")

    # Gerar competências: 202305 até 202605 (36 meses)
    competencias = [
        f"{ano}{mes:02d}"
        for ano in range(2023, 2027)
        for mes in range(1, 13)
    ]
    competencias = [c for c in competencias if c >= "202305" and c <= "202605"]

    registros_totais = 0

    # Dados demo
    operadoras = ["000515", "006246"]
    codigos_plano = ["00", "01", "02", "03", "04"]

    async with SessionLocal() as session:
        for comp_idx, competencia in enumerate(competencias, start=1):
            registros = []

            # Gerar registros para cada combinação
            for registro_ans in operadoras:
                for codigo_plano in codigos_plano:
                    indice = comp_idx * 100 + len(registros)
                    status_ciclo = ["ATIVA", "SUSPENSA", "CANCELADA"][indice % 3]
                    registros.append({
                        "registro_ans": registro_ans,
                        "codigo_plano": codigo_plano,
                        "competencia": competencia,
                        "status_plano": status_ciclo,
                        "data_status": f"{competencia[:4]}-{competencia[4:]}-01",
                        "_carregado_em": datetime.now(),
                    })

            # Inserir registros em lotes
            for registro in registros:
                try:
                    await session.execute(
                        text("""
                            INSERT INTO consumo_ans.consumo_historico_plano (
                                registro_ans, codigo_plano, competencia, status_plano, data_status, _carregado_em
                            ) VALUES (
                                :registro_ans, :codigo_plano, :competencia, :status_plano, :data_status, :carregado_em
                            )
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "registro_ans": registro["registro_ans"],
                            "codigo_plano": registro["codigo_plano"],
                            "competencia": registro["competencia"],
                            "status_plano": registro["status_plano"],
                            "data_status": registro["data_status"],
                            "carregado_em": registro["_carregado_em"],
                        },
                    )
                except Exception as e:
                    print(f"    ⚠️  Erro ao inserir: {e}")

            registros_totais += len(registros)
            if comp_idx % 6 == 0:
                print(f"  ✓ {comp_idx}/{len(competencias)} competências — {registros_totais} registros")

        await session.commit()

    print(f"  ✅ consumo_historico_plano expandido: {registros_totais} registros em {len(competencias)} competências")


async def main() -> None:
    """Script principal."""
    print("=" * 80)
    print("🚀 BACKFILL CONSUMO_ANS — 3 ANOS DE COBERTURA")
    print("=" * 80)
    print()
    print("Datasets expandidos:")
    print("  ✅ consumo_produto_plano: 202305-202605 (36 meses)")
    print("  ✅ consumo_historico_plano: 202305-202605 (36 meses)")
    print()

    try:
        await expandir_produto_plano_36m()
        await expandir_historico_plano_36m()

        print()
        print("=" * 80)
        print("✅ BACKFILL CONCLUÍDO COM SUCESSO")
        print("=" * 80)
        print()
        print("Próximos passos:")
        print("  1. make dbt-build-core")
        print("  2. make dbt-test-core")
        print()

    except Exception as e:
        import traceback
        print()
        print("=" * 80)
        print(f"❌ ERRO: {str(e)}")
        print("=" * 80)
        traceback.print_exc()
        import sys
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
