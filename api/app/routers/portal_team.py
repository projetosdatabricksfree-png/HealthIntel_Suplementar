"""Portal: gestão de equipe — listar membros, convidar, aceitar, remover, mudar role."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field, field_validator

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.security import gerar_hash_sha256, gerar_token_aleatorio
from api.app.dependencia_sessao import obter_usuario_sessao, verificar_role
from api.app.services import email_service
from sqlalchemy import text

router = APIRouter(prefix="/portal/team", tags=["portal-team"])

_ROLES_ADMIN = verificar_role("owner", "admin")

_ROLES_VALIDOS = {"owner", "admin", "developer", "billing", "viewer"}


def _tenant(request: Request) -> str:
    tid = getattr(request.state, "tenant_ativo_id", None)
    if not tid:
        raise HTTPException(status_code=403, detail={"codigo": "SEM_TENANT", "mensagem": "Nenhum tenant ativo na sessão."})
    return str(tid)


class ConviteInput(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    role: str = Field(default="viewer")

    @field_validator("role")
    @classmethod
    def _validar_role(cls, v: str) -> str:
        if v not in _ROLES_VALIDOS:
            raise ValueError(f"role deve ser um de: {', '.join(sorted(_ROLES_VALIDOS))}")
        return v


class AlterarRoleInput(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def _validar_role(cls, v: str) -> str:
        if v not in _ROLES_VALIDOS:
            raise ValueError(f"role deve ser um de: {', '.join(sorted(_ROLES_VALIDOS))}")
        return v


@router.get("")
async def listar_membros(
    request: Request,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = _tenant(request)
    async with SessionLocal() as db:
        rows = (await db.execute(
            text("""
                select cu.id, cu.role, cu.status, cu.aceito_em, cu.criado_em,
                       u.email, u.nome, u.avatar_url, u.ultimo_login_em
                from plataforma.cliente_usuario cu
                join plataforma.usuario u on u.id = cu.usuario_id
                where cu.cliente_id = :cid
                  and cu.status in ('ativo', 'pendente_convite')
                order by cu.criado_em
            """),
            {"cid": cliente_id},
        )).mappings().all()
    return {
        "dados": [
            {
                "id": str(r["id"]),
                "email": r["email"],
                "nome": r["nome"],
                "avatar_url": r["avatar_url"],
                "role": r["role"],
                "status": r["status"],
                "aceito_em": r["aceito_em"].isoformat() if r["aceito_em"] else None,
                "ultimo_login_em": r["ultimo_login_em"].isoformat() if r["ultimo_login_em"] else None,
            }
            for r in rows
        ]
    }


@router.post("/convite", status_code=status.HTTP_201_CREATED)
async def convidar_membro(
    payload: ConviteInput,
    request: Request,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = _tenant(request)
    settings = get_settings()

    async with SessionLocal() as db:
        cliente_row = (await db.execute(
            text("select nome from plataforma.cliente where id = :cid"),
            {"cid": cliente_id},
        )).mappings().first()

        usuario_row = (await db.execute(
            text("select id, nome from plataforma.usuario where email = :email"),
            {"email": payload.email},
        )).mappings().first()

        if usuario_row:
            vinculo = (await db.execute(
                text("select id from plataforma.cliente_usuario where cliente_id = :cid and usuario_id = :uid"),
                {"cid": cliente_id, "uid": usuario_row["id"]},
            )).first()
            if vinculo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"codigo": "MEMBRO_JA_EXISTE", "mensagem": "Este usuário já é membro da organização."},
                )
            target_uid = str(usuario_row["id"])
            target_nome = usuario_row["nome"]
        else:
            criado = (await db.execute(
                text("""
                    insert into plataforma.usuario (email, nome, status)
                    values (:email, :nome, 'pendente_email')
                    returning id
                """),
                {"email": payload.email, "nome": payload.email.split("@")[0]},
            )).scalar_one()
            target_uid = str(criado)
            target_nome = payload.email.split("@")[0]

        await db.execute(
            text("""
                insert into plataforma.cliente_usuario (cliente_id, usuario_id, role, status, convidado_por_id)
                values (:cid, :uid, :role, 'pendente_convite', :convidante)
            """),
            {"cid": cliente_id, "uid": target_uid, "role": payload.role, "convidante": usuario_id},
        )

        token_plain, token_hash = gerar_token_aleatorio()
        expira = datetime.now(UTC) + timedelta(days=7)
        await db.execute(
            text("""
                insert into plataforma.token_verificacao (usuario_id, tipo, hash_token, expira_em)
                values (:uid, 'convite_equipe', :hash, :exp)
            """),
            {"uid": target_uid, "hash": token_hash, "exp": expira},
        )
        await db.commit()

    base_url = "https://www.healthintel.com.br"
    link = f"{base_url}/aceitar-convite?token={token_plain}"
    org_nome = cliente_row["nome"] if cliente_row else "HealthIntel"
    html_corpo = (
        f"<p>Olá, {target_nome}!</p>"
        f"<p>Você foi convidado para integrar <strong>{org_nome}</strong> na plataforma HealthIntel com o papel <strong>{payload.role}</strong>.</p>"
        f'<p><a href="{link}" style="background:#6366f1;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none">Aceitar convite</a></p>'
        f"<p>Link expira em 7 dias.</p>"
    )
    texto_corpo = f"Convite para {org_nome} com papel {payload.role}. Acesse: {link}"
    try:
        email_status = await email_service.enviar_email_async(
            subject=f"Convite para a organização {org_nome} — HealthIntel",
            body_text=texto_corpo,
            body_html=html_corpo,
            to_email=payload.email,
        )
    except Exception:
        email_status = "falha"

    return {"dados": {"email": payload.email, "role": payload.role, "email_status": email_status}}


class AceitarConviteInput(BaseModel):
    token: str


@router.post("/convite/aceitar")
async def aceitar_convite(payload: AceitarConviteInput) -> dict:
    token_hash = gerar_hash_sha256(payload.token)
    async with SessionLocal() as db:
        tok = (await db.execute(
            text("""
                select tv.id, tv.usuario_id, tv.expira_em, tv.consumido_em
                from plataforma.token_verificacao tv
                where tv.hash_token = :hash and tv.tipo = 'convite_equipe'
            """),
            {"hash": token_hash},
        )).mappings().first()

        if not tok:
            raise HTTPException(status_code=404, detail={"codigo": "TOKEN_INVALIDO", "mensagem": "Token inválido."})
        if tok["consumido_em"]:
            raise HTTPException(status_code=400, detail={"codigo": "TOKEN_CONSUMIDO", "mensagem": "Token já utilizado."})
        if tok["expira_em"].replace(tzinfo=UTC) < datetime.now(UTC):
            raise HTTPException(status_code=400, detail={"codigo": "TOKEN_EXPIRADO", "mensagem": "Token expirado."})

        await db.execute(
            text("update plataforma.token_verificacao set consumido_em = now() where id = :id"),
            {"id": tok["id"]},
        )
        await db.execute(
            text("""
                update plataforma.cliente_usuario
                set status = 'ativo', aceito_em = now()
                where usuario_id = :uid and status = 'pendente_convite'
            """),
            {"uid": tok["usuario_id"]},
        )
        await db.execute(
            text("update plataforma.usuario set email_verificado_em = now(), status = 'ativo' where id = :id and status = 'pendente_email'"),
            {"id": tok["usuario_id"]},
        )
        await db.commit()

    return {"dados": {"status": "aceito"}}


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
async def remover_membro(
    usuario_id_alvo: str = Path(..., alias="usuario_id"),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = _tenant(request)
    if usuario_id_alvo == usuario_id:
        raise HTTPException(status_code=400, detail={"codigo": "AUTO_REMOCAO", "mensagem": "Você não pode se remover da organização."})

    async with SessionLocal() as db:
        resultado = await db.execute(
            text("""
                update plataforma.cliente_usuario
                set status = 'suspenso'
                where cliente_id = :cid and usuario_id = :uid and role != 'owner'
                returning id
            """),
            {"cid": cliente_id, "uid": usuario_id_alvo},
        )
        if not resultado.first():
            raise HTTPException(status_code=404, detail={"codigo": "MEMBRO_NAO_ENCONTRADO", "mensagem": "Membro não encontrado ou é owner (não pode ser removido)."})
        await db.commit()

    return {"dados": {"status": "removido"}}


@router.patch("/{usuario_id}")
async def alterar_role(
    payload: AlterarRoleInput,
    usuario_id_alvo: str = Path(..., alias="usuario_id"),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = _tenant(request)
    if payload.role == "owner":
        role_req = getattr(request.state, "role", "")
        if role_req != "owner":
            raise HTTPException(status_code=403, detail={"codigo": "SEM_PERMISSAO", "mensagem": "Somente owner pode promover outro usuário a owner."})

    async with SessionLocal() as db:
        resultado = await db.execute(
            text("""
                update plataforma.cliente_usuario
                set role = :role
                where cliente_id = :cid and usuario_id = :uid and status = 'ativo'
                returning id
            """),
            {"cid": cliente_id, "uid": usuario_id_alvo, "role": payload.role},
        )
        if not resultado.first():
            raise HTTPException(status_code=404, detail={"codigo": "MEMBRO_NAO_ENCONTRADO", "mensagem": "Membro ativo não encontrado."})
        await db.commit()

    return {"dados": {"status": "atualizado", "role": payload.role}}
