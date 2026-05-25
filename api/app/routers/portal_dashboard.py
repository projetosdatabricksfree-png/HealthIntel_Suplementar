"""Portal Dashboard: endpoints autenticados por JWT que refletem dados reais do tenant.

Aditivo a /v1/me/uso (que continua exigindo X-API-Key). O dashboard do portal
precisa funcionar mesmo sem chave em localStorage — usa a sessão do usuário.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.dependencia_sessao import obter_usuario_sessao
from api.app.routers.portal_api_keys import _tenant_ativo
from api.app.services.me_service import get_uso

router = APIRouter(prefix="/portal/dashboard", tags=["portal-dashboard"])


def _periodo_de_days(days: int | None, periodo: str) -> str:
    if days is None:
        return periodo
    if days <= 0:
        return "hoje"
    if days <= 7:
        return "7d"
    return "30d"


async def _plano_do_cliente(cliente_id: str) -> tuple[str, int]:
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select p.nome, p.limite_req_dia
                from plataforma.cliente c
                join plataforma.plano p on p.id = c.plano_id
                where c.id = :cid
                """
            ),
            {"cid": cliente_id},
        )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"codigo": "TENANT_NAO_ENCONTRADO", "mensagem": "Tenant não encontrado."},
        )
    return str(row["nome"]), int(row["limite_req_dia"] or 0)


@router.get("/uso")
async def dashboard_uso(
    request: Request,
    periodo: str = "hoje",
    days: int | None = None,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    plano_nome, limite_req_dia = await _plano_do_cliente(cliente_id)
    periodo_efetivo = _periodo_de_days(days, periodo)
    return await get_uso(
        cliente_id=cliente_id,
        periodo=periodo_efetivo,
        plano_nome=plano_nome,
        limite_req_dia=limite_req_dia,
    )
