from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_diops_bruto,
    carregar_tiss_procedimento_bruto,
)

OPERADORAS = [
    ("123456", "MEDICINA_DE_GRUPO", "SP"),
    ("654321", "COOPERATIVA_MEDICA", "MG"),
    ("222333", "SEGURADORA_ESPECIALIZADA_EM_SAUDE", "RJ"),
    ("444555", "AUTOGESTAO", "DF"),
    ("777888", "FILANTROPICA", "PE"),
]

GRUPOS = [
    ("000101", "CONSULTAS", "CONSULTA AMBULATORIAL"),
    ("000202", "EXAMES", "EXAMES LABORATORIAIS"),
    ("000303", "TERAPIAS", "TERAPIA OCUPACIONAL"),
]

UFS = ["SP", "MG", "RJ"]


async def _limpar_demo() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                delete from bruto_ans.tiss_procedimento_trimestral
                where _arquivo_origem like 'tiss_demo_%'
                   or _hash_arquivo like 'demo_hash_tiss%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from bruto_ans.diops_operadora_trimestral
                where _arquivo_origem like 'tiss_demo_%'
                   or _hash_arquivo like 'demo_hash_diops_tiss%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset in ('tiss_procedimento', 'diops')
                  and status = 'demo_local_tiss'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.job
                where nome_job = 'seed_demo_tiss'
                """
            )
        )
        await session.commit()


def _gerar_tiss() -> list[dict[str, object]]:
    registros: list[dict[str, object]] = []
    for op_indice, (registro_ans, modalidade, _uf_sede) in enumerate(OPERADORAS, start=1):
        for uf_indice, sg_uf in enumerate(UFS, start=1):
            for grupo_indice, (grupo_codigo, grupo_desc, subgrupo) in enumerate(GRUPOS, start=1):
                multiplicador = op_indice + uf_indice + grupo_indice
                registros.append(
                    {
                        "trimestre": "2025T1",
                        "registro_ans": registro_ans,
                        "sg_uf": sg_uf,
                        "grupo_procedimento": grupo_codigo,
                        "grupo_desc": grupo_desc,
                        "subgrupo_procedimento": subgrupo,
                        "qt_procedimentos": 100 * multiplicador,
                        "qt_beneficiarios_distintos": 30 * multiplicador,
                        "valor_total": float(2500 * multiplicador),
                        "modalidade": modalidade,
                        "tipo_contratacao": "COLETIVO",
                        "fonte_publicacao": "tiss_demo_2025T1",
                    }
                )
    return registros


def _gerar_diops() -> list[dict[str, object]]:
    registros: list[dict[str, object]] = []
    for op_indice, (registro_ans, _, _) in enumerate(OPERADORAS, start=1):
        multiplicador = op_indice + 10
        registros.append(
            {
                "trimestre": "2025T1",
                "registro_ans": registro_ans,
                "cnpj": f"{op_indice:014d}",
                "ativo_total": float(1000000 + multiplicador * 1000),
                "passivo_total": float(800000 + multiplicador * 800),
                "patrimonio_liquido": float(200000 + multiplicador * 200),
                "receita_total": float(300000 + multiplicador * 1500),
                "despesa_total": float(220000 + multiplicador * 1000),
                "resultado_periodo": float(80000 + multiplicador * 500),
                "provisao_tecnica": float(120000 + multiplicador * 300),
                "margem_solvencia_calculada": float(1.5 + op_indice / 10),
                "fonte_publicacao": "tiss_demo_2025T1",
            }
        )
    return registros


async def main() -> None:
    await _limpar_demo()
    registros_tiss = _gerar_tiss()
    registros_diops = _gerar_diops()
    for indice, registro in enumerate(registros_tiss, start=1):
        await carregar_tiss_procedimento_bruto(
            [registro],
            arquivo_origem=f"tiss_demo_2025T1_{indice}.csv",
            layout_id="layout_tiss_procedimento_csv",
            layout_versao_id="layout_tiss_procedimento_csv:v1",
            hash_arquivo=f"demo_hash_tiss_{indice}",
            hash_estrutura="demo_hash_estrutura_tiss",
        )
    for indice, registro in enumerate(registros_diops, start=1):
        await carregar_diops_bruto(
            [registro],
            arquivo_origem=f"tiss_demo_2025T1_diops_{indice}.csv",
            layout_id="layout_diops_csv",
            layout_versao_id="layout_diops_csv:v1",
            hash_arquivo=f"demo_hash_diops_tiss_{indice}",
            hash_estrutura="demo_hash_estrutura_diops_tiss",
        )
    print(
        {
            "status": "ok",
            "tiss_registros": len(registros_tiss),
            "diops_registros": len(registros_diops),
            "trimestre": "2025T1",
            "gerado_em": datetime.now(tz=UTC).isoformat(),
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
