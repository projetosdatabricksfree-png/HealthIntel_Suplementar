from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from api.app.core.config import get_settings
from api.app.core.errors import normalizar_http_exception
from api.app.middleware.hardening import aplicar_hardening_http
from api.app.middleware.log_requisicao import registrar_tempo_requisicao
from api.app.routers import (
    admin_billing,
    admin_layout,
    bronze,
    cnes,
    financeiro,
    mercado,
    meta,
    operadora,
    prata,
    ranking,
    rede,
    regulatorio,
    regulatorio_v2,
    tiss,
)
from api.app.services.health import obter_prontidao

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title=settings.app_nome, version=settings.app_versao, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.middleware("http")(aplicar_hardening_http)
app.middleware("http")(registrar_tempo_requisicao)
app.include_router(meta.router, prefix=settings.app_prefixo)
app.include_router(operadora.router, prefix=settings.app_prefixo)
app.include_router(mercado.router, prefix=settings.app_prefixo)
app.include_router(rede.router, prefix=settings.app_prefixo)
app.include_router(ranking.router, prefix=settings.app_prefixo)
app.include_router(regulatorio.router, prefix=settings.app_prefixo)
app.include_router(regulatorio_v2.router, prefix=settings.app_prefixo)
app.include_router(financeiro.router, prefix=settings.app_prefixo)
app.include_router(bronze.router, prefix=settings.app_prefixo)
app.include_router(prata.router, prefix=settings.app_prefixo)
app.include_router(cnes.router, prefix=settings.app_prefixo)
app.include_router(tiss.router, prefix=settings.app_prefixo)
app.include_router(admin_billing.router)
app.include_router(admin_layout.router)


@app.exception_handler(HTTPException)
async def tratar_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    return normalizar_http_exception(exc)


@app.get("/saude")
async def saude() -> dict:
    return {
        "status": "ok",
        "ambiente": settings.app_env,
        "versao": settings.app_versao,
        "dependencias": {
            "postgres": settings.postgres_host,
            "redis": settings.redis_host,
            "mongo": settings.mongo_host,
        },
    }


@app.get("/prontidao")
async def prontidao() -> JSONResponse:
    payload = await obter_prontidao()
    status_code = 200 if payload["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload)
