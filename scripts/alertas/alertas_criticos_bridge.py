#!/usr/bin/env python3
"""Bridge Postgres -> Slack/email para alertas criticos de backup.

Variaveis de ambiente:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    SLACK_WEBHOOK_URL   — webhook Slack (ex: https://hooks.slack.com/services/...)
    ALERTAS_EMAIL_DEST  — endereco de destino (ex: ops@healthintel.com.br)
    ALERTAS_SMTP_HOST   — host SMTP (ex: smtp.gmail.com)
    ALERTAS_SMTP_PORT   — porta SMTP (default: 587)
    ALERTAS_SMTP_USER   — usuario SMTP
    ALERTAS_SMTP_PASS   — senha SMTP
    ALERTAS_JANELA_MIN  — janela de busca em minutos (default: 15)

Cron (VPS):
    */5 * * * * root /opt/healthintel/scripts/alertas/cron_alertas.sh
"""

import json
import os
import smtplib
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import asyncpg


POSTGRES_DSN = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'healthintel')}"
    f":{os.getenv('POSTGRES_PASSWORD', 'healthintel')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}"
    f":{os.getenv('POSTGRES_PORT', '5432')}"
    f"/{os.getenv('POSTGRES_DB', 'healthintel')}"
)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
ALERTAS_EMAIL_DEST = os.getenv("ALERTAS_EMAIL_DEST", "")
ALERTAS_SMTP_HOST = os.getenv("ALERTAS_SMTP_HOST", "")
ALERTAS_SMTP_PORT = int(os.getenv("ALERTAS_SMTP_PORT", "587"))
ALERTAS_SMTP_USER = os.getenv("ALERTAS_SMTP_USER", "")
ALERTAS_SMTP_PASS = os.getenv("ALERTAS_SMTP_PASS", "")
ALERTAS_JANELA_MIN = int(os.getenv("ALERTAS_JANELA_MIN", "15"))


async def _buscar_alertas() -> list[dict]:
    conn = await asyncpg.connect(POSTGRES_DSN)
    try:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=ALERTAS_JANELA_MIN)
        rows = await conn.fetch(
            """
            SELECT id, verificado_em, check_tipo, severidade, mensagem
            FROM plataforma.backup_alerta
            WHERE severidade = 'critico'
              AND verificado_em >= $1
            ORDER BY verificado_em DESC
            """,
            cutoff,
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


def _enviar_slack(alertas: list[dict]) -> None:
    if not SLACK_WEBHOOK_URL:
        return
    linhas = "\n".join(
        f"• [{a['verificado_em'].strftime('%H:%M:%S')}] *{a['check_tipo']}* — {a['mensagem']}"
        for a in alertas
    )
    payload = {
        "text": f":rotating_light: *[HealthIntel] {len(alertas)} alerta(s) critico(s) nos ultimos {ALERTAS_JANELA_MIN} min*\n{linhas}"
    }
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            print(f"[alertas_bridge] Slack respondeu {resp.status}", file=sys.stderr)


def _enviar_email(alertas: list[dict]) -> None:
    if not all([ALERTAS_EMAIL_DEST, ALERTAS_SMTP_HOST, ALERTAS_SMTP_USER, ALERTAS_SMTP_PASS]):
        return
    linhas = "\n".join(
        f"- [{a['verificado_em'].strftime('%Y-%m-%d %H:%M:%S')}] {a['check_tipo']}: {a['mensagem']}"
        for a in alertas
    )
    msg = EmailMessage()
    msg["Subject"] = f"[HealthIntel] {len(alertas)} alerta(s) critico(s) de backup"
    msg["From"] = ALERTAS_SMTP_USER
    msg["To"] = ALERTAS_EMAIL_DEST
    msg.set_content(
        f"Alertas criticos detectados nos ultimos {ALERTAS_JANELA_MIN} minutos:\n\n{linhas}\n"
        f"\nVerifique plataforma.backup_alerta para detalhes completos."
    )
    with smtplib.SMTP(ALERTAS_SMTP_HOST, ALERTAS_SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(ALERTAS_SMTP_USER, ALERTAS_SMTP_PASS)
        smtp.send_message(msg)


async def main() -> None:
    alertas = await _buscar_alertas()
    if not alertas:
        print(f"[alertas_bridge] Nenhum alerta critico nos ultimos {ALERTAS_JANELA_MIN} min.")
        return

    print(f"[alertas_bridge] {len(alertas)} alerta(s) critico(s) encontrado(s). Notificando...")

    erros = []
    try:
        _enviar_slack(alertas)
        print("[alertas_bridge] Slack: enviado.")
    except Exception as exc:
        erros.append(f"Slack: {exc}")

    try:
        _enviar_email(alertas)
        print("[alertas_bridge] Email: enviado.")
    except Exception as exc:
        erros.append(f"Email: {exc}")

    if erros:
        print(f"[alertas_bridge] Erros de notificacao: {erros}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
