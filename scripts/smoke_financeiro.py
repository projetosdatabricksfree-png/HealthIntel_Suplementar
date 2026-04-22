import asyncio
import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def _contar_trimestres() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    count(*) as total_registros,
                    count(distinct trimestre) as total_trimestres,
                    min(score_financeiro_base) as menor_score,
                    max(score_financeiro_base) as maior_score
                from nucleo_ans.fat_financeiro_operadora_trimestral
                """
            )
        )
        return dict(result.mappings().first() or {})


def _serializar(valor: object) -> object:
    if isinstance(valor, Decimal):
        return float(valor)
    return valor


async def main() -> None:
    env = os.environ.copy()
    env.setdefault("DBT_PROFILES_DIR", str(Path("healthintel_dbt").resolve()))
    dbt_executavel = Path(".venv/bin/dbt")
    comando_base = str(dbt_executavel) if dbt_executavel.exists() else "dbt"
    comando = [
        comando_base,
        "build",
        "--project-dir",
        "healthintel_dbt",
        "--select",
        "tag:financeiro",
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True, env=env)
    if resultado.returncode != 0:
        print(resultado.stdout)
        print(resultado.stderr)
        raise SystemExit(resultado.returncode)

    resumo = await _contar_trimestres()
    if int(resumo.get("total_trimestres", 0)) < 8:
        raise SystemExit("Cobertura financeira abaixo de 8 trimestres")
    if int(resumo.get("total_registros", 0)) <= 0:
        raise SystemExit("Fato financeiro sem registros")

    print(
        json.dumps(
            {"dbt": "ok", "resumo": {chave: _serializar(valor) for chave, valor in resumo.items()}},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
