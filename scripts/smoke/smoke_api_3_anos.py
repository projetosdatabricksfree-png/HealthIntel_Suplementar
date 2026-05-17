#!/usr/bin/env python3
"""Smoke de cobertura temporal de 3 anos da API Core ANS."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from api.app.services.cobertura_temporal import endpoint_por_rota  # noqa: E402


def headers(api_key: str | None) -> dict[str, str]:
    return {"X-API-Key": api_key} if api_key else {}


def normalizar_path(path: str, amostras: dict[str, str]) -> str:
    return (
        path.replace("{registro_ans}", amostras["registro_ans"])
        .replace("{cd_municipio}", amostras["cd_municipio"])
        .replace("{sg_uf}", amostras["sg_uf"])
    )


def descobrir_amostras(client: httpx.Client, api_key: str | None) -> dict[str, str]:
    amostras = {
        "registro_ans": os.getenv("HEALTHINTEL_SMOKE_REGISTRO_ANS", "000001"),
        "cd_municipio": os.getenv("HEALTHINTEL_SMOKE_CD_MUNICIPIO", "3550308"),
        "sg_uf": os.getenv("HEALTHINTEL_SMOKE_SG_UF", "SP"),
    }
    try:
        resp = client.get("/v1/operadoras", headers=headers(api_key), params={"page": 1, "per_page": 1})
        if resp.status_code == 200:
            dados = resp.json().get("dados") or []
            if dados and dados[0].get("registro_ans"):
                amostras["registro_ans"] = str(dados[0]["registro_ans"]).zfill(6)
    except Exception:
        pass
    return amostras


def params_filtro_temporal(janela: dict[str, Any]) -> dict[str, Any]:
    tipo = janela.get("tipo")
    inicio = janela.get("inicio")
    fim = janela.get("fim")
    if not inicio or not fim:
        return {}
    if tipo in {"mensal", "snapshot_vigente"}:
        return {"competencia_inicio": inicio, "competencia_fim": fim}
    if tipo == "trimestral":
        return {"trimestre_inicio": inicio, "trimestre_fim": fim}
    if tipo == "anual":
        return {"ano_inicio": inicio, "ano_fim": fim}
    return {}


def endpoint_disponivel(item: dict[str, Any]) -> bool:
    return bool(item.get("aparece_catalogo_publico")) or item.get("status_publicacao") == "disponivel"


def validar_payload(payload: dict[str, Any], item: dict[str, Any]) -> list[str]:
    erros: list[str] = []
    if not isinstance(payload.get("dados"), list):
        erros.append("envelope sem lista dados")
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        erros.append("envelope sem meta")
        return erros
    if int(meta.get("total") or 0) <= 0:
        erros.append("meta.total <= 0 para endpoint disponivel")
    if item.get("endpoint_temporal"):
        janela = meta.get("janela_temporal")
        if not isinstance(janela, dict):
            erros.append("meta.janela_temporal ausente")
        elif janela.get("status_cobertura") != "ok_3_anos":
            erros.append(f"status_cobertura invalido: {janela.get('status_cobertura')}")
    if item.get("tipo_granularidade_temporal") == "snapshot_vigente":
        janela = meta.get("janela_temporal")
        if not isinstance(janela, dict) or janela.get("status_cobertura") != "snapshot_vigente":
            erros.append("snapshot sem janela_temporal snapshot_vigente")
    return erros


def executar(base_url: str, api_key: str | None) -> tuple[list[dict[str, Any]], int]:
    mapa = endpoint_por_rota()
    resultados: list[dict[str, Any]] = []
    falhas = 0
    with httpx.Client(base_url=base_url.rstrip("/"), timeout=30) as client:
        amostras = descobrir_amostras(client, api_key)
        meta_resp = client.get("/v1/meta/endpoints", headers=headers(api_key))
        if meta_resp.status_code != 200:
            return [
                {
                    "endpoint": "/v1/meta/endpoints",
                    "resultado": "falha",
                    "erro": f"HTTP {meta_resp.status_code}",
                }
            ], 1
        endpoints = meta_resp.json().get("dados") or []
        for item in endpoints:
            path = item.get("path") or item.get("rota")
            if not path or path not in mapa:
                continue
            disponivel = endpoint_disponivel(item)
            if not disponivel:
                resultados.append(
                    {
                        "endpoint": path,
                        "status_publicacao": item.get("status_publicacao"),
                        "resultado": "roadmap_ou_parcial_ok",
                    }
                )
                continue

            url = normalizar_path(path, amostras)
            params = {"page": 1, "per_page": 1, "pagina": 1, "por_pagina": 1}
            resp = client.get(url, headers=headers(api_key), params=params)
            erros: list[str] = []
            if resp.status_code != 200:
                erros.append(f"HTTP {resp.status_code}")
                payload: dict[str, Any] = {}
            else:
                try:
                    payload = resp.json()
                except Exception as exc:
                    payload = {}
                    erros.append(f"JSON invalido: {exc}")
            if payload:
                erros.extend(validar_payload(payload, item))
                janela = payload.get("meta", {}).get("janela_temporal") or {}
                filtro = params_filtro_temporal(janela)
                if filtro and item.get("endpoint_temporal"):
                    filtro_resp = client.get(url, headers=headers(api_key), params={**params, **filtro})
                    if filtro_resp.status_code != 200:
                        erros.append(f"filtro temporal HTTP {filtro_resp.status_code}")
                    else:
                        try:
                            filtro_payload = filtro_resp.json()
                            if "dados" not in filtro_payload or "meta" not in filtro_payload:
                                erros.append("filtro temporal sem envelope")
                        except Exception as exc:
                            erros.append(f"filtro temporal JSON invalido: {exc}")

            resultado = "ok" if not erros else "falha"
            if erros:
                falhas += 1
            resultados.append(
                {
                    "endpoint": path,
                    "url_testada": url,
                    "status_publicacao": item.get("status_publicacao"),
                    "status_cobertura_3_anos": item.get("status_cobertura_3_anos"),
                    "resultado": resultado,
                    "erros": erros,
                }
            )
    return resultados, falhas


def escrever_markdown(path: Path, resultados: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        "# Smoke API 3 anos",
        "",
        f"- Gerado em: {datetime.now(timezone.utc).isoformat()}",
        f"- Endpoints avaliados: {len(resultados)}",
        "",
        "| endpoint | status | resultado | erros |",
        "|---|---|---|---|",
    ]
    for item in resultados:
        linhas.append(
            "| `{}` | {} | **{}** | {} |".format(
                item.get("endpoint"),
                item.get("status_publicacao") or "",
                item.get("resultado"),
                "; ".join(item.get("erros") or []),
            )
        )
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("HEALTHINTEL_API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--api-key", default=os.getenv("HEALTHINTEL_API_KEY"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    resultados, falhas = executar(args.base_url, args.api_key)
    payload = {"gerado_em": datetime.now(timezone.utc).isoformat(), "resultados": resultados}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.md_out:
        escrever_markdown(args.md_out, resultados)
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
