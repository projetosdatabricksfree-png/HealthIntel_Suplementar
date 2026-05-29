"""Hardgate de cobertura mínima das tabelas `api_ans.*` prometidas no site.

Lê o mesmo catálogo usado pelo endpoint público `/status/cobertura`
(`api/app/services/status_cobertura.py`) e exige que cada dataset:

* Esteja populado (≥ MIN_LINHAS_OK linhas).
* Tenha `MAX(coluna_temporal)` em ano ≥ FRESHNESS_ANO_MIN.

Datasets reconhecidamente em remediação (drift documentado em
`docs/runbooks/sprint_s2_fase_a_drift_diagnostico.md`) ficam na lista
`DATASETS_EM_REMEDIACAO` — o teste anota `xfail` em vez de falhar,
para não bloquear CI enquanto a decisão de produto não sai.

Variável de ambiente para rodar localmente:

    HEALTHINTEL_PG_DSN=postgresql+psycopg://healthintel:healthintel@localhost:5432/healthintel \\
        pytest tests/hardgates/test_cobertura_api_ans_minima.py -v

Em CI, usa o DSN padrão configurado no compose.
"""

from __future__ import annotations

import os
import re

import pytest
import sqlalchemy
from sqlalchemy import text

from api.app.services.status_cobertura import DATASETS

MIN_LINHAS_OK = 1_000
FRESHNESS_ANO_MIN = 2024

DATASETS_EM_REMEDIACAO = {
    "reajustes",  # drift de layout — ver runbook S2 Fase A
    "vda",        # dataset mudou de natureza na ANS
    "fip",        # ingestão experimental, formato divergente
    "cnes",       # sub-ingerido em granularidade
    "sib_operadora",  # backfill 2023-2024 pendente
    "nip",        # parado em 2020-12 — backfill pendente
}


def _ano_de(texto: str | None) -> int | None:
    if not texto:
        return None
    digitos = re.findall(r"\d{4}", str(texto))
    anos = [int(d) for d in digitos if 2000 <= int(d) <= 2100]
    return max(anos) if anos else None


def _dsn() -> str:
    return os.getenv(
        "HEALTHINTEL_PG_DSN",
        "postgresql+psycopg2://healthintel:healthintel@localhost:5432/healthintel",
    )


@pytest.fixture(scope="module")
def engine():
    eng = sqlalchemy.create_engine(_dsn())
    try:
        yield eng
    finally:
        eng.dispose()


@pytest.mark.parametrize("dataset", DATASETS, ids=lambda d: d.dataset)
def test_dataset_populado(engine, dataset):
    """Garante que cada dataset prometido tem dados e está fresco."""
    if dataset.dataset in DATASETS_EM_REMEDIACAO:
        pytest.xfail(f"{dataset.dataset}: em remediação (ver sprint_s2_fase_a_drift_diagnostico.md)")

    with engine.connect() as conn:
        try:
            if dataset.coluna_temporal:
                row = conn.execute(
                    text(
                        f"SELECT MAX({dataset.coluna_temporal})::text AS maximo, "
                        f"COUNT(*) AS linhas FROM {dataset.tabela}"
                    )
                ).mappings().first()
            else:
                row = conn.execute(
                    text(f"SELECT NULL::text AS maximo, COUNT(*) AS linhas FROM {dataset.tabela}")
                ).mappings().first()
        except sqlalchemy.exc.SQLAlchemyError as exc:
            pytest.fail(f"{dataset.tabela}: erro ao consultar: {exc}")

    linhas = int(row["linhas"]) if row else 0
    maximo = row["maximo"] if row else None

    assert linhas >= MIN_LINHAS_OK, (
        f"{dataset.dataset} ({dataset.tabela}): apenas {linhas} linhas (mínimo {MIN_LINHAS_OK}). "
        f"Provável regressão de ingestão."
    )

    if dataset.coluna_temporal:
        ano = _ano_de(maximo)
        assert ano is not None and ano >= FRESHNESS_ANO_MIN, (
            f"{dataset.dataset} ({dataset.tabela}): MAX({dataset.coluna_temporal})={maximo!r} "
            f"(ano detectado {ano}) abaixo do mínimo {FRESHNESS_ANO_MIN}. "
            f"DAG provavelmente parou de rodar."
        )
