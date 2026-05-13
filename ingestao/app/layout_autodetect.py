"""Sprint 43 — auto-detector de layout para datasets ANS.

Lê a primeira linha (cabeçalho) do arquivo, gera uma assinatura sha256 das
colunas detectadas e consulta o Layout Service. Se a assinatura for
desconhecida (nenhum layout ativo do dataset bate), o serviço cria um
**rascunho** automaticamente para revisão humana e devolve o ID.

Fluxo:

    1. `detectar_assinatura(...)` extrai colunas físicas do arquivo
    2. `validar_arquivo_layout(...)` (em layout_client.py) verifica
       compatibilidade contra layouts ativos
    3. Se incompatível, chamamos `solicitar_rascunho(...)` aqui
    4. Retornamos um `ResultadoDeteccao` que a DAG/pipeline consome

A ingestão **não bloqueia**: continua com fallback `baixado_sem_parser` em
`arquivo_fonte_ans` e registra `LAYOUT_NAO_MAPEADO` em
`plataforma.tentativa_carga_ans`.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

import httpx

from ingestao.app.config import get_settings

settings = get_settings()

_MAX_LINHAS_AMOSTRA: Final[int] = 1
_TIMEOUT_HTTP_S: Final[float] = 20.0


@dataclass(slots=True)
class ResultadoDeteccao:
    """Resultado de `detectar_e_resolver_layout`."""
    dataset_codigo: str
    nome_arquivo: str
    colunas_detectadas: list[str]
    assinatura: str
    compativel: bool
    layout_id: str | None
    layout_versao_id: str | None
    rascunho_criado: bool
    rascunho_reaproveitado: bool
    motivos: list[str]


def _normalizar_coluna(valor: str) -> str:
    """Mesma regra do LayoutService._normalizar_coluna: lower + strip + remove
    espaços/aspas. Mantém compatibilidade de assinatura entre cliente e servidor."""
    if valor is None:
        return ""
    s = valor.strip().lower()
    s = s.replace("\"", "").replace("'", "")
    return s


def assinar_colunas(colunas: list[str]) -> str:
    """Gera assinatura sha256 das colunas normalizadas (estável)."""
    normalizadas = [_normalizar_coluna(c) for c in colunas]
    payload = "|".join(normalizadas)
    return sha256(payload.encode("utf-8")).hexdigest()


def detectar_cabecalho(
    caminho: str | Path, *, delimitador: str = ";", encoding: str = "utf-8"
) -> list[str]:
    """Lê a primeira linha do arquivo CSV e retorna as colunas detectadas.
    Tolerante a BOM e a encodings comuns (utf-8, latin-1 como fallback)."""
    p = Path(caminho)
    tentativas = [encoding, "utf-8-sig", "latin-1", "cp1252"]
    ultima_excecao: Exception | None = None
    for enc in tentativas:
        try:
            with open(p, encoding=enc, newline="") as f:
                reader = csv.reader(f, delimiter=delimitador)
                primeira_linha = next(reader, [])
                # Remove BOM residual da primeira coluna
                if primeira_linha and primeira_linha[0].startswith("﻿"):
                    primeira_linha[0] = primeira_linha[0][1:]
                return [str(c) for c in primeira_linha]
        except (UnicodeDecodeError, csv.Error) as exc:
            ultima_excecao = exc
            continue
    raise RuntimeError(
        f"Não consegui decodificar cabeçalho de {p} com {tentativas}: "
        f"{ultima_excecao}"
    )


def detectar_cabecalho_de_bytes(
    conteudo: bytes, *, delimitador: str = ";"
) -> list[str]:
    """Mesma lógica de `detectar_cabecalho` mas a partir de bytes em memória.
    Útil para downloads in-flight (ex.: streaming)."""
    tentativas = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in tentativas:
        try:
            texto = conteudo.decode(enc, errors="strict")
            reader = csv.reader(io.StringIO(texto), delimiter=delimitador)
            primeira = next(reader, [])
            if primeira and primeira[0].startswith("﻿"):
                primeira[0] = primeira[0][1:]
            return [str(c) for c in primeira]
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Bytes não decodificáveis com {tentativas}.")


async def validar_arquivo_layout(
    dataset_codigo: str, colunas_detectadas: list[str], nome_arquivo: str
) -> dict:
    """Wrapper local mantido para coesão (idêntico ao layout_client). Evita
    import circular se este módulo for usado de dentro de helpers que já
    importam layout_autodetect."""
    payload = {
        "dataset_codigo": dataset_codigo,
        "colunas_detectadas": colunas_detectadas,
        "nome_arquivo": nome_arquivo,
    }
    async with httpx.AsyncClient(
        base_url=settings.layout_service_url,
        timeout=_TIMEOUT_HTTP_S,
        headers={"X-Service-Token": settings.layout_service_token},
    ) as client:
        response = await client.post("/layout/validar-arquivo", json=payload)
    response.raise_for_status()
    return response.json()


async def solicitar_rascunho(
    *,
    dataset_codigo: str,
    colunas: list[str],
    nome_arquivo: str | None = None,
    arquivo_hash: str | None = None,
    motivo: str | None = None,
) -> dict:
    """Aciona POST /layout/{dataset_codigo}/rascunho. Idempotente por
    assinatura — múltiplas chamadas com a mesma assinatura retornam a mesma
    versão com `reaproveitado=True`.

    Retorna dict com: layout_id, layout_versao_id, status, assinatura_colunas,
    reaproveitado.
    """
    payload = {
        "colunas": colunas,
        "nome_arquivo": nome_arquivo,
        "arquivo_hash": arquivo_hash,
        "motivo": motivo or "assinatura desconhecida via auto-detector",
    }
    async with httpx.AsyncClient(
        base_url=settings.layout_service_url,
        timeout=_TIMEOUT_HTTP_S,
        headers={"X-Service-Token": settings.layout_service_token},
    ) as client:
        response = await client.post(
            f"/layout/{dataset_codigo}/rascunho", json=payload
        )
    response.raise_for_status()
    return response.json()


async def detectar_e_resolver_layout(
    *,
    dataset_codigo: str,
    caminho_arquivo: str | Path,
    delimitador: str = ";",
    encoding: str = "utf-8",
    arquivo_hash: str | None = None,
) -> ResultadoDeteccao:
    """Fluxo completo:

    1. Lê cabeçalho do arquivo
    2. Calcula assinatura
    3. Tenta validar contra layouts ativos do dataset
    4. Se incompatível, cria rascunho automaticamente

    Não bloqueia. A DAG/pipeline decide o que fazer com `ResultadoDeteccao`:
    - se `compativel=True`: prossegue parse normal
    - se `rascunho_criado=True`: registra `LAYOUT_NAO_MAPEADO` em
      `plataforma.tentativa_carga_ans` e marca o arquivo como
      `baixado_sem_parser` em `plataforma.arquivo_fonte_ans`.
    """
    nome_arquivo = Path(caminho_arquivo).name
    colunas = detectar_cabecalho(
        caminho_arquivo, delimitador=delimitador, encoding=encoding
    )
    assinatura = assinar_colunas(colunas)

    resposta_validar = await validar_arquivo_layout(
        dataset_codigo=dataset_codigo,
        colunas_detectadas=colunas,
        nome_arquivo=nome_arquivo,
    )
    compativel = bool(resposta_validar.get("compativel"))

    if compativel:
        return ResultadoDeteccao(
            dataset_codigo=dataset_codigo,
            nome_arquivo=nome_arquivo,
            colunas_detectadas=colunas,
            assinatura=assinatura,
            compativel=True,
            layout_id=resposta_validar.get("layout_id"),
            layout_versao_id=resposta_validar.get("layout_versao_id"),
            rascunho_criado=False,
            rascunho_reaproveitado=False,
            motivos=resposta_validar.get("motivos", []),
        )

    # Incompatível: cria rascunho automaticamente
    rascunho = await solicitar_rascunho(
        dataset_codigo=dataset_codigo,
        colunas=colunas,
        nome_arquivo=nome_arquivo,
        arquivo_hash=arquivo_hash,
        motivo="; ".join(resposta_validar.get("motivos", []) or ["assinatura desconhecida"]),
    )
    return ResultadoDeteccao(
        dataset_codigo=dataset_codigo,
        nome_arquivo=nome_arquivo,
        colunas_detectadas=colunas,
        assinatura=assinatura,
        compativel=False,
        layout_id=rascunho.get("layout_id"),
        layout_versao_id=rascunho.get("layout_versao_id"),
        rascunho_criado=True,
        rascunho_reaproveitado=bool(rascunho.get("reaproveitado")),
        motivos=resposta_validar.get("motivos", []),
    )
