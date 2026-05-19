from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text

from api.app.core.database import SessionLocal

_PERIODOS = {
    "hoje": 0,
    "7d": 7,
    "30d": 30,
    "mes_atual": -1,
}


def _intervalo(periodo: str) -> tuple[date, date]:
    """Returns (inicio, fim) as datetime.date objects."""
    hoje = date.today()
    if periodo == "hoje":
        return hoje, hoje
    if periodo == "mes_atual":
        return hoje.replace(day=1), hoje
    dias = _PERIODOS.get(periodo, 7)
    return hoje - timedelta(days=dias), hoje


async def get_uso(chave_id: str, periodo: str, plano_nome: str) -> dict:
    inicio, fim = _intervalo(periodo)
    fim_exclusivo = fim + timedelta(days=1)

    async with SessionLocal() as session:
        result_serie = await session.execute(
            text(
                """
                select
                    date_trunc('day', timestamp_req at time zone 'America/Sao_Paulo')::date as dia,
                    count(*) as requisicoes,
                    count(*) filter (where codigo_status >= 400) as erros,
                    round(avg(latencia_ms)) as latencia_ms
                from plataforma.log_uso
                where chave_id = :chave_id
                  and timestamp_req >= :inicio
                  and timestamp_req < :fim_exclusivo
                group by 1
                order by 1
                """
            ),
            {"chave_id": chave_id, "inicio": inicio, "fim_exclusivo": fim_exclusivo},
        )
        serie = [
            {
                "dia": str(row["dia"]),
                "requisicoes": int(row["requisicoes"]),
                "erros": int(row["erros"]),
                "latencia_ms": int(row["latencia_ms"] or 0),
            }
            for row in result_serie.mappings()
        ]

        result_endpoints = await session.execute(
            text(
                """
                select
                    endpoint,
                    count(*) as requisicoes,
                    count(*) filter (where codigo_status >= 400) as erros
                from plataforma.log_uso
                where chave_id = :chave_id
                  and timestamp_req >= :inicio
                  and timestamp_req < :fim_exclusivo
                group by endpoint
                order by requisicoes desc
                limit 20
                """
            ),
            {"chave_id": chave_id, "inicio": inicio, "fim_exclusivo": fim_exclusivo},
        )
        por_endpoint = [
            {
                "endpoint": str(row["endpoint"]),
                "requisicoes": int(row["requisicoes"]),
                "erros": int(row["erros"]),
            }
            for row in result_endpoints.mappings()
        ]

    total_requisicoes = sum(d["requisicoes"] for d in serie)
    total_erros = sum(d["erros"] for d in serie)
    latencia_media = (
        round(sum(d["latencia_ms"] for d in serie) / len(serie)) if serie else 0
    )

    return {
        "dados": {
            "periodo": periodo,
            "total_requisicoes": total_requisicoes,
            "total_erros": total_erros,
            "latencia_media_ms": latencia_media,
            "serie_diaria": serie,
            "por_endpoint": por_endpoint,
        },
        "meta": {
            "periodo": periodo,
            "inicio": str(inicio),
            "fim": str(fim),
            "plano": plano_nome,
        },
    }
