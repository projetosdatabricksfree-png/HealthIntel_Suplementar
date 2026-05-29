from datetime import datetime, timezone

from fastapi import HTTPException, Request, status

from api.app.core.config import get_settings
from api.app.core.redis_client import redis_client

settings = get_settings()


async def aplicar_rate_limit(request: Request) -> None:
    identificador = getattr(
        request.state,
        "chave_api_id",
        getattr(request.state, "chave_api", "anonimo"),
    )
    limite_rpm = getattr(request.state, "limite_rpm", settings.app_rate_limit_rpm)
    limite_req_dia = getattr(request.state, "limite_req_dia", 0)
    limite_req_mes = getattr(request.state, "limite_req_mes", 0)
    modelo_cobranca = getattr(request.state, "modelo_cobranca", "flat")
    cliente_id = getattr(request.state, "cliente_id", None)

    # Enterprise pay-as-you-go: bypass cap diário/mensal (consumo é faturado posteriormente).
    bypass_pay_as_you_go = modelo_cobranca == "pay_as_you_go"

    if not bypass_pay_as_you_go and cliente_id:
        if limite_req_mes > 0:
            mes_ref = datetime.now(timezone.utc).strftime("%Y%m")
            mes_key = f"rate_limit_month:{cliente_id}:{mes_ref}"
            try:
                mes_total = await redis_client.incr(mes_key)
                if mes_total == 1:
                    # TTL ~35 dias (cobre qualquer mês de calendário com margem)
                    await redis_client.expire(mes_key, 3024000)
                if mes_total > limite_req_mes:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            "codigo": "LIMITE_MENSAL_EXCEDIDO",
                            "mensagem": (
                                f"Cota mensal de {limite_req_mes} requisições atingida. "
                                "Faça upgrade do plano para continuar."
                            ),
                        },
                        headers={"Retry-After": "86400"},
                    )
            except HTTPException:
                raise
            except Exception:
                pass

        if limite_req_dia > 0:
            hoje = datetime.now(timezone.utc).strftime("%Y%m%d")
            dia_key = f"rate_limit_day:{cliente_id}:{hoje}"
            try:
                dia_total = await redis_client.incr(dia_key)
                if dia_total == 1:
                    await redis_client.expire(dia_key, 172800)
                if dia_total > limite_req_dia:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            "codigo": "LIMITE_DIARIO_EXCEDIDO",
                            "mensagem": (
                                f"Limite diário de {limite_req_dia} requisições atingido. "
                                "Faça upgrade do plano para continuar."
                            ),
                        },
                        headers={"Retry-After": "86400"},
                    )
            except HTTPException:
                raise
            except Exception:
                pass

    rota = request.url.path
    if rota.startswith("/v1/bronze"):
        peso = 3
        camada = "bronze"
    elif rota.startswith("/v1/prata"):
        peso = 2
        camada = "prata"
    elif rota.startswith("/v1/premium"):
        peso = 2
        camada = "premium"
    else:
        peso = 1
        camada = "ouro"
    chave = f"rate_limit:{identificador}"
    try:
        total = await redis_client.incrby(chave, peso)
    except Exception as exc:
        if settings.rate_limit_falha_aberta:
            request.state.rate_limit_status = "indisponivel_fail_open"
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "RATE_LIMIT_INDISPONIVEL",
                "mensagem": "Protecao de rate limit indisponivel.",
            },
        ) from exc

    request.state.rate_limit_status = "ok"

    try:
        if total == peso:
            await redis_client.expire(chave, 60)
    except Exception as exc:
        if settings.rate_limit_falha_aberta:
            request.state.rate_limit_status = "expire_indisponivel_fail_open"
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "codigo": "RATE_LIMIT_INDISPONIVEL",
                "mensagem": "Protecao de rate limit indisponivel.",
            },
        ) from exc

    if total > limite_rpm:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"codigo": "LIMITE_EXCEDIDO", "mensagem": "Limite por minuto excedido."},
            headers={"Retry-After": "60"},
        )

    request.state.camada = camada
