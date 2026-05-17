from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

try:
    from sqlalchemy import text
    from api.app.core.database import SessionLocal
except ModuleNotFoundError:  # permite uso das regras por scripts sem venv da API
    text = None
    SessionLocal = None

REPO = Path(__file__).resolve().parents[3]
MAPA_COBERTURA = REPO / "docs/catalogo_dados/api_core_ans/mapa_endpoint_fonte_3_anos.yml"

STATUS_OK = "ok_3_anos"
STATUS_PARCIAL = "parcial"
STATUS_VAZIO = "vazio"
STATUS_SNAPSHOT = "snapshot_vigente"
STATUS_NAO_TEMPORAL = "nao_temporal"
STATUS_FORA_ESCOPO = "fora_do_escopo"


def _identificador(valor: str) -> str:
    if not valor or not valor.replace("_", "").isalnum():
        raise ValueError(f"Identificador inseguro: {valor!r}")
    return valor


def relacao_segura(schema: str, tabela: str) -> str:
    return f"{_identificador(schema)}.{_identificador(tabela)}"


def coluna_segura(coluna: str) -> str:
    return _identificador(coluna)


@lru_cache(maxsize=1)
def carregar_mapa_cobertura() -> dict[str, Any]:
    with MAPA_COBERTURA.open(encoding="utf-8") as arquivo:
        return yaml.safe_load(arquivo) or {}


def endpoints_cobertura() -> list[dict[str, Any]]:
    return list(carregar_mapa_cobertura().get("endpoints", []))


def endpoint_por_rota() -> dict[str, dict[str, Any]]:
    return {item["endpoint"]: item for item in endpoints_cobertura()}


def dataset_por_nome() -> dict[str, dict[str, Any]]:
    return {item["nome_dataset"]: item for item in endpoints_cobertura()}


def cobertura_por_fonte() -> dict[str, dict[str, Any]]:
    fontes: dict[str, dict[str, Any]] = {}
    for item in endpoints_cobertura():
        fonte = f"{item['schema_origem']}.{item['tabela_origem']}"
        fontes.setdefault(fonte, item)
    return fontes


def parse_competencia(valor: Any) -> tuple[int, str, int] | None:
    texto = str(valor or "").strip()
    if not re.fullmatch(r"\d{6}", texto):
        return None
    ano = int(texto[:4])
    mes = int(texto[4:6])
    if mes < 1 or mes > 12:
        return None
    return ano * 12 + mes, texto, ano


def parse_ano(valor: Any) -> tuple[int, str, int] | None:
    texto = str(valor or "").strip()
    if not re.fullmatch(r"\d{4}", texto):
        return None
    ano = int(texto)
    return ano, texto, ano


