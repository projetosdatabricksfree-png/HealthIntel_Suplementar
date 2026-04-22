import asyncio
import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal


async def _resumo() -> dict:
    async with SessionLocal() as session:
        result = await session.execute(
            text(
                """
                select
                    count(*) as total_registros,
                    count(distinct competencia) as total_competencias,
                    min(score_v2) as menor_score,
                    max(score_v2) as maior_score
                from nucleo_ans.fat_score_v2_operadora_mensal
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
        "+tag:financeiro_v2",
        "+tag:score_v2",
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True, env=env)
    if resultado.returncode != 0:
        print(resultado.stdout)
        print(resultado.stderr)
        raise SystemExit(resultado.returncode)

    resumo = await _resumo()
    if int(resumo.get("total_registros", 0)) < 4:
        raise SystemExit("Score v2 sem registros")
    if int(resumo.get("total_competencias", 0)) < 2:
        raise SystemExit("Score v2 sem competencias")
    menor_score = resumo.get("menor_score")
    maior_score = resumo.get("maior_score")
    if menor_score is not None and float(menor_score) < 0:
        raise SystemExit("Score v2 abaixo de zero")
    if maior_score is not None and float(maior_score) > 100:
        raise SystemExit("Score v2 acima de 100")

    print(
        json.dumps(
            {"dbt": "ok", "resumo": {chave: _serializar(valor) for chave, valor in resumo.items()}},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
