from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client

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


async def _quota_diaria_redis(cliente_id: str) -> int:
    hoje_str = datetime.now(UTC).strftime("%Y%m%d")
    chave_redis = f"rate_limit_day:{cliente_id}:{hoje_str}"
    try:
        valor = await redis_client.get(chave_redis)
        return int(valor) if valor is not None else 0
    except Exception:
        return 0


async def get_uso(
    cliente_id: str,
    periodo: str,
    plano_nome: str,
    limite_req_dia: int = 0,
) -> dict:
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
                where cliente_id = :cliente_id
                  and timestamp_req >= :inicio
                  and timestamp_req < :fim_exclusivo
                group by 1
                order by 1
                """
            ),
            {"cliente_id": cliente_id, "inicio": inicio, "fim_exclusivo": fim_exclusivo},
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
                where cliente_id = :cliente_id
                  and timestamp_req >= :inicio
                  and timestamp_req < :fim_exclusivo
                group by endpoint
                order by requisicoes desc
                limit 20
                """
            ),
            {"cliente_id": cliente_id, "inicio": inicio, "fim_exclusivo": fim_exclusivo},
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
    success_rate = (
        round(((total_requisicoes - total_erros) / total_requisicoes) * 1000) / 10
        if total_requisicoes > 0
        else 100.0
    )
    quota_used_today = await _quota_diaria_redis(cliente_id)

    return {
        "dados": {
            "periodo": periodo,
            "total_requisicoes": total_requisicoes,
            "total_erros": total_erros,
            "latencia_media_ms": latencia_media,
            "success_rate": success_rate,
            "serie_diaria": serie,
            "por_endpoint": por_endpoint,
        },
        "meta": {
            "periodo": periodo,
            "inicio": str(inicio),
            "fim": str(fim),
            "plano": plano_nome,
            "quota_daily": int(limite_req_dia),
            "quota_used_today": quota_used_today,
        },
    }
