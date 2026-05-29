"""Cobertura por dataset ANS para o endpoint público /status/cobertura.

Lê tabelas `api_ans.*` e devolve MIN/MAX/COUNT da coluna temporal relevante.
Usado pela landing para renderizar Coverage com dados reais.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

from api.app.core.database import SessionLocal


@dataclass(frozen=True)
class DatasetCobertura:
    dataset: str
    rotulo: str
    tabela: str
    coluna_temporal: str | None
    descricao: str


# Datasets prometidos no `Coverage.tsx` (frontend).
DATASETS: tuple[DatasetCobertura, ...] = (
    DatasetCobertura("cadop", "CADOP", "api_ans.api_bronze_cadop", "competencia", "Cadastro de operadoras de saúde suplementar"),
    DatasetCobertura("sib_operadora", "SIB · Operadora", "api_ans.api_bronze_sib_operadora", "competencia", "Beneficiários agregados por operadora"),
    DatasetCobertura("sib_municipio", "SIB · Município", "api_ans.api_bronze_sib_municipio", "competencia", "Beneficiários agregados por município e competência"),
    DatasetCobertura("cnes", "CNES", "api_ans.api_cnes_municipio", "competencia", "Rede de estabelecimentos, equipes e vínculos"),
    DatasetCobertura("diops", "DIOPS", "api_ans.api_bronze_diops", "trimestre", "Demonstrações financeiras das operadoras"),
    DatasetCobertura("fip", "FIP", "api_ans.api_bronze_fip", "trimestre", "Informações financeiras complementares"),
    DatasetCobertura("idss", "IDSS", "api_ans.api_bronze_idss", "ano_base", "Índice de Desempenho da Saúde Suplementar"),
    DatasetCobertura("nip", "NIP", "api_ans.api_bronze_nip", "trimestre", "Notificações de Intermediação Preliminar"),
    DatasetCobertura("reajustes", "Reajustes", "api_ans.api_reajuste_agrupamento", "competencia", "Reajustes autorizados por operadora"),
    DatasetCobertura("tuss", "ROL / TUSS", "api_ans.api_tuss_procedimento_vigente", None, "Catálogo de procedimentos vigentes"),
    DatasetCobertura("prudencial", "Prudencial / Garantias", "api_ans.api_prudencial_operadora_trimestral", "trimestre", "Suficiência patrimonial trimestral"),
    DatasetCobertura("vda", "VDA", "api_ans.api_bronze_vda", "competencia", "Valor a Devolver — componente de garantias"),
    DatasetCobertura("market_share", "Market Share", "api_ans.api_market_share_mensal", "competencia", "Share de mercado mensal derivado SIB"),
    DatasetCobertura("score", "Score HealthIntel", "api_ans.api_score_v3_operadora_mensal", "competencia_id", "Score V3 das operadoras"),
    DatasetCobertura("ranking", "Rankings", "api_ans.api_ranking_composto_mensal", "competencia_id", "Ranking composto mensal"),
)


def _competencia_recente(maximo: Any) -> bool:
    """Heurística: considera o dataset atualizado se max competência ≥ 2024.

    Formatos suportados: `YYYYMM`, `nTYYYY`, `YYYYTn`, `YYYY`.
    """
    if not maximo:
        return False
    texto = str(maximo)
    digitos = "".join(c for c in texto if c.isdigit())
    if not digitos:
        return False
    if len(digitos) >= 4:
        candidatos = [digitos[:4], digitos[-4:]]
        for cand in candidatos:
            try:
                ano = int(cand)
                if 2000 <= ano <= 2100 and ano >= 2024:
                    return True
            except ValueError:
                continue
    return False


def _classificar(linhas: int, min_v: Any, max_v: Any, exige_freshness: bool) -> str:
    if linhas == 0:
        return "vazio"
    if linhas < 1000:
        return "parcial"
    if exige_freshness and not _competencia_recente(max_v):
        return "parcial"
    return "ok"


async def listar_cobertura() -> list[dict[str, Any]]:
    """Retorna a lista de datasets com MIN/MAX/COUNT lidos do banco."""
    resultado: list[dict[str, Any]] = []
    async with SessionLocal() as session:
        for d in DATASETS:
            try:
                if d.coluna_temporal:
                    q = text(
                        f"SELECT MIN({d.coluna_temporal})::text AS minimo, "
                        f"MAX({d.coluna_temporal})::text AS maximo, "
                        f"COUNT(*) AS linhas FROM {d.tabela}"
                    )
                else:
                    q = text(
                        f"SELECT NULL::text AS minimo, NULL::text AS maximo, "
                        f"COUNT(*) AS linhas FROM {d.tabela}"
                    )
                row = (await session.execute(q)).mappings().first()
                linhas = int(row["linhas"]) if row else 0
                minimo = row["minimo"] if row else None
                maximo = row["maximo"] if row else None
                situacao = _classificar(
                    linhas, minimo, maximo, exige_freshness=d.coluna_temporal is not None
                )
            except Exception as exc:
                linhas = 0
                minimo = None
                maximo = None
                situacao = "indisponivel"
                resultado.append(
                    {
                        "dataset": d.dataset,
                        "rotulo": d.rotulo,
                        "descricao": d.descricao,
                        "tabela": d.tabela,
                        "min_competencia": None,
                        "max_competencia": None,
                        "linhas": 0,
                        "situacao": situacao,
                        "erro": str(exc)[:160],
                    }
                )
                continue

            resultado.append(
                {
                    "dataset": d.dataset,
                    "rotulo": d.rotulo,
                    "descricao": d.descricao,
                    "tabela": d.tabela,
                    "min_competencia": minimo,
                    "max_competencia": maximo,
                    "linhas": linhas,
                    "situacao": situacao,
                }
            )
    return resultado
