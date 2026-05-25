from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.dependencia import validar_chave
from api.app.dependencia_sessao import obter_usuario_sessao
from api.app.middleware.rate_limit import aplicar_rate_limit
from api.app.services import auth_service
from api.app.services.auth_service import AuthError
from api.app.services.me_service import get_uso

router = APIRouter(prefix="/me", tags=["me"])


def _periodo_de_days(days: int | None, periodo: str) -> str:
    if days is None:
        return periodo
    if days <= 0:
        return "hoje"
    if days <= 7:
        return "7d"
    return "30d"


@router.get("/uso")
async def uso_cliente(
    request: Request,
    periodo: str = "7d",
    days: int | None = None,
    _: str = Depends(validar_chave),
) -> dict:
    await aplicar_rate_limit(request)
    cliente_id = request.state.cliente_id
    plano_nome = request.state.plano_nome
    limite_req_dia = getattr(request.state, "limite_req_dia", 0)
    periodo_efetivo = _periodo_de_days(days, periodo)
    return await get_uso(
        cliente_id=cliente_id,
        periodo=periodo_efetivo,
        plano_nome=plano_nome,
        limite_req_dia=limite_req_dia,
    )


class PerfilPatchInput(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)


async def _perfil_b2b(usuario_id: str) -> dict | None:
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select empresa, cnpj, telefone, cargo, segmento, objetivo_uso,
                       site_empresa, tamanho_empresa, mensagem,
                       aceite_termos_em, aceite_lgpd_em
                from plataforma.usuario_perfil_b2b
                where usuario_id = cast(:uid as uuid)
                """
            ),
            {"uid": usuario_id},
        )).mappings().first()
    if not row:
        return None
    return {
        "empresa": row["empresa"],
        "cnpj": row["cnpj"],
        "telefone": row["telefone"],
        "cargo": row["cargo"],
        "segmento": row["segmento"],
        "objetivo_uso": row["objetivo_uso"],
        "site_empresa": row["site_empresa"],
        "tamanho_empresa": row["tamanho_empresa"],
        "mensagem": row["mensagem"],
        "aceite_termos_em": row["aceite_termos_em"].isoformat() if row["aceite_termos_em"] else None,
        "aceite_lgpd_em": row["aceite_lgpd_em"].isoformat() if row["aceite_lgpd_em"] else None,
    }


@router.get("/perfil")
async def perfil(
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    try:
        dados = await auth_service.obter_perfil(usuario_id)
    except AuthError as e:
        raise HTTPException(status_code=e.status, detail={"codigo": e.codigo, "mensagem": e.mensagem})
    dados["perfil_b2b"] = await _perfil_b2b(usuario_id)
    return dados


@router.patch("/perfil")
async def atualizar_perfil(
    payload: PerfilPatchInput,
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    async with SessionLocal() as db:
        await db.execute(
            text("update plataforma.usuario set nome = :nome, atualizado_em = now() where id = :id"),
            {"nome": payload.nome.strip(), "id": usuario_id},
        )
        await db.commit()
    try:
        dados = await auth_service.obter_perfil(usuario_id)
    except AuthError as e:
        raise HTTPException(status_code=e.status, detail={"codigo": e.codigo, "mensagem": e.mensagem})
    dados["perfil_b2b"] = await _perfil_b2b(usuario_id)
    return dados
