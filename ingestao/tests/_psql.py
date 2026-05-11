"""Helper para executar psql em fixtures de teste, CI-aware.

Em CI (variavel POSTGRES_HOST setada), conecta direto via psql local usando
env vars POSTGRES_*. Localmente, faz fallback para `docker compose exec`
apenas quando POSTGRES_HOST nao esta definida.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

_COMPOSE_ROOT = Path(__file__).resolve().parents[2]


def _modo_direto() -> bool:
    return bool(os.getenv("POSTGRES_HOST"))


def _comando_e_ambiente(
    *extra_args: str,
) -> tuple[list[str], dict[str, str] | None, Path | None]:
    if _modo_direto():
        cmd = [
            "psql",
            "-h", os.getenv("POSTGRES_HOST", "localhost"),
            "-p", os.getenv("POSTGRES_PORT", "5432"),
            "-U", os.getenv("POSTGRES_USER", "healthintel"),
            "-d", os.getenv("POSTGRES_DB", "healthintel"),
            "-v", "ON_ERROR_STOP=1",
            *extra_args,
        ]
        env = {**os.environ, "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", "healthintel")}
        return cmd, env, None

    cmd = [
        "docker", "compose", "-f", "infra/docker-compose.yml",
        "exec", "-T", "postgres",
        "psql",
        "-v", "ON_ERROR_STOP=1",
        "-U", "healthintel",
        "-d", "healthintel",
        *extra_args,
    ]
    return cmd, None, _COMPOSE_ROOT


def executar_script(
    sql: str,
    *extra_args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    cmd, env, cwd = _comando_e_ambiente(*extra_args)
    return subprocess.run(
        cmd,
        input=sql,
        text=True,
        env=env,
        cwd=cwd,
        check=check,
        capture_output=True,
    )


def executar_comando(
    sql: str,
    *extra_args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    cmd, env, cwd = _comando_e_ambiente(*extra_args, "-c", sql)
    return subprocess.run(
        cmd,
        text=True,
        env=env,
        cwd=cwd,
        check=check,
        capture_output=True,
    )


def aplicar_arquivo(caminho: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return executar_script(caminho.read_text(), check=check)
