"""Lógica de autenticação: cadastro, login, verificação, reset, refresh, logout."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.security import (
    decodificar_access_token,
    gerar_access_token,
    gerar_hash_sha256,
    gerar_token_aleatorio,
    hash_senha,
    verificar_senha,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthError(Exception):
    def __init__(self, codigo: str, mensagem: str, status: int = 400):
        self.codigo = codigo
        self.mensagem = mensagem
        self.status = status
        super().__init__(mensagem)


async def _provisionar_plano_free(db, usuario_id: str, email: str, nome: str) -> str | None:
    """Idempotente: cria cliente free + cliente_usuario se o usuário não tem tenant."""
    existing = (await db.execute(
        text("SELECT cliente_id FROM plataforma.cliente_usuario WHERE usuario_id = cast(:uid as uuid) AND status = 'ativo' LIMIT 1"),
        {"uid": usuario_id},
    )).first()
    if existing:
        return str(existing[0])

    plano = (await db.execute(
        text("SELECT id FROM plataforma.plano WHERE nome = 'free' AND status = 'ativo' LIMIT 1"),
    )).first()
    if not plano:
        return None

    novo_id = str(uuid4())
    await db.execute(
        text("""
            INSERT INTO plataforma.cliente (id, nome, email, status, plano_id)
            VALUES (:id, :nome, :email, 'ativo', cast(:plano_id as uuid))
            ON CONFLICT (email) DO NOTHING
        """),
        {"id": novo_id, "nome": nome, "email": email, "plano_id": str(plano[0])},
    )
    row = (await db.execute(
        text("SELECT id FROM plataforma.cliente WHERE email = :email LIMIT 1"),
        {"email": email},
    )).first()
    if not row:
        return None
    cliente_id = str(row[0])
    await db.execute(
        text("""
            INSERT INTO plataforma.cliente_usuario (cliente_id, usuario_id, role, status)
            VALUES (cast(:cid as uuid), cast(:uid as uuid), 'owner', 'ativo')
            ON CONFLICT (cliente_id, usuario_id) DO NOTHING
        """),
        {"cid": cliente_id, "uid": usuario_id},
    )
    return cliente_id


# ---------------------------------------------------------------------------
# Cadastro
# ---------------------------------------------------------------------------

async def cadastrar_usuario(email: str, nome: str, senha: str, ip: str | None = None) -> dict:
    async with SessionLocal() as db:
        existe = await db.execute(
            text("select id from plataforma.usuario where email = :email"),
            {"email": email},
        )
        if existe.first():
            # Mensagem genérica anti-enumeração
            return {"status": "pendente_verificacao"}

        uid_result = await db.execute(
            text(
                """
                insert into plataforma.usuario (email, nome, senha_hash, status)
                values (:email, :nome, :hash, 'pendente_email')
                returning id
                """
            ),
            {"email": email, "nome": nome, "hash": hash_senha(senha)},
        )
        usuario_id = str(uid_result.scalar_one())

        token_plain, token_hash = gerar_token_aleatorio()
        expira = datetime.now(UTC) + timedelta(hours=settings.auth_email_verification_ttl_hours)
        await db.execute(
            text(
                """
                insert into plataforma.token_verificacao (usuario_id, tipo, hash_token, expira_em, ip_origem)
                values (:uid, 'verificar_email', :hash, :exp, :ip)
                """
            ),
            {"uid": usuario_id, "hash": token_hash, "exp": expira, "ip": ip},
        )
        await db.commit()

    return {"status": "pendente_verificacao", "token": token_plain, "usuario_id": usuario_id}


# ---------------------------------------------------------------------------
# Verificar e-mail
# ---------------------------------------------------------------------------

async def verificar_email(token_plain: str) -> None:
    token_hash = gerar_hash_sha256(token_plain)
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select id, usuario_id, expira_em, consumido_em
                from plataforma.token_verificacao
                where hash_token = :hash and tipo = 'verificar_email'
                """
            ),
            {"hash": token_hash},
        )).mappings().first()

        if not row:
            raise AuthError("TOKEN_INVALIDO", "Token inválido.", 400)
        if row["consumido_em"]:
            raise AuthError("TOKEN_JA_USADO", "Token já utilizado.", 400)
        if row["expira_em"] < datetime.now(UTC):
            raise AuthError("TOKEN_EXPIRADO", "Token expirado.", 400)

        await db.execute(
            text("update plataforma.token_verificacao set consumido_em = now() where id = :id"),
            {"id": row["id"]},
        )
        await db.execute(
            text(
                """
                update plataforma.usuario
                set status = 'ativo', email_verificado_em = now(), atualizado_em = now()
                where id = :uid
                """
            ),
            {"uid": row["usuario_id"]},
        )
        await db.commit()

        usuario_row = (await db.execute(
            text("SELECT nome, email FROM plataforma.usuario WHERE id = cast(:uid as uuid)"),
            {"uid": row["usuario_id"]},
        )).mappings().first()
        if usuario_row:
            await _provisionar_plano_free(db, row["usuario_id"], usuario_row["email"], usuario_row["nome"])
            await db.commit()


