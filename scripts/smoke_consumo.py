from __future__ import annotations

import asyncio

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal

FILTROS_TEMPORAIS = {
    "consumo_operadora_360": ("competencia", "202501"),
    "consumo_beneficiarios_operadora_mes": ("competencia", "202501"),
    "consumo_beneficiarios_municipio_mes": ("competencia", "202501"),
    "consumo_financeiro_operadora_trimestre": ("trimestre", "2025T1"),
    "consumo_regulatorio_operadora_trimestre": ("trimestre", "2025T1"),
    "consumo_rede_assistencial_municipio": ("competencia", "202501"),
    "consumo_oportunidade_municipio": ("competencia", "202501"),
    "consumo_score_operadora_mes": ("competencia", "202501"),
}

SCHEMAS_INTERNOS = ["bruto_ans", "stg_ans", "int_ans", "nucleo_ans", "plataforma"]


async def main() -> None:
    resultados: dict[str, int] = {}
    async with SessionLocal() as session:
        for modelo, (coluna, valor) in FILTROS_TEMPORAIS.items():
            total = await session.scalar(
                text(f"select count(*) from consumo_ans.{modelo} where {coluna} = :valor"),
                {"valor": valor},
            )
            resultados[modelo] = int(total or 0)
        score_invalido = await session.scalar(
            text(
                """
                select count(*)
                from consumo_ans.consumo_score_operadora_mes
                where score_total is not null
                  and (score_total < 0 or score_total > 100)
                """
            )
        )
        permissoes_internas = {}
        for schema in SCHEMAS_INTERNOS:
            permitido = await session.scalar(
                text(
                    "select has_schema_privilege('healthintel_cliente_reader', :schema, 'USAGE')"
                ),
                {"schema": schema},
            )
            permissoes_internas[schema] = bool(permitido)
    vazios = {modelo: total for modelo, total in resultados.items() if total <= 0}
    acessos_internos = [schema for schema, permitido in permissoes_internas.items() if permitido]
    if vazios or score_invalido or acessos_internos:
        raise SystemExit(
            {
                "vazios": vazios,
                "score_invalido": int(score_invalido or 0),
                "schemas_internos_com_acesso": acessos_internos,
            }
        )
    print({"status": "ok", "modelos": len(resultados)})


if __name__ == "__main__":
    asyncio.run(main())
