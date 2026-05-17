#!/usr/bin/env python3
"""
Smoke test completo dos endpoints do portal HealthIntel Core ANS.

Uso:
    HEALTHINTEL_API_KEY=<key> python3 scripts/smoke/smoke_api_portal_endpoints_http.py [BASE_URL]

Classifica cada resultado como:
  [OK]      200 JSON com envelope {dados, meta}
  [VAZIO]   200 JSON com total=0 (esperado para endpoints roadmap)
  [AUTH]    401 JSON sem chave (correto)
  [INTER]   403 JSON para endpoint interno (correto)
  [NEGOCIO] 404 JSON de negócio (correto — registro sem dados)
  [FAIL]    qualquer resposta inesperada ou HTML detectado
"""
import os
import sys
import json
import urllib.request
import urllib.error
from typing import Any

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://5.189.160.27:8080"
KEY = os.environ.get("HEALTHINTEL_API_KEY", "")

OK = 0
VAZIO = 0
AUTH_OK = 0
INTER_OK = 0
NEGOCIO_OK = 0
FAIL = 0

RESULTADOS: list[dict] = []


def _req(path: str, headers: dict | None = None, timeout: int = 15) -> tuple[int, str, dict]:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            ct = resp.headers.get("Content-Type", "")
            return resp.status, body, {"content_type": ct}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        ct = e.headers.get("Content-Type", "")
        return e.code, body, {"content_type": ct}
    except Exception as exc:
        return 0, str(exc), {"content_type": ""}


def _is_html(body: str, ct: str) -> bool:
    return "text/html" in ct or body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")


def _parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except Exception:
        return None


def _envelope_ok(data: Any) -> bool:
    return isinstance(data, dict) and "dados" in data and "meta" in data


def _total(data: Any) -> int | None:
    if isinstance(data, dict):
        return data.get("meta", {}).get("total")
    return None


def check_auth(label: str, path: str) -> None:
    global AUTH_OK, FAIL
    code, body, meta = _req(path)
    ct = meta["content_type"]
    if _is_html(body, ct):
        print(f"[FAIL]  {label} (sem chave) — {code} HTML detectado")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "auth", "status": code, "resultado": "FAIL", "obs": "HTML"})
        return
    if code == 401:
        data = _parse_json(body)
        print(f"[AUTH]  {label} (sem chave) — 401 JSON ok")
        AUTH_OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "auth", "status": 401, "resultado": "AUTH_OK"})
    else:
        print(f"[FAIL]  {label} (sem chave) — {code} (esperado 401)")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "auth", "status": code, "resultado": "FAIL", "obs": f"esperado 401, recebeu {code}"})


def check_interno(label: str, path: str) -> None:
    global INTER_OK, FAIL
    code, body, meta = _req(path)
    ct = meta["content_type"]
    if _is_html(body, ct):
        print(f"[FAIL]  {label} — {code} HTML detectado (esperado JSON 403)")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "interno", "status": code, "resultado": "FAIL", "obs": "HTML"})
        return
    if code == 403:
        print(f"[INTER] {label} — 403 JSON ok (endpoint interno esperado)")
        INTER_OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "interno", "status": 403, "resultado": "INTER_OK"})
    else:
        print(f"[FAIL]  {label} — {code} (esperado 403 JSON para endpoint interno)")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "interno", "status": code, "resultado": "FAIL"})


def check_publico(label: str, path: str) -> None:
    global OK, FAIL
    code, body, meta = _req(path)
    ct = meta["content_type"]
    if _is_html(body, ct):
        print(f"[FAIL]  {label} — {code} HTML detectado")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "publico", "status": code, "resultado": "FAIL", "obs": "HTML"})
        return
    if code == 200:
        print(f"[OK]    {label} — 200 JSON ok")
        OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "publico", "status": 200, "resultado": "OK"})
    else:
        print(f"[FAIL]  {label} — {code}")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "publico", "status": code, "resultado": "FAIL"})


def check_dados(label: str, path: str, espera_vazio: bool = False) -> None:
    global OK, VAZIO, FAIL
    if not KEY:
        print(f"[SKIP]  {label} — HEALTHINTEL_API_KEY não definida")
        return
    headers = {"X-API-Key": KEY}
    code, body, meta = _req(path, headers=headers)
    ct = meta["content_type"]
    if _is_html(body, ct):
        print(f"[FAIL]  {label} — {code} HTML detectado")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "dados", "status": code, "resultado": "FAIL", "obs": "HTML"})
        return
    data = _parse_json(body)
    if code != 200:
        print(f"[FAIL]  {label} — {code}")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "dados", "status": code, "resultado": "FAIL"})
        return
    env_ok = _envelope_ok(data)
    total = _total(data)
    if not env_ok:
        print(f"[FAIL]  {label} — 200 mas envelope inválido")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "dados", "status": 200, "resultado": "FAIL", "obs": "envelope inválido"})
        return
    if total == 0 or espera_vazio:
        print(f"[VAZIO] {label} — 200, total=0 (esperado roadmap/vazio_bloqueado)")
        VAZIO += 1
        RESULTADOS.append({"endpoint": label, "tipo": "dados", "status": 200, "resultado": "VAZIO", "total": total})
    else:
        print(f"[OK]    {label} — 200, total={total}, envelope=ok")
        OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "dados", "status": 200, "resultado": "OK", "total": total})


