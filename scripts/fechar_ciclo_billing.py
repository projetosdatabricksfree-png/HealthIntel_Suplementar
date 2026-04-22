import argparse
import asyncio
import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.schemas.billing import BillingFechamentoRequest
from api.app.services.billing import fechar_ciclo_faturamento


async def registrar_job(
    *,
    job_id: str,
    status: str,
    referencia: str,
    registros_processados: int,
    mensagem_erro: str | None = None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.job (
                    id,
                    dag_id,
                    nome_job,
                    fonte_ans,
                    status,
                    iniciado_em,
                    finalizado_em,
                    registro_processado,
                    registro_com_falha,
                    mensagem_erro
                ) values (
                    :id,
                    :dag_id,
                    :nome_job,
                    :fonte_ans,
                    :status,
                    :iniciado_em,
                    :finalizado_em,
                    :registro_processado,
                    :registro_com_falha,
                    :mensagem_erro
                )
                """
            ),
            {
                "id": job_id,
                "dag_id": "dag_billing_fechamento_mensal",
                "nome_job": f"billing_{referencia}",
                "fonte_ans": "plataforma.billing",
                "status": status,
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": registros_processados,
                "registro_com_falha": 0 if status == "sucesso" else 1,
                "mensagem_erro": mensagem_erro,
            },
        )
        await session.commit()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Fecha o ciclo mensal de billing do HealthIntel.")
    parser.add_argument("--referencia", required=True, help="Referencia YYYY-MM.")
    parser.add_argument("--cliente-id", default=None)
    parser.add_argument("--ator", default="script_billing")
    parser.add_argument("--origem", default="script")
    args = parser.parse_args()

    job_id = str(uuid4())
    try:
        resultado = await fechar_ciclo_faturamento(
            BillingFechamentoRequest(
                referencia=args.referencia,
                cliente_id=args.cliente_id,
                ator=args.ator,
                origem=args.origem,
            )
        )
        await registrar_job(
            job_id=job_id,
            status="sucesso",
            referencia=args.referencia,
            registros_processados=len(resultado["dados"]),
        )
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001
        await registrar_job(
            job_id=job_id,
            status="falha",
            referencia=args.referencia,
            registros_processados=0,
            mensagem_erro=str(exc),
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())