def parse_trimestre(valor: Any) -> tuple[int, str, int] | None:
    texto = str(valor or "").strip().upper()
    match = re.fullmatch(r"([1-4])T(\d{4})", texto)
    if match:
        trimestre = int(match.group(1))
        ano = int(match.group(2))
        return ano * 4 + trimestre, f"{trimestre}T{ano}", ano
    match = re.fullmatch(r"(\d{4})Q([1-4])", texto)
    if match:
        ano = int(match.group(1))
        trimestre = int(match.group(2))
        return ano * 4 + trimestre, f"{trimestre}T{ano}", ano
    comp = parse_competencia(texto)
    if comp:
        _, _, ano = comp
        mes = int(texto[4:6])
        trimestre = ((mes - 1) // 3) + 1
        return ano * 4 + trimestre, f"{trimestre}T{ano}", ano
    return None


def parse_temporal(valor: Any, granularidade: str) -> tuple[int, str, int] | None:
    if granularidade == "mensal" or granularidade == "snapshot_vigente":
        return parse_competencia(valor)
    if granularidade == "trimestral":
        return parse_trimestre(valor)
    if granularidade == "anual":
        return parse_ano(valor)
    return None


def ordem_trimestre(valor: str | None) -> int | None:
    parsed = parse_trimestre(valor)
    return parsed[0] if parsed else None


def expr_ordem_trimestre(coluna: str) -> str:
    col = coluna_segura(coluna)
    valor = f"{col}::text"
    return (
        "case "
        f"when {valor} ~ '^[1-4]T[0-9]{{4}}$' "
        f"then substring({valor} from 3 for 4)::int * 4 + substring({valor} from 1 for 1)::int "
        f"when {valor} ~ '^[0-9]{{4}}Q[1-4]$' "
        f"then substring({valor} from 1 for 4)::int * 4 + substring({valor} from 6 for 1)::int "
        f"when {valor} ~ '^[0-9]{{6}}$' "
        f"then substring({valor} from 1 for 4)::int * 4 + ((substring({valor} from 5 for 2)::int - 1) / 3 + 1)::int "
        "else null end"
    )


def adicionar_filtro_mensal(
    filtros: list[str],
    params: dict[str, Any],
    coluna: str,
    *,
    competencia: Any = None,
    competencia_inicio: Any = None,
    competencia_fim: Any = None,
) -> None:
    col = coluna_segura(coluna)
    if competencia:
        params[f"{col}_competencia"] = str(competencia)
        filtros.append(f"{col}::text = :{col}_competencia")
    if competencia_inicio:
        params[f"{col}_inicio"] = str(competencia_inicio)
        filtros.append(f"{col}::text >= :{col}_inicio")
    if competencia_fim:
        params[f"{col}_fim"] = str(competencia_fim)
        filtros.append(f"{col}::text <= :{col}_fim")


def adicionar_filtro_anual(
    filtros: list[str],
    params: dict[str, Any],
    coluna: str,
    *,
    ano_base: Any = None,
    ano_inicio: Any = None,
    ano_fim: Any = None,
) -> None:
    col = coluna_segura(coluna)
    if ano_base:
        params[f"{col}_ano_base"] = int(ano_base)
        filtros.append(f"{col}::int = :{col}_ano_base")
    if ano_inicio:
        params[f"{col}_ano_inicio"] = int(ano_inicio)
        filtros.append(f"{col}::int >= :{col}_ano_inicio")
    if ano_fim:
        params[f"{col}_ano_fim"] = int(ano_fim)
        filtros.append(f"{col}::int <= :{col}_ano_fim")


def adicionar_filtro_trimestral(
    filtros: list[str],
    params: dict[str, Any],
    coluna: str,
    *,
    trimestre: Any = None,
    trimestre_inicio: Any = None,
    trimestre_fim: Any = None,
) -> None:
    expr = expr_ordem_trimestre(coluna)
    if trimestre:
        ordem = ordem_trimestre(str(trimestre))
        if ordem is not None:
            params[f"{coluna}_trimestre"] = ordem
            filtros.append(f"{expr} = :{coluna}_trimestre")
    if trimestre_inicio:
        ordem = ordem_trimestre(str(trimestre_inicio))
        if ordem is not None:
            params[f"{coluna}_trimestre_inicio"] = ordem
            filtros.append(f"{expr} >= :{coluna}_trimestre_inicio")
    if trimestre_fim:
        ordem = ordem_trimestre(str(trimestre_fim))
        if ordem is not None:
            params[f"{coluna}_trimestre_fim"] = ordem
            filtros.append(f"{expr} <= :{coluna}_trimestre_fim")


def calcular_resumo_cobertura(item: dict[str, Any], total: int, valores: list[Any]) -> dict[str, Any]:
    granularidade = item.get("granularidade_temporal") or "nao_temporal"
    parsed = [
        parse_temporal(valor, granularidade)
        for valor in valores
        if valor is not None and str(valor).strip() != ""
    ]
    parsed = [valor for valor in parsed if valor is not None]
    distintos = sorted({valor[0]: valor for valor in parsed}.values(), key=lambda item: item[0])
    anos = sorted({valor[2] for valor in distintos})

    qtd_competencias = len(distintos) if granularidade in {"mensal", "snapshot_vigente"} else 0
    qtd_trimestres = len(distintos) if granularidade == "trimestral" else 0
    qtd_anos = len(distintos) if granularidade == "anual" else len(anos)
    menor = distintos[0][1] if distintos else None
    maior = distintos[-1][1] if distintos else None

    if granularidade == "fora_do_escopo":
        status = STATUS_FORA_ESCOPO
        motivo = "Endpoint fora do escopo da sprint."
    elif granularidade == "nao_temporal":
        status = STATUS_NAO_TEMPORAL
        motivo = "Endpoint sem dimensao temporal historica."
    elif granularidade == "snapshot_vigente":
        status = STATUS_SNAPSHOT if total > 0 else STATUS_VAZIO
        motivo = "Snapshot vigente nao exige 3 anos." if total > 0 else "Tabela snapshot sem linhas."
    elif total <= 0:
        status = STATUS_VAZIO
        motivo = "Tabela origem sem linhas reais."
    elif granularidade == "mensal" and qtd_competencias >= 36:
        status = STATUS_OK
        motivo = "Cobertura mensal possui pelo menos 36 competencias distintas."
    elif granularidade == "trimestral" and qtd_trimestres >= 12:
        status = STATUS_OK
        motivo = "Cobertura trimestral possui pelo menos 12 trimestres distintos."
    elif granularidade == "anual" and qtd_anos >= 3:
        status = STATUS_OK
        motivo = "Cobertura anual possui pelo menos 3 anos-base distintos."
    else:
        status = STATUS_PARCIAL
        motivo = "Cobertura temporal inferior ao minimo comercial de 3 anos."

    acao = "nenhuma"
    if status == STATUS_PARCIAL:
        acao = "executar backfill real ou ocultar como disponivel no catalogo publico"
    elif status == STATUS_VAZIO:
        acao = "manter roadmap/fora do catalogo disponivel ate carga real produzir linhas"

    return {
        "endpoint": item.get("endpoint"),
        "tabela_origem": item.get("tabela_origem"),
        "schema_origem": item.get("schema_origem"),
        "coluna_temporal": item.get("coluna_temporal"),
        "granularidade_temporal": granularidade,
        "total_linhas": total,
        "menor_competencia": menor if granularidade in {"mensal", "snapshot_vigente"} else None,
        "maior_competencia": maior if granularidade in {"mensal", "snapshot_vigente"} else None,
        "qtd_competencias": qtd_competencias,
        "menor_trimestre": menor if granularidade == "trimestral" else None,
        "maior_trimestre": maior if granularidade == "trimestral" else None,
        "qtd_trimestres": qtd_trimestres,
        "menor_ano": menor if granularidade == "anual" else (min(anos) if anos else None),
        "maior_ano": maior if granularidade == "anual" else (max(anos) if anos else None),
        "qtd_anos": qtd_anos,
        "anos_cobertos": anos,
        "status_cobertura": status,
        "motivo": motivo,
        "acao_recomendada": acao,
    }


async def auditar_item_cobertura(item: dict[str, Any]) -> dict[str, Any]:
    if text is None or SessionLocal is None:
        raise RuntimeError("SQLAlchemy indisponivel para auditar cobertura via API.")
    relacao = relacao_segura(item["schema_origem"], item["tabela_origem"])
    coluna = coluna_segura(item["coluna_temporal"])
    async with SessionLocal() as session:
        existe = await session.execute(text("select to_regclass(:relacao)"), {"relacao": relacao})
        if existe.scalar_one() is None:
            resumo = calcular_resumo_cobertura(item, 0, [])
            resumo["motivo"] = "Tabela origem nao existe no banco."
            resumo["acao_recomendada"] = "criar/publicar tabela origem ou marcar endpoint como roadmap"
            return resumo
        total = int((await session.execute(text(f"select count(*) from {relacao}"))).scalar_one())
        valores = (
            await session.execute(
                text(f"select distinct {coluna}::text as valor from {relacao} where {coluna} is not null")
            )
        ).scalars().all()
    return calcular_resumo_cobertura(item, total, list(valores))


async def auditar_endpoint(endpoint: str) -> dict[str, Any] | None:
    item = endpoint_por_rota().get(endpoint)
    if not item:
        return None
    return await auditar_item_cobertura(item)


async def janela_temporal_endpoint(endpoint: str) -> dict[str, Any] | None:
    resumo = await auditar_endpoint(endpoint)
    if not resumo:
        return None
    tipo = resumo["granularidade_temporal"]
    if tipo == "mensal" or tipo == "snapshot_vigente":
        inicio = resumo["menor_competencia"]
        fim = resumo["maior_competencia"]
        qtd = resumo["qtd_competencias"]
    elif tipo == "trimestral":
        inicio = resumo["menor_trimestre"]
        fim = resumo["maior_trimestre"]
        qtd = resumo["qtd_trimestres"]
    elif tipo == "anual":
        inicio = resumo["menor_ano"]
        fim = resumo["maior_ano"]
        qtd = resumo["qtd_anos"]
    else:
        inicio = fim = None
        qtd = 0
    return {
        "tipo": tipo,
        "inicio": inicio,
        "fim": fim,
        "qtd_competencias": resumo["qtd_competencias"],
        "qtd_trimestres": resumo["qtd_trimestres"],
        "qtd_anos": resumo["qtd_anos"],
        "qtd_periodos": qtd,
        "anos_cobertos": resumo["anos_cobertos"],
        "status_cobertura": resumo["status_cobertura"],
    }


async def anexar_janela_temporal(payload: dict[str, Any], endpoint: str) -> dict[str, Any]:
    janela = await janela_temporal_endpoint(endpoint)
    if janela:
        payload.setdefault("meta", {})["janela_temporal"] = janela
    return payload