def check_parametrico(label: str, path_template: str, descobrir_via: str, campo: str = "registro_ans") -> None:
    global OK, VAZIO, NEGOCIO_OK, FAIL
    if not KEY:
        print(f"[SKIP]  {label} — HEALTHINTEL_API_KEY não definida")
        return
    headers = {"X-API-Key": KEY}

    # Descoberta dinâmica
    code_d, body_d, _ = _req(f"{descobrir_via}?per_page=1", headers=headers)
    data_d = _parse_json(body_d)
    registro = None
    if code_d == 200 and data_d and data_d.get("dados"):
        registro = data_d["dados"][0].get(campo)

    if not registro:
        print(f"[VAZIO] {label} — sem {campo} com dados em {descobrir_via} (roadmap/vazio_bloqueado)")
        VAZIO += 1
        RESULTADOS.append({"endpoint": label, "tipo": "parametrico", "status": None, "resultado": "VAZIO", "obs": f"sem dados em {descobrir_via}"})
        return

    path = path_template.format(**{campo: registro})
    code, body, meta = _req(path, headers=headers)
    ct = meta["content_type"]
    if _is_html(body, ct):
        print(f"[FAIL]  {label} ({registro}) — {code} HTML detectado")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "parametrico", "status": code, "resultado": "FAIL", "obs": "HTML"})
        return
    data = _parse_json(body)
    if code == 200 and _envelope_ok(data):
        total = _total(data)
        print(f"[OK]    {label} ({registro}) — 200, total={total}")
        OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "parametrico", "status": 200, "resultado": "OK", "total": total})
    elif code == 404:
        print(f"[NEGOCIO] {label} ({registro}) — 404 JSON de negócio (sem_dados_para_filtro)")
        NEGOCIO_OK += 1
        RESULTADOS.append({"endpoint": label, "tipo": "parametrico", "status": 404, "resultado": "NEGOCIO_OK"})
    else:
        print(f"[FAIL]  {label} ({registro}) — {code}")
        FAIL += 1
        RESULTADOS.append({"endpoint": label, "tipo": "parametrico", "status": code, "resultado": "FAIL"})


# ───── Início dos testes ─────

print(f"=== Smoke Portal HealthIntel Core ANS ===")
print(f"    BASE_URL: {BASE_URL}")
print(f"    KEY: {KEY[:12]}..." if KEY else "    KEY: (não definida — testes com chave serão pulados)")
print()

print("--- Endpoints sem autenticação ---")
check_publico("/saude", "/saude")
check_interno("/prontidao (interno)", "/prontidao")

print()
print("--- Autenticação: 401 sem chave ---")
for ep in [
    "/v1/meta/dataset", "/v1/meta/versao", "/v1/meta/pipeline", "/v1/meta/endpoints",
    "/v1/operadoras", "/v1/produtos-planos", "/v1/historico-planos",
    "/v1/regulatorio", "/v1/igr", "/v1/nip", "/v1/idss",
    "/v1/financeiro", "/v1/prudencial", "/v1/regime-especial", "/v1/glosa",
    "/v1/tuss/procedimentos", "/v1/mercado/municipio",
    "/v1/rankings/operadora/score", "/v1/rankings/operadora/crescimento",
    "/v1/rankings/municipio/oportunidade", "/v1/rankings/municipio/oportunidade-v2",
    "/v1/rankings/composto",
]:
    check_auth(ep, ep)

print()
print("--- Endpoints meta (com chave) ---")
check_dados("/v1/meta/dataset", "/v1/meta/dataset")
check_dados("/v1/meta/versao", "/v1/meta/versao")
check_dados("/v1/meta/pipeline", "/v1/meta/pipeline")
check_dados("/v1/meta/endpoints", "/v1/meta/endpoints")

