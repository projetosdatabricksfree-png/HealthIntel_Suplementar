"""Portal: gestão de API keys por sessão de usuário (não X-API-Key)."""

from __future__ import annotations

import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field

from api.app.core.database import SessionLocal
from api.app.core.redis_client import get_redis
from api.app.core.security import gerar_hash_sha256
from api.app.dependencia_sessao import obter_usuario_sessao, verificar_role
from sqlalchemy import text

router = APIRouter(prefix="/portal/api-keys", tags=["portal-api-keys"])

_ROLES_VIEWER = verificar_role("owner", "admin", "developer", "billing", "viewer")
_ROLES_DEVELOPER = verificar_role("owner", "admin", "developer")
_ROLES_ADMIN = verificar_role("owner", "admin")


class CriarChaveInput(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    ambiente: str = Field(default="producao")

    def model_post_init(self, _: Any) -> None:
        if self.ambiente not in ("sandbox", "producao"):
            raise ValueError("ambiente deve ser 'sandbox' ou 'producao'")


def _gerar_chave_plain(ambiente: str) -> str:
    corpo = secrets.token_urlsafe(40).replace("-", "x").replace("_", "y")
    prefixo = "hi_test_" if ambiente == "sandbox" else "hi_live_"
    return f"{prefixo}{corpo}"[:48]


async def _tenant_ativo(request: Request) -> str:
    tid = getattr(request.state, "tenant_ativo_id", None)
    if not tid:
        raise HTTPException(status_code=403, detail={"codigo": "SEM_TENANT", "mensagem": "Nenhum tenant ativo na sessão."})
    return str(tid)


async def _plano_do_tenant(db: Any, cliente_id: str) -> dict:
    row = (await db.execute(
        text("""
            select p.id, p.nome, p.limite_api_keys
            from plataforma.cliente c
            join plataforma.plano p on p.id = c.plano_id
            where c.id = :cid
        """),
        {"cid": cliente_id},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail={"codigo": "TENANT_NAO_ENCONTRADO", "mensagem": "Tenant não encontrado."})
    return dict(row)


@router.get("")
async def listar_chaves(
    request: Request,
    usuario_id: str = Depends(_ROLES_VIEWER),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        rows = (await db.execute(
            text("""
                select id, nome, prefixo_chave, ambiente, escopos, status,
                       criado_em, ultimo_uso_em, revogada_em, expira_em
                from plataforma.chave_api
                where cliente_id = :cid and revogada_em is null
                order by criado_em desc
            """),
            {"cid": cliente_id},
        )).mappings().all()
    return {
        "dados": [
            {
                "id": str(r["id"]),
                "nome": r["nome"],
                "prefixo": r["prefixo_chave"],
                "ambiente": r["ambiente"],
                "escopos": list(r["escopos"] or []),
                "status": r["status"],
                "criado_em": r["criado_em"].isoformat() if r["criado_em"] else None,
                "ultimo_uso_em": r["ultimo_uso_em"].isoformat() if r["ultimo_uso_em"] else None,
                "revogada_em": r["revogada_em"].isoformat() if r["revogada_em"] else None,
                "expira_em": r["expira_em"].isoformat() if r["expira_em"] else None,
            }
            for r in rows
        ]
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def criar_chave(
    payload: CriarChaveInput,
    request: Request,
    usuario_id: str = Depends(_ROLES_DEVELOPER),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        plano = await _plano_do_tenant(db, cliente_id)
        limite = plano["limite_api_keys"]

        if limite != -1:
            contagem = (await db.execute(
                text("select count(*) from plataforma.chave_api where cliente_id = :cid and status = 'ativo'"),
                {"cid": cliente_id},
            )).scalar_one()
            if contagem >= limite:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={"codigo": "LIMITE_API_KEYS", "mensagem": f"Plano {plano['nome']} permite {limite} chave(s) ativa(s)."},
                )

        chave_plain = _gerar_chave_plain(payload.ambiente)
        hash_chave = gerar_hash_sha256(chave_plain)
        prefixo = chave_plain[:10]

        row = (await db.execute(
            text("""
                insert into plataforma.chave_api
                    (cliente_id, plano_id, hash_chave, prefixo_chave, status, nome, ambiente, escopos, criada_por_usuario_id)
                values
                    (:cid, :pid, :hash, :prefixo, 'ativo', :nome, :amb, array[]::text[], :uid)
                returning id, criado_em
            """),
            {
                "cid": cliente_id,
                "pid": plano["id"],
                "hash": hash_chave,
                "prefixo": prefixo,
                "nome": payload.nome,
                "amb": payload.ambiente,
                "uid": usuario_id,
            },
        )).mappings().first()
        await db.commit()

    return {
        "dados": {
            "id": str(row["id"]),
            "chave_plain": chave_plain,
            "prefixo": prefixo,
            "nome": payload.nome,
            "ambiente": payload.ambiente,
            "criado_em": row["criado_em"].isoformat(),
        }
    }


async def _revogar_chave_db(db: Any, chave_id: str, cliente_id: str, usuario_id: str) -> dict:
    row = (await db.execute(
        text("""
            update plataforma.chave_api
            set status = 'revogado', revogada_em = now(), revogada_por_usuario_id = :uid
            where id = :id and cliente_id = :cid and revogada_em is null
            returning id, hash_chave
        """),
        {"id": chave_id, "cid": cliente_id, "uid": usuario_id},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail={"codigo": "CHAVE_NAO_ENCONTRADA", "mensagem": "Chave não encontrada ou já excluída."})
    return dict(row)


@router.post("/{chave_id}/revogar")
async def revogar_chave(
    chave_id: str = Path(...),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        row = await _revogar_chave_db(db, chave_id, cliente_id, usuario_id)
        await db.commit()

    redis = await get_redis()
    if redis:
        await redis.delete(f"api_key:{row['hash_chave']}")

    return {"dados": {"status": "revogado", "id": chave_id}}


@router.post("/{chave_id}/desabilitar")
async def desabilitar_chave(
    chave_id: str = Path(...),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        row = (await db.execute(
            text("""
                update plataforma.chave_api
                set status = 'desabilitado'
                where id = :id and cliente_id = :cid and status = 'ativo' and revogada_em is null
                returning id, hash_chave
            """),
            {"id": chave_id, "cid": cliente_id},
        )).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail={"codigo": "CHAVE_NAO_ENCONTRADA", "mensagem": "Chave não encontrada ou já desabilitada."})
        await db.commit()

    redis = await get_redis()
    if redis:
        await redis.delete(f"api_key:{row['hash_chave']}")

    return {"dados": {"status": "desabilitado", "id": chave_id}}


@router.post("/{chave_id}/habilitar")
async def habilitar_chave(
    chave_id: str = Path(...),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        plano = await _plano_do_tenant(db, cliente_id)
        limite = plano["limite_api_keys"]
        if limite != -1:
            contagem = (await db.execute(
                text("select count(*) from plataforma.chave_api where cliente_id = :cid and status = 'ativo'"),
                {"cid": cliente_id},
            )).scalar_one()
            if contagem >= limite:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={"codigo": "LIMITE_API_KEYS", "mensagem": f"Plano {plano['nome']} permite {limite} chave(s) ativa(s). Desabilite ou exclua outra para habilitar esta."},
                )

        row = (await db.execute(
            text("""
                update plataforma.chave_api
                set status = 'ativo'
                where id = :id and cliente_id = :cid and status = 'desabilitado' and revogada_em is null
                returning id
            """),
            {"id": chave_id, "cid": cliente_id},
        )).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail={"codigo": "CHAVE_NAO_ENCONTRADA", "mensagem": "Chave não encontrada ou já está ativa."})
        await db.commit()

    return {"dados": {"status": "ativo", "id": chave_id}}


@router.post("/{chave_id}/rotacionar", status_code=status.HTTP_201_CREATED)
async def rotacionar_chave(
    chave_id: str = Path(...),
    request: Request = None,
    usuario_id: str = Depends(_ROLES_ADMIN),
) -> dict:
    cliente_id = await _tenant_ativo(request)
    async with SessionLocal() as db:
        old = (await db.execute(
            text("select nome, ambiente, plano_id, hash_chave from plataforma.chave_api where id = :id and cliente_id = :cid and status = 'ativo'"),
            {"id": chave_id, "cid": cliente_id},
        )).mappings().first()
        if not old:
            raise HTTPException(status_code=404, detail={"codigo": "CHAVE_NAO_ENCONTRADA", "mensagem": "Chave não encontrada ou já revogada."})

        await _revogar_chave_db(db, chave_id, cliente_id, usuario_id)

        chave_plain = _gerar_chave_plain(old["ambiente"] or "producao")
        hash_chave = gerar_hash_sha256(chave_plain)
        prefixo = chave_plain[:10]

        nova = (await db.execute(
            text("""
                insert into plataforma.chave_api
                    (cliente_id, plano_id, hash_chave, prefixo_chave, status, nome, ambiente, escopos, criada_por_usuario_id)
                values
                    (:cid, :pid, :hash, :prefixo, 'ativo', :nome, :amb, array[]::text[], :uid)
                returning id, criado_em
            """),
            {
                "cid": cliente_id,
                "pid": old["plano_id"],
                "hash": hash_chave,
                "prefixo": prefixo,
                "nome": old["nome"],
                "amb": old["ambiente"] or "producao",
                "uid": usuario_id,
            },
        )).mappings().first()
        await db.commit()

    redis = await get_redis()
    if redis:
        await redis.delete(f"api_key:{old['hash_chave']}")

    return {
        "dados": {
            "id": str(nova["id"]),
            "chave_plain": chave_plain,
            "prefixo": prefixo,
            "criado_em": nova["criado_em"].isoformat(),
        }
    }
