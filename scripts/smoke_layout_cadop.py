"""Smoke: valida que o layout CADOP está ativo no mongo_layout_service
e que o alias REGISTRO_OPERADORA -> registro_ans está presente.

Uso:
  LAYOUT_SERVICE_TOKEN=<token> python scripts/smoke_layout_cadop.py
  make smoke-layout-cadop
"""
from __future__ import annotations

import os
import sys

import httpx

BASE_URL = os.getenv("LAYOUT_SERVICE_BASE_URL", "http://localhost:8001")
TOKEN = os.getenv("LAYOUT_SERVICE_TOKEN", "healthintel_layout_service_local_token_2026")
DATASET = os.getenv("SMOKE_CADOP_DATASET", "cadop")
ALIAS_ESPERADO_DE = os.getenv("SMOKE_CADOP_ALIAS_DE", "REGISTRO_OPERADORA")
ALIAS_ESPERADO_PARA = os.getenv("SMOKE_CADOP_ALIAS_PARA", "registro_ans")

headers = {"X-Service-Token": TOKEN}
falhas: list[str] = []


def _fail(msg: str) -> None:
    falhas.append(msg)
    print(f"[smoke_layout_cadop] FAIL: {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"[smoke_layout_cadop] OK: {msg}")


with httpx.Client(base_url=BASE_URL, headers=headers, timeout=10.0) as client:
    # 1. Listar datasets e confirmar que cadop existe
    resp = client.get("/layout/datasets")
    if resp.status_code != 200:
        _fail(f"GET /layout/datasets retornou {resp.status_code}")
    else:
        datasets = {d.get("codigo") for d in resp.json()} if isinstance(resp.json(), list) else set()
        if DATASET not in datasets:
            _fail(f"dataset '{DATASET}' ausente em /layout/datasets (encontrados: {sorted(datasets)})")
        else:
            _ok(f"dataset '{DATASET}' presente")

    # 2. Buscar layout ativo para cadop
    resp2 = client.get("/layout/layouts", params={"dataset_codigo": DATASET})
    if resp2.status_code != 200:
        _fail(f"GET /layout/layouts?dataset_codigo={DATASET} retornou {resp2.status_code}")
    else:
        layouts = resp2.json() if isinstance(resp2.json(), list) else []
        ativos = [l for l in layouts if l.get("status") == "ativo"]
        if not ativos:
            _fail(f"nenhum layout com status='ativo' para dataset '{DATASET}'")
        else:
            layout = ativos[0]
            layout_id = layout.get("id") or layout.get("_id")
            _ok(f"layout ativo encontrado: id={layout_id}")

            # 3. Verificar alias REGISTRO_OPERADORA -> registro_ans
            aliases = layout.get("aliases", {})
            # aliases pode ser dict {de: para} ou list de {de, para}
            alias_encontrado = False
            if isinstance(aliases, dict):
                alias_encontrado = aliases.get(ALIAS_ESPERADO_DE) == ALIAS_ESPERADO_PARA
            elif isinstance(aliases, list):
                alias_encontrado = any(
                    a.get("de") == ALIAS_ESPERADO_DE and a.get("para") == ALIAS_ESPERADO_PARA
                    for a in aliases
                )

            if not alias_encontrado:
                # Tentar endpoint dedicado de aliases
                resp3 = client.get(f"/layout/layouts/{layout_id}/aliases")
                if resp3.status_code == 200:
                    alias_data = resp3.json()
                    if isinstance(alias_data, dict):
                        alias_encontrado = alias_data.get(ALIAS_ESPERADO_DE) == ALIAS_ESPERADO_PARA
                    elif isinstance(alias_data, list):
                        alias_encontrado = any(
                            a.get("de") == ALIAS_ESPERADO_DE and a.get("para") == ALIAS_ESPERADO_PARA
                            for a in alias_data
                        )

            if alias_encontrado:
                _ok(f"alias '{ALIAS_ESPERADO_DE}' -> '{ALIAS_ESPERADO_PARA}' presente")
            else:
                _fail(
                    f"alias '{ALIAS_ESPERADO_DE}' -> '{ALIAS_ESPERADO_PARA}' ausente. "
                    f"Executar: make bootstrap-cadop-layouts"
                )

print(f"\n[smoke_layout_cadop] resultado: {len(falhas)} falha(s)")
if falhas:
    sys.exit(1)
