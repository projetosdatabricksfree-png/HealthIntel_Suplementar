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


async def _plano_do_cliente(cliente_id: str) -> dict:
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select
                    p.nome,
                    p.limite_req_dia,
                    p.limite_req_mes,
                    p.modelo_cobranca,
                    t.expira_em as trial_expira_em,
                    case
                        when t.cliente_id is not null
                             and t.consumido = false
                             and t.expira_em > now()
                        then true else false
                    end as trial_ativo
                from plataforma.cliente c
                join plataforma.plano p on p.id = c.plano_id
                left join plataforma.trial_pro t on t.cliente_id = c.id
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
    trial_expira = row.get("trial_expira_em")
    return {
        "nome": str(row["nome"]),
        "limite_req_dia": int(row["limite_req_dia"] or 0),
        "limite_req_mes": int(row["limite_req_mes"] or 0),
        "modelo_cobranca": str(row.get("modelo_cobranca") or "flat"),
        "trial_pro_ativo": bool(row.get("trial_ativo")),
        "trial_pro_expira_em": trial_expira.isoformat() if trial_expira else None,
    }


@router.get("/uso")
async def dashboard_uso(
    request: Request,
    periodo: str = "hoje",
    days: int | None = None,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    plano = await _plano_do_cliente(cliente_id)
    periodo_efetivo = _periodo_de_days(days, periodo)
    return await get_uso(
        cliente_id=cliente_id,
        periodo=periodo_efetivo,
        plano_nome=plano["nome"],
        limite_req_dia=plano["limite_req_dia"],
        limite_req_mes=plano["limite_req_mes"],
        modelo_cobranca=plano["modelo_cobranca"],
        trial_pro_ativo=plano["trial_pro_ativo"],
        trial_pro_expira_em=plano["trial_pro_expira_em"],
    )
