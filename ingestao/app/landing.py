from __future__ import annotations

import hashlib
from pathlib import Path

import httpx

from ingestao.app.config import get_settings


def caminho_landing(dataset: str, competencia: str, estado: str = "raw") -> Path:
    base = Path(get_settings().ingestao_landing_path)
    caminho = base / dataset / competencia / estado
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def calcular_hash_arquivo(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            sha.update(bloco)
    return sha.hexdigest()


async def baixar_arquivo(
    dataset: str,
    competencia: str,
    url: str,
    nome_arquivo: str | None = None,
) -> dict:
    destino_dir = caminho_landing(dataset, competencia, "raw")
    nome = nome_arquivo or url.rstrip("/").split("/")[-1]
    destino = destino_dir / nome
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        response = await client.get(url)
    response.raise_for_status()
    destino.write_bytes(response.content)
    return {
        "path": destino,
        "arquivo_origem": nome,
        "url": url,
        "hash_arquivo": calcular_hash_arquivo(destino),
        "tamanho_bytes": destino.stat().st_size,
    }
