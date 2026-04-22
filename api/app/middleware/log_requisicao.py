import time

from fastapi import Request

from api.app.services.uso import registrar_log_uso


async def registrar_tempo_requisicao(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    latencia_ms = int((time.perf_counter() - inicio) * 1000)
    response.headers["X-Process-Time"] = f"{latencia_ms / 1000:.4f}"
    response.headers["X-Cache"] = getattr(request.state, "cache_status", "miss")
    if getattr(request.state, "chave_api_id", None):
        await registrar_log_uso(
            chave_id=request.state.chave_api_id,
            cliente_id=request.state.cliente_id,
            plano_id=request.state.plano_id,
            endpoint=request.url.path,
            rota=getattr(getattr(request.scope, "get", lambda *_: None)("route"), "path", None),
            metodo=request.method,
            codigo_status=response.status_code,
            latencia_ms=latencia_ms,
            cache_hit=getattr(request.state, "cache_status", "miss") == "hit",
            ip_cliente=request.client.host if request.client else None,
        )
    return response
