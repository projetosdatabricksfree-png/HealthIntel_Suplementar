"""Endpoints de autenticação — /v1/auth/*"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, field_validator

from api.app.dependencia_sessao import obter_usuario_sessao
from api.app.services import auth_service
from api.app.services.auth_service import AuthError
from api.app.services.email_service import enviar_email_async
from api.app.util.validators_br import (
    normalizar_cnpj,
    normalizar_telefone,
    validar_cnpj,
    validar_telefone_br,
)

SEGMENTOS_PERMITIDOS = {
    "operadora",
    "corretora_administradora",
    "healthtech",
    "consultoria",
    "hospital_prestador",
    "escritorio_juridico",
    "bi_dados",
    "outro",
}

OBJETIVOS_PERMITIDOS = {
    "testar_api",
    "avaliar_dados_ans",
    "integrar_bi",
    "pesquisa_regulatoria",
    "avaliacao_comercial",
}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _ua(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _tratar_auth_error(exc: AuthError) -> HTTPException:
    return HTTPException(
        status_code=exc.status,
        detail={"codigo": exc.codigo, "mensagem": exc.mensagem},
    )


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CadastroInput(BaseModel):
    email: EmailStr
    nome: str
    senha: str
    empresa: str
    cnpj: str
    telefone: str
    cargo: str
    segmento: str
    objetivo_uso: str
    aceite_termos: bool
    aceite_lgpd: bool
    site_empresa: str | None = None
    tamanho_empresa: str | None = None
    mensagem: str | None = None

    @field_validator("nome", "empresa", "cargo")
    @classmethod
    def texto_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Campo obrigatório.")
        return v.strip()

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter ao menos 8 caracteres.")
        return v

    @field_validator("cnpj")
    @classmethod
    def cnpj_valido(cls, v: str) -> str:
        if not validar_cnpj(v):
            raise ValueError("CNPJ inválido.")
        return normalizar_cnpj(v)

    @field_validator("telefone")
    @classmethod
    def telefone_valido(cls, v: str) -> str:
        if not validar_telefone_br(v):
            raise ValueError("Telefone inválido. Use DDD + número (10 ou 11 dígitos).")
        return normalizar_telefone(v)

    @field_validator("segmento")
    @classmethod
    def segmento_valido(cls, v: str) -> str:
        if v not in SEGMENTOS_PERMITIDOS:
            raise ValueError(f"Segmento inválido. Use um de: {', '.join(sorted(SEGMENTOS_PERMITIDOS))}.")
        return v

    @field_validator("objetivo_uso")
    @classmethod
    def objetivo_valido(cls, v: str) -> str:
        if v not in OBJETIVOS_PERMITIDOS:
            raise ValueError(f"Objetivo inválido. Use um de: {', '.join(sorted(OBJETIVOS_PERMITIDOS))}.")
        return v

    @field_validator("aceite_termos", "aceite_lgpd")
    @classmethod
    def aceite_obrigatorio(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Aceite obrigatório.")
        return v


class LoginInput(BaseModel):
    email: EmailStr
    senha: str


class GoogleLoginInput(BaseModel):
    id_token: str


class VerificarEmailInput(BaseModel):
    token: str


class ReenviarVerificacaoInput(BaseModel):
    email: EmailStr


class SolicitarResetInput(BaseModel):
    email: EmailStr


class ConfirmarResetInput(BaseModel):
    token: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter ao menos 8 caracteres.")
        return v


class RefreshInput(BaseModel):
    refresh_token: str


class LogoutInput(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
async def cadastro(body: CadastroInput, request: Request) -> dict:
    perfil_b2b = {
        "empresa": body.empresa,
        "cnpj": body.cnpj,
        "telefone": body.telefone,
        "cargo": body.cargo,
        "segmento": body.segmento,
        "objetivo_uso": body.objetivo_uso,
        "site_empresa": body.site_empresa,
        "tamanho_empresa": body.tamanho_empresa,
        "mensagem": body.mensagem,
        "aceite_termos": body.aceite_termos,
        "aceite_lgpd": body.aceite_lgpd,
    }
    resultado = await auth_service.cadastrar_usuario(
        email=str(body.email),
        nome=body.nome,
        senha=body.senha,
        ip=_ip(request),
        perfil_b2b=perfil_b2b,
    )
    if "token" in resultado:
        from api.app.core.config import get_settings
        settings = get_settings()
        link = f"{settings.frontend_public_url}/verificar-email?token={resultado['token']}"
        subject = "Confirme seu e-mail — HealthIntel"
        txt = f"Olá, {body.nome}!\n\nClique no link abaixo para confirmar seu cadastro:\n{link}\n\nO link expira em 24 horas."
        html = _html_verificacao(body.nome, link)
        await enviar_email_async(subject, txt, html, to_email=str(body.email))

    return {"status": "pendente_verificacao", "mensagem": "Verifique seu e-mail para ativar a conta."}


@router.post("/login")
async def login(body: LoginInput, request: Request) -> dict:
    try:
        return await auth_service.login(
            email=str(body.email),
            senha=body.senha,
            ip=_ip(request),
            user_agent=_ua(request),
        )
    except AuthError as e:
        raise _tratar_auth_error(e)


@router.post("/google")
async def login_google(body: GoogleLoginInput, request: Request) -> dict:
    try:
        return await auth_service.login_google(
            id_token=body.id_token,
            ip=_ip(request),
            user_agent=_ua(request),
        )
    except AuthError as e:
        raise _tratar_auth_error(e)


@router.post("/verificar-email")
async def verificar_email(body: VerificarEmailInput) -> dict:
    try:
        await auth_service.verificar_email(body.token)
        return {"status": "ok", "mensagem": "E-mail verificado com sucesso."}
    except AuthError as e:
        raise _tratar_auth_error(e)


@router.post("/reenviar-verificacao")
async def reenviar_verificacao(body: ReenviarVerificacaoInput) -> dict:
    resultado = await auth_service.reenviar_verificacao(str(body.email))
    if "token" in resultado:
        from api.app.core.config import get_settings
        settings = get_settings()
        link = f"{settings.frontend_public_url}/verificar-email?token={resultado['token']}"
        subject = "Confirme seu e-mail — HealthIntel"
        txt = f"Novo link de verificação:\n{link}\n\nExpira em 24 horas."
        html = _html_verificacao("", link)
        await enviar_email_async(subject, txt, html, to_email=str(body.email))
    return {"status": "ok", "mensagem": "Se o e-mail estiver cadastrado e pendente, um link foi enviado."}


@router.post("/reset/solicitar")
async def solicitar_reset(body: SolicitarResetInput) -> dict:
    resultado = await auth_service.solicitar_reset(str(body.email))
    if resultado.get("token"):
        from api.app.core.config import get_settings
        settings = get_settings()
        link = f"{settings.frontend_public_url}/reset-senha?token={resultado['token']}"
        subject = "Redefinição de senha — HealthIntel"
        txt = f"Clique no link abaixo para redefinir sua senha:\n{link}\n\nExpira em 30 minutos."
        html = _html_reset(link)
        await enviar_email_async(subject, txt, html, to_email=str(body.email))
    return {"status": "ok", "mensagem": "Se o e-mail estiver cadastrado, um link foi enviado."}


@router.post("/reset/confirmar")
async def confirmar_reset(body: ConfirmarResetInput) -> dict:
    try:
        await auth_service.confirmar_reset(body.token, body.nova_senha)
        return {"status": "ok", "mensagem": "Senha redefinida com sucesso."}
    except AuthError as e:
        raise _tratar_auth_error(e)


@router.post("/refresh")
async def refresh(body: RefreshInput) -> dict:
    try:
        return await auth_service.refresh_access_token(body.refresh_token)
    except AuthError as e:
        raise _tratar_auth_error(e)


@router.post("/logout")
async def logout(body: LogoutInput) -> dict:
    await auth_service.logout(body.refresh_token)
    return {"status": "ok"}


@router.post("/logout-tudo")
async def logout_tudo(
    request: Request,
    usuario_id: str = Depends(obter_usuario_sessao),
) -> dict:
    await auth_service.logout_tudo(usuario_id)
    return {"status": "ok", "mensagem": "Todas as sessões encerradas."}


# ---------------------------------------------------------------------------
# Templates de e-mail (HTML simples)
# ---------------------------------------------------------------------------

def _html_verificacao(nome: str, link: str) -> str:
    saudacao = f"Olá, {nome}!<br>" if nome else ""
    return f"""<!doctype html>
<html><body style="font-family:-apple-system,Inter,sans-serif;color:#102a43;max-width:640px;margin:0 auto;padding:24px;">
  <h2 style="color:#0878c9">Confirme seu e-mail — HealthIntel</h2>
  <p>{saudacao}Clique no botão abaixo para confirmar sua conta.</p>
  <p><a href="{link}" style="background:#0878c9;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;">Confirmar e-mail</a></p>
  <p style="color:#627d98;font-size:12px">O link expira em 24 horas. Se não solicitou, ignore este e-mail.</p>
</body></html>"""


def _html_reset(link: str) -> str:
    return f"""<!doctype html>
<html><body style="font-family:-apple-system,Inter,sans-serif;color:#102a43;max-width:640px;margin:0 auto;padding:24px;">
  <h2 style="color:#0878c9">Redefinição de senha — HealthIntel</h2>
  <p>Clique no botão abaixo para criar uma nova senha.</p>
  <p><a href="{link}" style="background:#0878c9;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;">Redefinir senha</a></p>
  <p style="color:#627d98;font-size:12px">O link expira em 30 minutos. Se não solicitou, ignore este e-mail.</p>
</body></html>"""
