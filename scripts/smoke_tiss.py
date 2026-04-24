from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key


async def _fake_auth(request=None, x_api_key: str | None = None):
    if request is not None:
        request.state.chave_api_id = "tiss_smoke"
        request.state.cliente_id = "tiss_smoke_cliente"
        request.state.plano_id = "tiss_smoke_plano"
        request.state.limite_rpm = 1000
        request.state.endpoint_permitido = ["/v1", "/admin", "/saude", "/prontidao"]
    return x_api_key or "tiss_smoke_key"


def _coletar(client: TestClient, metodo: str, url: str, **kwargs):
    response = client.request(metodo, url, **kwargs)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return {
        "url": url,
        "status_code": response.status_code,
        "ok": response.status_code < 400,
        "body": body,
    }


async def main() -> None:
    dbt_executavel = Path(".venv/bin/dbt")
    comando_base = str(dbt_executavel) if dbt_executavel.exists() else "dbt"
    env = {**os.environ, "DBT_PROFILES_DIR": str(Path("healthintel_dbt").resolve())}
    resultado_build = subprocess.run(
        [
            comando_base,
            "build",
            "--project-dir",
            "healthintel_dbt",
            "--select",
            "+tag:tiss",
            "+tag:rede",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado_build.returncode != 0:
        print(resultado_build.stdout)
        print(resultado_build.stderr)
        raise SystemExit(resultado_build.returncode)

    app.dependency_overrides[validar_api_key] = _fake_auth
    try:
        with TestClient(app) as client:
            resultados = [
                _coletar(
                    client,
                    "GET",
                    "/v1/tiss/123456/procedimentos",
                    headers={"X-API-Key": "tiss_smoke_key"},
                    params={"trimestre": "2025T1"},
                ),
                _coletar(
                    client,
                    "GET",
                    "/v1/tiss/123456/sinistralidade",
                    headers={"X-API-Key": "tiss_smoke_key"},
                    params={"trimestre": "2025T1"},
                ),
                _coletar(
                    client,
                    "GET",
                    "/v1/rede/gap/3550308",
                    headers={"X-API-Key": "tiss_smoke_key"},
                    params={"competencia": "202501"},
                ),
            ]
    finally:
        app.dependency_overrides.clear()

    falhas = [resultado for resultado in resultados if not resultado["ok"]]
    print(json.dumps({"checks": len(resultados), "falhas": len(falhas)}, ensure_ascii=False))
    for resultado in resultados:
        print(
            json.dumps(
                {"url": resultado["url"], "status_code": resultado["status_code"]},
                ensure_ascii=False,
            )
        )
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
