from __future__ import annotations

import asyncio

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal

FILTROS_TEMPORAIS = {
    "consumo_operadora_360": "competencia",
    "consumo_beneficiarios_operadora_mes": "competencia",
    "consumo_beneficiarios_municipio_mes": "competencia",
    "consumo_financeiro_operadora_trimestre": "trimestre",
    "consumo_regulatorio_operadora_trimestre": "trimestre",
    "consumo_rede_assistencial_municipio": "competencia",
    "consumo_oportunidade_municipio": "competencia",
    "consumo_score_operadora_mes": "competencia",
}

SCHEMAS_INTERNOS = ["bruto_ans", "stg_ans", "int_ans", "nucleo_ans", "plataforma"]


async def main() -> None:
    resultados: dict[str, int] = {}
    periodos: dict[str, str] = {}
    async with SessionLocal() as session:
        for modelo, coluna in FILTROS_TEMPORAIS.items():
            valor = await session.scalar(
                text(
                    f"""
                    select {coluna}::text
                    from consumo_ans.{modelo}
                    where {coluna} is not null
                    order by {coluna} desc
                    limit 1
                    """
                )
            )
            periodos[modelo] = str(valor or "")
            total = await session.scalar(
                text(
                    f"select count(*) from consumo_ans.{modelo} where {coluna}::text = :valor"
                ),
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
        permissoes_consumo = {
            modelo: bool(
                await session.scalar(
                    text(
                        "select has_table_privilege("
                        "'healthintel_cliente_reader', :tabela, 'SELECT')"
                    ),
                    {"tabela": f"consumo_ans.{modelo}"},
                )
            )
            for modelo in FILTROS_TEMPORAIS
        }
    vazios = {modelo: total for modelo, total in resultados.items() if total <= 0}
    acessos_internos = [schema for schema, permitido in permissoes_internas.items() if permitido]
    sem_select_consumo = [
        modelo for modelo, permitido in permissoes_consumo.items() if not permitido
    ]
    if vazios or score_invalido or acessos_internos or sem_select_consumo:
        raise SystemExit(
            {
                "vazios": vazios,
                "periodos": periodos,
                "score_invalido": int(score_invalido or 0),
                "schemas_internos_com_acesso": acessos_internos,
                "consumo_sem_select": sem_select_consumo,
            }
        )
    print({"status": "ok", "modelos": len(resultados), "periodos": periodos})


if __name__ == "__main__":
    asyncio.run(main())
