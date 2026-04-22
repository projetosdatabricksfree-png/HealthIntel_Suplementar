from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from mongo_layout_service.app.core.config import get_settings
from mongo_layout_service.app.core.database import get_database, get_mongo_client
from mongo_layout_service.app.core.security import validar_service_token
from mongo_layout_service.app.middleware.hardening import aplicar_hardening_http
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.routers.layout import router as layout_router
from mongo_layout_service.app.services.health import obter_prontidao
from mongo_layout_service.app.services.layout_service import LayoutService

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    service = LayoutService(LayoutRepository(get_database()))
    await service.inicializar()
    yield
    get_mongo_client().close()


app = FastAPI(title=settings.app_nome, version=settings.app_versao, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.middleware("http")(aplicar_hardening_http)
app.include_router(layout_router)


@app.get("/saude")
async def saude() -> dict:
    return {
        "status": "ok",
        "servico": "layout-registry",
        "ambiente": settings.app_env,
        "mongo_db": settings.mongo_db,
    }


@app.get("/prontidao", dependencies=[Depends(validar_service_token)])
async def prontidao() -> JSONResponse:
    payload = await obter_prontidao()
    return JSONResponse(status_code=200, content=payload)
