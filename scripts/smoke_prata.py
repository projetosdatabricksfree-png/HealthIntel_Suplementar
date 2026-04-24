from __future__ import annotations

import asyncio

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.main import app
from api.app.middleware.autenticacao import validar_api_key

CHAVE_ID = "00000000-0000-4000-8000-000000000101"
CLIENTE_ID = "00000000-0000-4000-8000-000000000102"
PLANO_ID = "00000000-0000-4000-8000-000000000103"


async def _fake_auth(request: Request, x_api_key: str | None = None):
    request.state.chave_api_id = CHAVE_ID
    request.state.cliente_id = CLIENTE_ID
    request.state.plano_id = PLANO_ID
    request.state.limite_rpm = 1000
    request.state.endpoint_permitido = ["/v1"]
    request.state.camadas_permitidas = ["prata", "ouro", "bronze"]
    return x_api_key or "prata_smoke_key"


ENDPOINTS = [
    "/v1/prata/cadop?competencia=202501",
    "/v1/prata/sib/operadora?competencia=202501",
    "/v1/prata/sib/municipio?competencia=202501",
    "/v1/prata/igr?competencia=2025T1",
    "/v1/prata/nip?competencia=2025T1",
    "/v1/prata/idss?competencia=2024",
    "/v1/prata/diops?competencia=2025T1",
    "/v1/prata/fip?competencia=2025T1",
    "/v1/prata/vda?competencia=202501",
    "/v1/prata/glosa?competencia=202501",
    "/v1/prata/rede-assistencial?competencia=202501",
    "/v1/prata/operadora/enriquecida?competencia=202501",
    "/v1/prata/municipio/metrica?competencia=202501",
    "/v1/prata/financeiro/periodo?competencia=2025T1",
    "/v1/prata/cnes/municipio?competencia=202501",
    "/v1/prata/cnes/rede-gap?competencia=202501",
    "/v1/prata/tiss/procedimento?competencia=2025T1",
]


async def _preparar_credencial_smoke() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.plano (
                    id, nome, limite_rpm, endpoint_permitido, status, camadas_permitidas
                ) values (
                    :plano_id,
                    'plano_prata_smoke',
                    1000,
                    array['/v1'],
                    'ativo',
                    array['prata', 'ouro', 'bronze']
                )
                on conflict (id) do nothing
                """
            ),
            {"plano_id": PLANO_ID},
        )
        await session.execute(
            text(
                """
                insert into plataforma.cliente (
                    id, nome, email, status, plano_id
                ) values (
                    :cliente_id,
                    'Cliente Smoke Prata',
                    'smoke-prata@healthintel.local',
                    'ativo',
                    :plano_id
                )
                on conflict (id) do nothing
                """
            ),
            {"cliente_id": CLIENTE_ID, "plano_id": PLANO_ID},
        )
        await session.execute(
            text(
                """
                insert into plataforma.chave_api (
                    id, cliente_id, plano_id, hash_chave, prefixo_chave, status
                ) values (
                    :chave_id,
                    :cliente_id,
                    :plano_id,
                    repeat('a', 64),
                    'smokeprata',
                    'ativa'
                )
                on conflict (id) do nothing
                """
            ),
            {"chave_id": CHAVE_ID, "cliente_id": CLIENTE_ID, "plano_id": PLANO_ID},
        )
        await session.commit()


def main() -> None:
    asyncio.run(_preparar_credencial_smoke())
    app.dependency_overrides[validar_api_key] = _fake_auth
    try:
        client = TestClient(app)
        headers = {"X-API-Key": "prata_smoke_key"}
        falhas: list[dict[str, object]] = []
        for endpoint in ENDPOINTS:
            response = client.get(endpoint, headers=headers)
            if response.status_code != 200:
                falhas.append({"endpoint": endpoint, "status_code": response.status_code})
                continue
            payload = response.json()
            if "qualidade" not in payload.get("meta", {}):
                falhas.append({"endpoint": endpoint, "erro": "meta.qualidade ausente"})
    finally:
        app.dependency_overrides.clear()
    if falhas:
        raise SystemExit(f"Smoke Prata falhou: {falhas}")
    print({"status": "ok", "endpoints": len(ENDPOINTS)})


if __name__ == "__main__":
    main()
