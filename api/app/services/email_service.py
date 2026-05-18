"""Envio de email transacional via SMTP (Gmail por padrão).

Fail-soft: se SMTP não estiver configurado ou falhar, retorna status sem
levantar exceção — o lead já foi persistido antes da chamada.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def smtp_configurado() -> bool:
    return bool(_env("EMAIL_SMTP_HOST") and _env("EMAIL_SMTP_USER") and _env("EMAIL_SMTP_PASSWORD"))


def _enviar_smtp_sync(
    subject: str, body_text: str, body_html: str, to_email: str | None = None
) -> None:
    host = _env("EMAIL_SMTP_HOST", "smtp.gmail.com")
    port = int(_env("EMAIL_SMTP_PORT", "587"))
    user = _env("EMAIL_SMTP_USER")
    password = _env("EMAIL_SMTP_PASSWORD")
    from_name = _env("EMAIL_SMTP_FROM_NAME", "HealthIntel Contato")
    destino = to_email or _env("EMAIL_CONTATO_DESTINO", user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{user}>"
    msg["To"] = destino
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


async def enviar_email_async(
    subject: str, body_text: str, body_html: str, to_email: str | None = None
) -> str:
    """Envia email. Retorna 'enviado', 'fila_local' (falha) ou 'desabilitado'."""
    if not smtp_configurado():
        logger.info("SMTP não configurado, email não enviado (assunto=%s)", subject)
        return "desabilitado"
    try:
        await run_in_threadpool(_enviar_smtp_sync, subject, body_text, body_html, to_email)
        return "enviado"
    except Exception as exc:
        logger.exception("Falha SMTP ao enviar email: %s", exc)
        return "fila_local"


def montar_email_lead(payload: dict) -> tuple[str, str, str]:
    """Monta (subject, body_text, body_html) a partir do payload do lead."""
    empresa = payload.get("empresa", "—")
    plano = payload.get("plano") or "Sem plano informado"
    nome = payload.get("nome", "—")
    email = payload.get("email", "—")
    perfil = payload.get("perfil", "—")
    mensagem = payload.get("mensagem", "")
    origem = payload.get("origem") or "—"

    subject = f"[HealthIntel Lead] {empresa} — {plano}"

    body_text = (
        f"Novo lead recebido pelo site HealthIntel.\n\n"
        f"Nome:     {nome}\n"
        f"E-mail:   {email}\n"
        f"Empresa:  {empresa}\n"
        f"Perfil:   {perfil}\n"
        f"Plano:    {plano}\n"
        f"Origem:   {origem}\n\n"
        f"Mensagem:\n{mensagem}\n"
    )

    body_html = f"""<!doctype html>
<html><body style="font-family: -apple-system, Inter, sans-serif; color: #102a43; line-height: 1.6; max-width: 640px; margin: 0 auto; padding: 24px;">
  <h2 style="color: #0878c9; margin: 0 0 16px;">Novo lead HealthIntel</h2>
  <p style="color: #627d98; margin: 0 0 24px;">Recebido pelo site público — responder direto ao e-mail do lead.</p>
  <table cellpadding="8" style="width: 100%; border-collapse: collapse; background: #f5fbff; border-radius: 12px;">
    <tr><td style="font-weight: 600; width: 120px;">Nome</td><td>{_escape(nome)}</td></tr>
    <tr><td style="font-weight: 600;">E-mail</td><td><a href="mailto:{_escape(email)}">{_escape(email)}</a></td></tr>
    <tr><td style="font-weight: 600;">Empresa</td><td>{_escape(empresa)}</td></tr>
    <tr><td style="font-weight: 600;">Perfil</td><td>{_escape(perfil)}</td></tr>
    <tr><td style="font-weight: 600;">Plano</td><td>{_escape(plano)}</td></tr>
    <tr><td style="font-weight: 600;">Origem</td><td>{_escape(origem)}</td></tr>
  </table>
  <h3 style="margin: 24px 0 8px;">Mensagem</h3>
  <p style="background: white; border: 1px solid #d8eaf5; border-radius: 8px; padding: 16px; white-space: pre-wrap;">{_escape(mensagem)}</p>
  <p style="color: #627d98; font-size: 12px; margin-top: 24px;">Lead também persistido em <code>plataforma.lead_contato</code>.</p>
</body></html>"""

    return subject, body_text, body_html


def montar_email_api_key(payload: dict) -> tuple[str, str, str]:
    """Monta email transacional com a API key provisionada no checkout."""
    nome = payload.get("nome") or "cliente"
    email = payload.get("email", "")
    plano = payload.get("plano", "")
    chave_api = payload.get("chave_api", "")
    criado_em = payload.get("criado_em", "")

    subject = f"Seu acesso HealthIntel Core ANS - {plano}"

    body_text = (
        f"Olá, {nome}.\n\n"
        "Seu pagamento foi confirmado e sua API key HealthIntel foi provisionada.\n\n"
        f"Plano: {plano}\n"
        f"E-mail: {email}\n"
        f"Criado em: {criado_em}\n\n"
        f"API key:\n{chave_api}\n\n"
        "Use a chave no header HTTP abaixo em cada requisição:\n"
        f"X-API-Key: {chave_api}\n\n"
        "Guarde esta chave em local seguro. Ela não será exibida novamente.\n"
    )

    body_html = f"""<!doctype html>
<html><body style="font-family: -apple-system, Inter, sans-serif; color: #102a43; line-height: 1.6; max-width: 680px; margin: 0 auto; padding: 24px;">
  <h2 style="color: #0878c9; margin: 0 0 16px;">Acesso HealthIntel Core ANS</h2>
  <p>Olá, {_escape(str(nome))}. Seu pagamento foi confirmado e sua API key foi provisionada.</p>
  <table cellpadding="8" style="width: 100%; border-collapse: collapse; background: #f5fbff; border-radius: 12px;">
    <tr><td style="font-weight: 600; width: 120px;">Plano</td><td>{_escape(str(plano))}</td></tr>
    <tr><td style="font-weight: 600;">E-mail</td><td>{_escape(str(email))}</td></tr>
    <tr><td style="font-weight: 600;">Criado em</td><td>{_escape(str(criado_em))}</td></tr>
  </table>
  <h3 style="margin: 24px 0 8px;">API key</h3>
  <p style="background: #0b1f33; color: #e6f4ff; border-radius: 8px; padding: 16px; word-break: break-all; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;">{_escape(str(chave_api))}</p>
  <p>Use o header <code>X-API-Key</code> em cada requisição.</p>
  <p style="color: #627d98; font-size: 12px; margin-top: 24px;">Guarde esta chave em local seguro. Ela não será exibida novamente.</p>
</body></html>"""

    return subject, body_text, body_html


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