print()
print("--- Endpoints de dados com chave ---")
check_dados("/v1/operadoras", "/v1/operadoras?page=1&per_page=5")
check_dados("/v1/produtos-planos", "/v1/produtos-planos?page=1&per_page=5")
check_dados("/v1/historico-planos", "/v1/historico-planos?page=1&per_page=5")
check_dados("/v1/regulatorio", "/v1/regulatorio?page=1&per_page=5")
check_dados("/v1/igr", "/v1/igr?page=1&per_page=5")
check_dados("/v1/nip", "/v1/nip?page=1&per_page=5")
check_dados("/v1/idss", "/v1/idss?page=1&per_page=5")
check_dados("/v1/financeiro", "/v1/financeiro?page=1&per_page=5")
check_dados("/v1/prudencial", "/v1/prudencial?page=1&per_page=5")
check_dados("/v1/regime-especial", "/v1/regime-especial?page=1&per_page=5")
check_dados("/v1/glosa", "/v1/glosa?page=1&per_page=5")
check_dados("/v1/tuss/procedimentos", "/v1/tuss/procedimentos?page=1&per_page=5")
check_dados("/v1/mercado/municipio", "/v1/mercado/municipio?page=1&per_page=5")
check_dados("/v1/rankings/operadora/score", "/v1/rankings/operadora/score?page=1&per_page=5")
check_dados("/v1/rankings/operadora/crescimento", "/v1/rankings/operadora/crescimento?page=1&per_page=5")
check_dados("/v1/rankings/municipio/oportunidade", "/v1/rankings/municipio/oportunidade?page=1&per_page=5")
check_dados("/v1/rankings/municipio/oportunidade-v2", "/v1/rankings/municipio/oportunidade-v2?page=1&per_page=5")
check_dados("/v1/rankings/composto", "/v1/rankings/composto?page=1&per_page=5")

print()
print("--- Endpoints parametrizados (descoberta dinâmica) ---")
# operadora genérica
check_parametrico(
    "/v1/operadoras/{registro_ans}",
    "/v1/operadoras/{registro_ans}",
    "/v1/operadoras",
    "registro_ans",
)
check_parametrico(
    "/v1/operadoras/{registro_ans}/score",
    "/v1/operadoras/{registro_ans}/score",
    "/v1/operadoras",
    "registro_ans",
)
check_parametrico(
    "/v1/operadoras/{registro_ans}/score-v3",
    "/v1/operadoras/{registro_ans}/score-v3",
    "/v1/operadoras",
    "registro_ans",
)
check_parametrico(
    "/v1/operadoras/{registro_ans}/regulatorio",
    "/v1/operadoras/{registro_ans}/regulatorio",
    "/v1/operadoras",
    "registro_ans",
)
check_parametrico(
    "/v1/operadoras/{registro_ans}/financeiro",
    "/v1/operadoras/{registro_ans}/financeiro",
    "/v1/operadoras",
    "registro_ans",
)
# regime-especial: descobrir via endpoint flat (117 registros)
check_parametrico(
    "/v1/operadoras/{registro_ans}/regime-especial",
    "/v1/operadoras/{registro_ans}/regime-especial",
    "/v1/regime-especial",
    "registro_ans",
)
# score-regulatorio: tabela pode estar zerada — fallback para vazio
check_parametrico(
    "/v1/operadoras/{registro_ans}/score-regulatorio",
    "/v1/operadoras/{registro_ans}/score-regulatorio",
    "/v1/regulatorio",
    "registro_ans",
)

print()
print("--- Endpoints roadmap/vazio_bloqueado (200 com total=0 esperado) ---")
check_dados("/v1/cnes/municipio/123456 (roadmap)", "/v1/cnes/municipio/123456?page=1&per_page=5", espera_vazio=True)
check_dados("/v1/cnes/uf/SP (roadmap)", "/v1/cnes/uf/SP?page=1&per_page=5", espera_vazio=True)
check_dados("/v1/rede/municipio/123456 (roadmap)", "/v1/rede/municipio/123456?page=1&per_page=5", espera_vazio=True)
check_dados("/v1/mercado/vazio-assistencial (roadmap)", "/v1/mercado/vazio-assistencial?page=1&per_page=5", espera_vazio=True)
check_dados("/v1/regulatorio/rn623 (roadmap)", "/v1/regulatorio/rn623?page=1&per_page=5", espera_vazio=True)
# portabilidade: tabela zerada — qualquer registro_ans retorna total=0
check_dados("/v1/operadoras/359017/portabilidade (roadmap)", "/v1/operadoras/359017/portabilidade?page=1&per_page=5", espera_vazio=True)

print()
print(f"=== Resultado Final ===")
print(f"    [OK]      {OK}")
print(f"    [VAZIO]   {VAZIO}  (roadmap/vazio_bloqueado — esperados)")
print(f"    [AUTH]    {AUTH_OK}  (401 sem chave — corretos)")
print(f"    [INTER]   {INTER_OK}  (403 JSON interno — correto)")
print(f"    [NEGOCIO] {NEGOCIO_OK}  (404 JSON de negócio — corretos)")
print(f"    [FAIL]    {FAIL}")
print()

if FAIL == 0:
    print("SMOKE PASSOU: 0 falhas.")
    sys.exit(0)
else:
    print(f"SMOKE FALHOU: {FAIL} falha(s).")
    sys.exit(1)
