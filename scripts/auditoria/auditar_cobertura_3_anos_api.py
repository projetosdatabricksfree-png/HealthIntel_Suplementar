#!/usr/bin/env python3
"""Audita cobertura temporal de 3 anos dos endpoints Core ANS.

Uso:
    python scripts/auditoria/auditar_cobertura_3_anos_api.py \
        --json-out docs/evidencias/release_0_9/cobertura_3_anos_api.json \
        --md-out docs/evidencias/release_0_9/cobertura_3_anos_api.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from api.app.services.cobertura_temporal import (  # noqa: E402
    calcular_resumo_cobertura,
    endpoints_cobertura,
    relacao_segura,
)

DOCKER_COMPOSE = REPO / "infra/docker-compose.yml"


def psql(sql: str) -> str:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE),
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "healthintel",
        "-d",
        "healthintel",
        "-A",
        "-t",
        "-q",
        "-P",
        "pager=off",
        "-c",
        sql,
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
    return resultado.stdout.strip()


def auditar_item(item: dict[str, Any]) -> dict[str, Any]:
    relacao = relacao_segura(item["schema_origem"], item["tabela_origem"])
    coluna = item["coluna_temporal"]
    existe = psql(f"select to_regclass('{relacao}') is not null;").lower() == "t"
    if not existe:
        resumo = calcular_resumo_cobertura(item, 0, [])
        resumo["motivo"] = "Tabela origem nao existe no banco."
        resumo["acao_recomendada"] = "criar/publicar tabela origem ou marcar endpoint como roadmap"
        return resumo

    total = int(psql(f"select count(*) from {relacao};") or "0")
    valores_raw = psql(
        f"select distinct {coluna}::text from {relacao} where {coluna} is not null order by 1;"
    )
    valores = [linha for linha in valores_raw.splitlines() if linha.strip()]
    resumo = calcular_resumo_cobertura(item, total, valores)
    resumo["status_publicacao_mapa"] = item.get("status_publicacao")
    resumo["nome_dataset"] = item.get("nome_dataset")
    resumo["regra_3_anos"] = item.get("regra_3_anos")
    resumo["exige_backfill"] = bool(item.get("exige_backfill"))
    resumo["observacao"] = item.get("observacao")
    return resumo


def auditar() -> list[dict[str, Any]]:
    return [auditar_item(item) for item in endpoints_cobertura()]


def escrever_markdown(path: Path, resultados: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    por_status: dict[str, int] = {}
    for item in resultados:
        por_status[item["status_cobertura"]] = por_status.get(item["status_cobertura"], 0) + 1

    linhas = [
        "# Auditoria de cobertura 3 anos - API Core ANS",
        "",
        f"- Gerado em: {datetime.now(timezone.utc).isoformat()}",
        f"- Endpoints auditados: {len(resultados)}",
        "",
        "## Resumo",
        "",
        "| status | endpoints |",
        "|---|---:|",
    ]
    for status, total in sorted(por_status.items()):
        linhas.append(f"| {status} | {total} |")

    linhas.extend(
        [
            "",
            "## Cobertura por endpoint",
            "",
            "| endpoint | fonte | granularidade | linhas | inicio | fim | periodos | status | acao |",
            "|---|---|---|---:|---|---|---:|---|---|",
        ]
    )
    for item in resultados:
        inicio = (
            item["menor_competencia"]
            or item["menor_trimestre"]
            or item["menor_ano"]
            or ""
        )
        fim = item["maior_competencia"] or item["maior_trimestre"] or item["maior_ano"] or ""
        periodos = (
            item["qtd_competencias"]
            or item["qtd_trimestres"]
            or item["qtd_anos"]
            or 0
        )
        fonte = f"{item['schema_origem']}.{item['tabela_origem']}.{item['coluna_temporal']}"
        linhas.append(
            "| `{endpoint}` | `{fonte}` | {gran} | {linhas} | {inicio} | {fim} | "
            "{periodos} | **{status}** | {acao} |".format(
                endpoint=item["endpoint"],
                fonte=fonte,
                gran=item["granularidade_temporal"],
                linhas=item["total_linhas"],
                inicio=inicio,
                fim=fim,
                periodos=periodos,
                status=item["status_cobertura"],
                acao=item["acao_recomendada"],
            )
        )
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument(
        "--permitir-parcial",
        action="store_true",
        help="Nao falha se endpoints mapeados como disponivel estiverem parciais/vazios.",
    )
    args = parser.parse_args()

    resultados = auditar()
    payload = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "resultados": resultados,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.md_out:
        escrever_markdown(args.md_out, resultados)

    bloqueios = [
        item
        for item in resultados
        if item.get("status_publicacao_mapa") == "disponivel"
        and item["status_cobertura"] not in {"ok_3_anos", "snapshot_vigente", "nao_temporal"}
    ]
    if bloqueios and not args.permitir_parcial:
        print("FALHA cobertura 3 anos: endpoints disponiveis sem cobertura minima", file=sys.stderr)
        for item in bloqueios:
            print(f"- {item['endpoint']}: {item['status_cobertura']} ({item['motivo']})", file=sys.stderr)
        return 1
    print("SUCESSO auditoria cobertura 3 anos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
