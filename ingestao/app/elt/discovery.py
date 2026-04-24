from __future__ import annotations

import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from ingestao.app.config import get_settings
from ingestao.app.elt.classifier import (
    EXTENSOES_SUPORTADAS,
    classificar_fonte_ans,
    fonte_pertence_ao_escopo,
)

ANS_PDA_BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"


class _IndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self.links.append(href)


def _eh_diretorio(url: str) -> bool:
    return urlparse(url).path.endswith("/")


def _nome_arquivo(url: str) -> str | None:
    nome = urlparse(url).path.rstrip("/").split("/")[-1]
    return nome or None


def _extensao(url: str) -> str:
    nome = _nome_arquivo(url) or ""
    if "." not in nome:
        return ""
    return "." + nome.rsplit(".", 1)[-1].lower()


def _parse_last_modified(valor: str | None) -> object | None:
    if not valor:
        return None
    try:
        return parsedate_to_datetime(valor)
    except (TypeError, ValueError):
        return None


def _parse_tamanho(valor: str | None) -> int | None:
    if not valor:
        return None
    texto = valor.strip()
    if texto in {"", "-"}:
        return None
    multiplicador = 1
    sufixo = texto[-1].upper()
    if sufixo in {"K", "M", "G"}:
        multiplicador = {"K": 1024, "M": 1024**2, "G": 1024**3}[sufixo]
        texto = texto[:-1]
    try:
        return int(float(texto) * multiplicador)
    except ValueError:
        return None


def _parse_data_indice(valor: str | None) -> object | None:
    if not valor:
        return None
    texto = valor.strip()
    if texto in {"", "-"}:
        return None
    for formato in ("%Y-%m-%d %H:%M", "%d-%b-%Y %H:%M"):
        try:
            return datetime.strptime(texto, formato).replace(tzinfo=UTC)
        except ValueError:
            continue
    return _parse_last_modified(texto)


def _metadata_por_href(html: str) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    padrao = re.compile(
        r'<a href="(?P<href>[^"]+)">.*?</a>\s*</td>'
        r'<td[^>]*>(?P<data>[^<]*)</td>\s*'
        r'<td[^>]*>(?P<tamanho>[^<]*)</td>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in padrao.finditer(html):
        href = match.group("href")
        metadata[href] = {
            "tamanho_bytes": _parse_tamanho(match.group("tamanho")),
            "last_modified": _parse_data_indice(match.group("data")),
        }
    return metadata


async def descobrir_fontes_ans(
    base_url: str = ANS_PDA_BASE_URL,
    *,
    max_depth: int = 5,
    escopo: str = "sector_core",
) -> list[dict]:
    settings = get_settings()
    timeout = httpx.Timeout(
        connect=settings.ans_http_connect_timeout_seconds,
        read=settings.ans_http_read_timeout_seconds,
        write=settings.ans_http_write_timeout_seconds,
        pool=settings.ans_http_pool_timeout_seconds,
    )
    headers = {"User-Agent": settings.ans_http_user_agent}
    visitados: set[str] = set()
    fontes: dict[str, dict] = {}

    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        async def visitar(url: str, profundidade: int) -> None:
            if profundidade > max_depth or url in visitados:
                return
            visitados.add(url)
            try:
                response = await client.get(url)
                response.raise_for_status()
            except httpx.HTTPError:
                return

            parser = _IndexParser()
            parser.feed(response.text)
            metadata_href = _metadata_por_href(response.text)
            for href in parser.links:
                if (
                    href.startswith("?")
                    or href in {"../", "/"}
                    or "parent directory" in href.lower()
                    or href.rstrip("/") == urlparse(base_url).path.rstrip("/")
                ):
                    continue
                absoluto = urljoin(url, href)
                parsed = urlparse(absoluto)
                if parsed.netloc != urlparse(base_url).netloc:
                    continue
                if _eh_diretorio(absoluto):
                    await visitar(absoluto, profundidade + 1)
                    continue
                extensao = _extensao(absoluto)
                if extensao and extensao not in EXTENSOES_SUPORTADAS:
                    continue
                nome = _nome_arquivo(absoluto)
                classificacao = classificar_fonte_ans(absoluto, nome)
                fonte = {
                    **classificacao,
                    "url": absoluto,
                    "nome_arquivo": nome,
                    "diretorio_origem": url,
                    "nivel": profundidade,
                    "ativo": True,
                    "observacao": None,
                }
                if not fonte_pertence_ao_escopo(fonte, escopo):
                    continue
                metadata = metadata_href.get(
                    href,
                    {"tamanho_bytes": None, "last_modified": None},
                )
                fonte.update(metadata)
                fontes[absoluto] = fonte

        await visitar(base_url, 0)

    return sorted(fontes.values(), key=lambda item: (item["prioridade"], item["url"]))
