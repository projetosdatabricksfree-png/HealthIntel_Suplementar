from __future__ import annotations

import asyncio

from sqlalchemy import text

from api.app.services.historico_sob_demanda import (
    EntitlementHistoricoAusenteError,
    aprovar_solicitacao_via_operacao,
    validar_acesso_competencia,
)
from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.historico_sob_demanda import processar_proxima_solicitacao_historico

CLIENTE_PADRAO = "90000000-0000-0000-0000-000000000101"
CLIENTE_PREMIUM = "90000000-0000-0000-0000-000000000102"


async def _preparar_cliente(session, cliente_id: str, email: str) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.cliente (
                id,
                nome,
                email,
                status,
                plano_id,
                status_cobranca,
                dia_fechamento
            ) values (
                cast(:cliente_id as uuid),
                :nome,
                :email,
                'ativo',
                '11111111-1111-1111-1111-111111111114',
                'em_dia',
                1
            )
            on conflict (email) do update set status = 'ativo'
            """
        ),
        {"cliente_id": cliente_id, "nome": email, "email": email},
    )


async def main() -> None:
    async with SessionLocal() as session:
        async with session.begin():
            await _preparar_cliente(session, CLIENTE_PADRAO, "smoke-historico-padrao@local")
            await _preparar_cliente(session, CLIENTE_PREMIUM, "smoke-historico-premium@local")
            await session.execute(
                text(
                    """
                    update plataforma.cliente_dataset_acesso
                       set ativo = false
                     where cliente_id in (
                         cast(:cliente_padrao as uuid),
                         cast(:cliente_premium as uuid)
                     )
                       and dataset_codigo = 'sib_operadora'
                       and ativo is true
                    """
                ),
                {"cliente_padrao": CLIENTE_PADRAO, "cliente_premium": CLIENTE_PREMIUM},
            )
            result = await session.execute(
                text(
                    """
                    insert into plataforma.solicitacao_historico (
                        cliente_id,
                        dataset_codigo,
                        competencia_inicio,
                        competencia_fim,
                        status,
                        motivo
                    ) values (
                        cast(:cliente_id as uuid),
                        'sib_operadora',
                        202401,
                        202401,
                        'pendente',
                        'smoke historico sob demanda'
                    )
                    returning id
                    """
                ),
                {"cliente_id": CLIENTE_PREMIUM},
            )
            solicitacao_id = int(result.scalar_one())
            await aprovar_solicitacao_via_operacao(
                solicitacao_id,
                aprovado_por="smoke",
                conn=session,
            )

        async with session.begin():
            try:
                await validar_acesso_competencia(
                    CLIENTE_PADRAO,
                    "sib_operadora",
                    202401,
                    session,
                )
            except EntitlementHistoricoAusenteError:
                padrao_bloqueado = True
            else:
                padrao_bloqueado = False

            premium_permitido = await validar_acesso_competencia(
                CLIENTE_PREMIUM,
                "sib_operadora",
                202401,
                session,
            )
            try:
                await validar_acesso_competencia(
                    CLIENTE_PREMIUM,
                    "sib_operadora",
                    202301,
                    session,
                )
            except Exception:
                fora_faixa_bloqueado = True
            else:
                fora_faixa_bloqueado = False
            hot_permitido = await validar_acesso_competencia(
                CLIENTE_PADRAO,
                "sib_operadora",
                202602,
                session,
            )
            resultado = await processar_proxima_solicitacao_historico(
                dry_run=True,
                conn=session,
            )
            particao = await session.scalar(
                text("select to_regclass('bruto_ans.sib_beneficiario_operadora_2024')::text")
            )
            concluida = await session.scalar(
                text(
                    """
                    select count(*)
                    from plataforma.solicitacao_historico
                    where id = :id
                      and status = 'concluida'
                    """
                ),
                {"id": solicitacao_id},
            )

    checks = {
        "padrao_bloqueado": padrao_bloqueado,
        "premium_permitido": bool(premium_permitido),
        "fora_faixa_bloqueado": fora_faixa_bloqueado,
        "hot_permitido": bool(hot_permitido),
        "dag_dry_run_concluida": resultado.status == "concluida",
        "particao_2024": particao == "bruto_ans.sib_beneficiario_operadora_2024",
        "solicitacao_concluida": int(concluida or 0) == 1,
    }
    if not all(checks.values()):
        raise SystemExit({"erro": "smoke_historico_sob_demanda_falhou", "checks": checks})
    print({"status": "ok", "solicitacao_id": solicitacao_id, "checks": checks})


if __name__ == "__main__":
    asyncio.run(main())