# ---------------------------------------------------------------------------
# Reenviar verificação
# ---------------------------------------------------------------------------

async def reenviar_verificacao(email: str) -> dict:
    async with SessionLocal() as db:
        row = (await db.execute(
            text("select id, status from plataforma.usuario where email = :email"),
            {"email": email},
        )).mappings().first()

        # Anti-enumeração: sempre 200
        if not row or row["status"] != "pendente_email":
            return {"status": "ok"}

        # Invalida tokens anteriores do mesmo tipo
        await db.execute(
            text(
                """
                update plataforma.token_verificacao
                set consumido_em = now()
                where usuario_id = :uid and tipo = 'verificar_email' and consumido_em is null
                """
            ),
            {"uid": row["id"]},
        )

        token_plain, token_hash = gerar_token_aleatorio()
        expira = datetime.now(UTC) + timedelta(hours=settings.auth_email_verification_ttl_hours)
        await db.execute(
            text(
                """
                insert into plataforma.token_verificacao (usuario_id, tipo, hash_token, expira_em)
                values (:uid, 'verificar_email', :hash, :exp)
                """
            ),
            {"uid": row["id"], "hash": token_hash, "exp": expira},
        )
        await db.commit()

    return {"status": "ok", "token": token_plain}


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def login(email: str, senha: str, ip: str | None = None, user_agent: str | None = None) -> dict:
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select id, nome, senha_hash, status, falhas_login, bloqueado_ate, email_verificado_em
                from plataforma.usuario where email = :email
                """
            ),
            {"email": email},
        )).mappings().first()

        # Mensagem genérica para e-mail não encontrado
        if not row:
            raise AuthError("CREDENCIAIS_INVALIDAS", "E-mail ou senha incorretos.", 401)

        if row["bloqueado_ate"] and row["bloqueado_ate"] > datetime.now(UTC):
            raise AuthError("CONTA_BLOQUEADA", "Conta temporariamente bloqueada. Tente novamente mais tarde.", 429)

        if row["status"] == "pendente_email":
            raise AuthError("EMAIL_NAO_VERIFICADO", "Verifique seu e-mail antes de fazer login.", 403)

        if row["status"] not in {"ativo"}:
            raise AuthError("CREDENCIAIS_INVALIDAS", "E-mail ou senha incorretos.", 401)

        if not row["senha_hash"] or not verificar_senha(senha, row["senha_hash"]):
            novas_falhas = row["falhas_login"] + 1
            bloqueado_ate = None
            if novas_falhas >= settings.auth_login_lockout_max:
                bloqueado_ate = datetime.now(UTC) + timedelta(minutes=settings.auth_login_lockout_min)
                novas_falhas = 0
            await db.execute(
                text(
                    """
                    update plataforma.usuario
                    set falhas_login = :f, bloqueado_ate = :b, atualizado_em = now()
                    where id = :uid
                    """
                ),
                {"f": novas_falhas, "b": bloqueado_ate, "uid": row["id"]},
            )
            await db.commit()
            raise AuthError("CREDENCIAIS_INVALIDAS", "E-mail ou senha incorretos.", 401)

        usuario_id = str(row["id"])

        # Reset falhas + atualizar ultimo_login
        await db.execute(
            text(
                """
                update plataforma.usuario
                set falhas_login = 0, bloqueado_ate = null, ultimo_login_em = now(), atualizado_em = now()
                where id = :uid
                """
            ),
            {"uid": usuario_id},
        )

        # Tenant ativo = primeiro cliente vinculado como owner
        tenant_row = (await db.execute(
            text(
                """
                select cu.cliente_id, cu.role
                from plataforma.cliente_usuario cu
                where cu.usuario_id = :uid and cu.status = 'ativo'
                order by cu.criado_em
                limit 1
                """
            ),
            {"uid": usuario_id},
        )).mappings().first()

        cliente_id = str(tenant_row["cliente_id"]) if tenant_row else None
        role = str(tenant_row["role"]) if tenant_row else "viewer"

        if not tenant_row:
            nome_usuario = str(row.get("nome") or email.split("@")[0])
            cliente_id_novo = await _provisionar_plano_free(db, usuario_id, email, nome_usuario)
            if cliente_id_novo:
                cliente_id = cliente_id_novo
                role = "owner"

        tokens = await _criar_sessao(db, usuario_id, cliente_id, ip, user_agent)
        await db.commit()

    return {
        "access_token": gerar_access_token(usuario_id, cliente_id, role),
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "usuario_id": usuario_id,
        "cliente_id": cliente_id,
        "role": role,
    }


# ---------------------------------------------------------------------------
# Login via Google
# ---------------------------------------------------------------------------

async def login_google(id_token: str, ip: str | None = None, user_agent: str | None = None) -> dict:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    try:
        request = google_requests.Request()
        payload = google_id_token.verify_oauth2_token(
            id_token, request, settings.google_oauth_client_id
        )
    except Exception as exc:
        logger.warning("Google token inválido: %s", exc)
        raise AuthError("GOOGLE_TOKEN_INVALIDO", "Token Google inválido.", 401)

    google_sub = payload["sub"]
    email = payload.get("email", "")
    nome = payload.get("name") or email.split("@")[0]

    async with SessionLocal() as db:
        # Busca por google_sub primeiro, depois por e-mail
        row = (await db.execute(
            text("select id, status from plataforma.usuario where google_sub = :sub"),
            {"sub": google_sub},
        )).mappings().first()

        if not row and email:
            row = (await db.execute(
                text("select id, status from plataforma.usuario where email = :email"),
                {"email": email},
            )).mappings().first()
            if row:
                # Vincula google_sub ao usuário existente
                await db.execute(
                    text("update plataforma.usuario set google_sub = :sub, atualizado_em = now() where id = :uid"),
                    {"sub": google_sub, "uid": row["id"]},
                )

        if not row:
            # Novo usuário via Google — e-mail já verificado
            uid_result = await db.execute(
                text(
                    """
                    insert into plataforma.usuario (email, nome, google_sub, status, email_verificado_em)
                    values (:email, :nome, :sub, 'ativo', now())
                    returning id
                    """
                ),
                {"email": email, "nome": nome, "sub": google_sub},
            )
            usuario_id = str(uid_result.scalar_one())
        else:
            if row["status"] == "bloqueado":
                raise AuthError("CREDENCIAIS_INVALIDAS", "E-mail ou senha incorretos.", 401)
            usuario_id = str(row["id"])

        await db.execute(
            text("update plataforma.usuario set ultimo_login_em = now(), atualizado_em = now() where id = :uid"),
            {"uid": usuario_id},
        )

        tenant_row = (await db.execute(
            text(
                """
                select cu.cliente_id, cu.role
                from plataforma.cliente_usuario cu
                where cu.usuario_id = :uid and cu.status = 'ativo'
                order by cu.criado_em limit 1
                """
            ),
            {"uid": usuario_id},
        )).mappings().first()

        cliente_id = str(tenant_row["cliente_id"]) if tenant_row else None
        role = str(tenant_row["role"]) if tenant_row else "viewer"

        if not tenant_row:
            cliente_id_novo = await _provisionar_plano_free(db, usuario_id, email, nome)
            if cliente_id_novo:
                cliente_id = cliente_id_novo
                role = "owner"

        tokens = await _criar_sessao(db, usuario_id, cliente_id, ip, user_agent)
        await db.commit()

    return {
        "access_token": gerar_access_token(usuario_id, cliente_id, role),
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "usuario_id": usuario_id,
        "cliente_id": cliente_id,
        "role": role,
    }


# ---------------------------------------------------------------------------
# Reset de senha
# ---------------------------------------------------------------------------

async def solicitar_reset(email: str) -> dict:
    """Sempre retorna 200 (anti-enumeração). token é None se e-mail não existe."""
    async with SessionLocal() as db:
        row = (await db.execute(
            text("select id from plataforma.usuario where email = :email and status = 'ativo'"),
            {"email": email},
        )).mappings().first()

        if not row:
            return {"status": "ok", "token": None}

        # Invalida tokens anteriores
        await db.execute(
            text(
                """
                update plataforma.token_verificacao
                set consumido_em = now()
                where usuario_id = :uid and tipo = 'reset_senha' and consumido_em is null
                """
            ),
            {"uid": row["id"]},
        )

        token_plain, token_hash = gerar_token_aleatorio()
        expira = datetime.now(UTC) + timedelta(minutes=settings.auth_password_reset_ttl_min)
        await db.execute(
            text(
                """
                insert into plataforma.token_verificacao (usuario_id, tipo, hash_token, expira_em)
                values (:uid, 'reset_senha', :hash, :exp)
                """
            ),
            {"uid": row["id"], "hash": token_hash, "exp": expira},
        )
        await db.commit()

    return {"status": "ok", "token": token_plain, "usuario_id": str(row["id"])}


async def confirmar_reset(token_plain: str, nova_senha: str) -> None:
    token_hash = gerar_hash_sha256(token_plain)
    async with SessionLocal() as db:
        row = (await db.execute(
            text(
                """
                select id, usuario_id, expira_em, consumido_em
                from plataforma.token_verificacao
                where hash_token = :hash and tipo = 'reset_senha'
                """
            ),
            {"hash": token_hash},
        )).mappings().first()

        if not row or row["consumido_em"] or row["expira_em"] < datetime.now(UTC):
            raise AuthError("TOKEN_INVALIDO", "Token inválido ou expirado.", 400)

        await db.execute(
            text("update plataforma.token_verificacao set consumido_em = now() where id = :id"),
            {"id": row["id"]},
        )
        await db.execute(
            text(
                """
                update plataforma.usuario
                set senha_hash = :hash, senha_atualizada_em = now(), falhas_login = 0,
                    bloqueado_ate = null, atualizado_em = now()
                where id = :uid
                """
            ),
            {"hash": hash_senha(nova_senha), "uid": row["usuario_id"]},
        )
        # Revoga todas as sessões após reset
        await db.execute(
            text("update plataforma.sessao set revogada_em = now() where usuario_id = :uid and revogada_em is null"),
            {"uid": row["usuario_id"]},
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------

async def refresh_access_token(refresh_token_plain: str) -> dict:
    token_hash = gerar_hash_sha256(refresh_token_plain)
    async with SessionLocal() as db:
        sessao = (await db.execute(
            text(
                """
                select s.id, s.usuario_id, s.cliente_id_ativo, s.expira_em, s.revogada_em,
                       cu.role
                from plataforma.sessao s
                left join plataforma.cliente_usuario cu
                    on cu.usuario_id = s.usuario_id
                    and cu.cliente_id = s.cliente_id_ativo
                    and cu.status = 'ativo'
                where s.hash_refresh_token = :hash
                """
            ),
            {"hash": token_hash},
        )).mappings().first()

        if not sessao or sessao["revogada_em"] or sessao["expira_em"] < datetime.now(UTC):
            raise AuthError("REFRESH_INVALIDO", "Sessão inválida ou expirada.", 401)

        usuario_id = str(sessao["usuario_id"])
        cliente_id = str(sessao["cliente_id_ativo"]) if sessao["cliente_id_ativo"] else None
        role = str(sessao["role"]) if sessao["role"] else "viewer"

        # Rotação: revoga sessão atual, cria nova
        await db.execute(
            text("update plataforma.sessao set revogada_em = now() where id = :id"),
            {"id": sessao["id"]},
        )

        novo_plain, novo_hash = gerar_token_aleatorio()
        expira = datetime.now(UTC) + timedelta(days=settings.auth_jwt_refresh_ttl_days)
        await db.execute(
            text(
                """
                insert into plataforma.sessao
                    (usuario_id, cliente_id_ativo, hash_refresh_token, expira_em)
                values (:uid, :cid, :hash, :exp)
                """
            ),
            {"uid": usuario_id, "cid": cliente_id, "hash": novo_hash, "exp": expira},
        )
        await db.execute(
            text("update plataforma.usuario set ultimo_login_em = now() where id = :uid"),
            {"uid": usuario_id},
        )
        await db.commit()

    return {
        "access_token": gerar_access_token(usuario_id, cliente_id, role),
        "refresh_token": novo_plain,
        "token_type": "bearer",
    }


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

async def logout(refresh_token_plain: str) -> None:
    token_hash = gerar_hash_sha256(refresh_token_plain)
    async with SessionLocal() as db:
        await db.execute(
            text("update plataforma.sessao set revogada_em = now() where hash_refresh_token = :hash"),
            {"hash": token_hash},
        )
        await db.commit()


async def logout_tudo(usuario_id: str) -> None:
    async with SessionLocal() as db:
        await db.execute(
            text("update plataforma.sessao set revogada_em = now() where usuario_id = :uid and revogada_em is null"),
            {"uid": usuario_id},
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Perfil
# ---------------------------------------------------------------------------

async def obter_perfil(usuario_id: str) -> dict:
    async with SessionLocal() as db:
        usuario = (await db.execute(
            text(
                """
                select id, email, nome, avatar_url, status, email_verificado_em,
                       ultimo_login_em, criado_em
                from plataforma.usuario where id = :uid
                """
            ),
            {"uid": usuario_id},
        )).mappings().first()

        if not usuario:
            raise AuthError("USUARIO_NAO_ENCONTRADO", "Usuário não encontrado.", 404)

        tenants = (await db.execute(
            text(
                """
                select cu.cliente_id, cu.role, c.nome, c.status, pl.nome as plano_nome
                from plataforma.cliente_usuario cu
                join plataforma.cliente c on c.id = cu.cliente_id
                join plataforma.plano pl on pl.id = c.plano_id
                where cu.usuario_id = :uid and cu.status = 'ativo'
                order by cu.criado_em
                """
            ),
            {"uid": usuario_id},
        )).mappings().all()

    return {
        "id": str(usuario["id"]),
        "email": str(usuario["email"]),
        "nome": str(usuario["nome"]),
        "avatar_url": usuario["avatar_url"],
        "status": str(usuario["status"]),
        "email_verificado": usuario["email_verificado_em"] is not None,
        "ultimo_login_em": usuario["ultimo_login_em"].isoformat() if usuario["ultimo_login_em"] else None,
        "criado_em": usuario["criado_em"].isoformat(),
        "tenants": [
            {
                "cliente_id": str(t["cliente_id"]),
                "nome": str(t["nome"]),
                "role": str(t["role"]),
                "status": str(t["status"]),
                "plano_nome": str(t["plano_nome"]),
            }
            for t in tenants
        ],
    }


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

async def _criar_sessao(db, usuario_id: str, cliente_id: str | None, ip: str | None, user_agent: str | None) -> dict:
    plain, hash_token = gerar_token_aleatorio()
    expira = datetime.now(UTC) + timedelta(days=settings.auth_jwt_refresh_ttl_days)
    await db.execute(
        text(
            """
            insert into plataforma.sessao
                (usuario_id, cliente_id_ativo, hash_refresh_token, ip, user_agent, expira_em)
            values (:uid, :cid, :hash, :ip, :ua, :exp)
            """
        ),
        {
            "uid": usuario_id,
            "cid": cliente_id,
            "hash": hash_token,
            "ip": ip,
            "ua": user_agent,
            "exp": expira,
        },
    )
    return {"refresh_token": plain}
