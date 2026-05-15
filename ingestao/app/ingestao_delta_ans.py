"""Ingestao Sprint 41/42 - Delta ANS real e auditavel.

As fontes delta da ANS nem sempre sao arquivos diretos: varias familias
publicam indices HTML com CSV/TXT/ZIP dentro. Este modulo resolve o arquivo
real antes da carga, registra `plataforma.arquivo_fonte_ans` e evita parsear
HTML/dicionarios como dado produtivo.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
import re
import zipfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from uuid import uuid4

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    POLITICA_DATASET_ALIAS,
    SessionLocal,
    carregar_dataset_bruto,
    carregar_dataset_bruto_em_batches,
    coluna_periodo_dataset,
    dataset_periodo_ja_carregado,
    registrar_job_carga,
    registrar_lote_ingestao,
)
from ingestao.app.config import get_settings
from ingestao.app.pipeline_bronze import processar_arquivo_bruto

_ANS_FTP = "https://dadosabertos.ans.gov.br/FTP/PDA"
_EXTENSOES_DADOS = (".csv", ".txt", ".zip")
_EXTENSOES_DOCUMENTAIS = (".ods", ".pdf", ".xls", ".xlsx", ".json", ".xml")
_DEFAULT_MAX_FILES = 1
_BATCH_SIZE = 5000


@dataclass(frozen=True)
class FonteDelta:
    dataset_codigo: str
    familia: str
    url: str
    nome_arquivo: str
    competencia: str
    tamanho_bytes: int | None = None
    last_modified: datetime | None = None


class _IndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def _url(caminho: str) -> str:
    return f"{_ANS_FTP}/{caminho.lstrip('/')}"


def _eh_diretorio(url: str) -> bool:
    return urlparse(url).path.endswith("/")


def _nome_arquivo(url: str) -> str:
    return unquote(Path(urlparse(url).path).name)


def _competencia_do_nome(nome: str, default: str) -> str:
    match = re.search(r"(20\d{4})", nome)
    return match.group(1) if match else default


def _max_files() -> int:
    valor = os.getenv("ANS_DELTA_MAX_FILES", str(_DEFAULT_MAX_FILES))
    try:
        return max(1, int(valor))
    except ValueError:
        return _DEFAULT_MAX_FILES


def _tiss_ufs() -> list[str]:
    valor = os.getenv("ANS_TISS_UFS", "SP")
    return [uf.strip().upper() for uf in valor.split(",") if uf.strip()]


def _tiss_tipos() -> list[str]:
    valor = os.getenv("ANS_TISS_TIPOS", "CONS")
    return [item.strip().upper() for item in valor.split(",") if item.strip()]


def _normalizar_chave(chave: str) -> str:
    return (
        chave.strip()
        .lstrip("#")
        .replace("\ufeff", "")
        .replace('"', "")
        .strip()
    )


def _detectar_encoding(conteudo: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            conteudo.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "latin-1"


def _detectar_dialect(amostra: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(amostra, delimiters=";,|\t,")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
        return dialect


def _ler_csv_bytes(conteudo: bytes) -> list[dict[str, str]]:
    encoding = _detectar_encoding(conteudo[:8192])
    texto = conteudo.decode(encoding, errors="replace")
    amostra = texto[:8192]
    if "<html" in amostra.lower() or "<!doctype html" in amostra.lower():
        raise ValueError("Arquivo HTML nao e fonte tabular ANS valida.")
    reader = csv.DictReader(io.StringIO(texto), dialect=_detectar_dialect(amostra))
    return [
        {_normalizar_chave(str(chave)): valor for chave, valor in row.items() if chave}
        for row in reader
    ]


def _iter_csv_path(path: Path) -> Iterator[list[dict[str, str]]]:
    with path.open("rb") as binario:
        encoding = _detectar_encoding(binario.read(8192))
    with path.open("r", encoding=encoding, errors="replace", newline="") as arquivo:
        amostra = arquivo.read(8192)
        arquivo.seek(0)
        if "<html" in amostra.lower() or "<!doctype html" in amostra.lower():
            raise ValueError("Arquivo HTML nao e fonte tabular ANS valida.")
        reader = csv.DictReader(arquivo, dialect=_detectar_dialect(amostra))
        batch: list[dict[str, str]] = []
        for row in reader:
            batch.append({_normalizar_chave(str(k)): v for k, v in row.items() if k})
            if len(batch) >= _BATCH_SIZE:
                yield batch
                batch = []
        if batch:
            yield batch


def _iter_zip_path(path: Path) -> Iterator[list[dict[str, str]]]:
    with zipfile.ZipFile(path) as pacote:
        for nome in pacote.namelist():
            if nome.endswith("/") or not nome.lower().endswith((".csv", ".txt")):
                continue
            with pacote.open(nome, "r") as binario:
                conteudo_amostra = binario.read(8192)
                encoding = _detectar_encoding(conteudo_amostra)
                binario.seek(0)
                wrapper = io.TextIOWrapper(
                    binario,
                    encoding=encoding,
                    errors="replace",
                    newline="",
                )
                amostra = wrapper.read(8192)
                wrapper.seek(0)
                reader = csv.DictReader(wrapper, dialect=_detectar_dialect(amostra))
                batch: list[dict[str, str]] = []
                for row in reader:
                    batch.append({_normalizar_chave(str(k)): v for k, v in row.items() if k})
                    if len(batch) >= _BATCH_SIZE:
                        yield batch
                        batch = []
                if batch:
                    yield batch


def _ler_arquivo(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".zip":
        registros: list[dict[str, str]] = []
        for batch in _iter_zip_path(path):
            registros.extend(batch)
        return registros
    return [registro for batch in _iter_csv_path(path) for registro in batch]


def _iter_arquivo(path: Path) -> Iterator[list[dict[str, str]]]:
    if path.suffix.lower() == ".zip":
        yield from _iter_zip_path(path)
        return
    yield from _iter_csv_path(path)


async def _listar_links(url: str) -> list[str]:
    settings = get_settings()
    timeout = httpx.Timeout(
        connect=settings.ans_http_connect_timeout_seconds,
        read=settings.ans_http_read_timeout_seconds,
        write=settings.ans_http_write_timeout_seconds,
        pool=settings.ans_http_pool_timeout_seconds,
    )
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": settings.ans_http_user_agent},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
    parser = _IndexParser()
    parser.feed(response.text)
    links: list[str] = []
    for href in parser.links:
        if href.startswith("?") or href in {"../", "/"} or "parent" in href.lower():
            continue
        absoluto = urljoin(url, href)
        if urlparse(absoluto).netloc == urlparse(_ANS_FTP).netloc:
            links.append(absoluto)
    return links


async def _resolver_fontes(
    *,
    dataset_codigo: str,
    familia: str,
    competencia: str,
    base_url: str,
    padrao: str | None = None,
    max_files: int | None = None,
) -> list[FonteDelta]:
    if not _eh_diretorio(base_url):
        nome = _nome_arquivo(base_url)
        return [
            FonteDelta(
                dataset_codigo=dataset_codigo,
                familia=familia,
                url=base_url,
                nome_arquivo=nome,
                competencia=_competencia_do_nome(nome, competencia),
            )
        ]

    regex = re.compile(padrao or r".*\.(csv|txt|zip)$", re.IGNORECASE)
    fontes: list[FonteDelta] = []
    for link in await _listar_links(base_url):
        nome = _nome_arquivo(link)
        nome_lower = nome.lower()
        if nome_lower.endswith(_EXTENSOES_DOCUMENTAIS):
            continue
        if not nome_lower.endswith(_EXTENSOES_DADOS):
            continue
        if not regex.search(nome):
            continue
        fontes.append(
            FonteDelta(
                dataset_codigo=dataset_codigo,
                familia=familia,
                url=link,
                nome_arquivo=nome,
                competencia=_competencia_do_nome(nome, competencia),
            )
        )

    if not fontes:
        raise RuntimeError(f"Nenhum arquivo tabular encontrado para {dataset_codigo}: {base_url}")

    fontes.sort(key=lambda item: (item.competencia, item.nome_arquivo), reverse=True)
    limite = max_files if max_files is not None else _max_files()
    return fontes[:limite]


async def _resolver_fontes_tiss(
    *,
    dataset_codigo: str,
    familia: str,
    competencia: str,
    subfamilia: str,
    marcador_nome: str,
) -> list[FonteDelta]:
    ano = (competencia or "")[:4]
    if not re.fullmatch(r"20\d{2}", ano):
        ano = str(date.today().year - 1)
    fontes: list[FonteDelta] = []
    tipos = _tiss_tipos()
    for uf in _tiss_ufs():
        base = _url(f"TISS/{subfamilia}/{ano}/{uf}/")
        tipo_expr = "|".join(re.escape(tipo) for tipo in tipos)
        padrao = rf"^{re.escape(uf)}_(20\d{{4}})_{marcador_nome}_({tipo_expr})\.zip$"
        try:
            fontes.extend(
                await _resolver_fontes(
                    dataset_codigo=dataset_codigo,
                    familia=familia,
                    competencia=competencia,
                    base_url=base,
                    padrao=padrao,
                    max_files=int(os.getenv("ANS_TISS_MAX_FILES", "1")),
                )
            )
        except Exception:
            continue
    ano_fallback = str(date.today().year - 1)
    if not fontes and ano != ano_fallback:
        return await _resolver_fontes_tiss(
            dataset_codigo=dataset_codigo,
            familia=familia,
            competencia=ano_fallback,
            subfamilia=subfamilia,
            marcador_nome=marcador_nome,
        )
    if not fontes:
        raise RuntimeError(
            f"Nenhum arquivo TISS encontrado para {dataset_codigo}, ano={ano}, "
            f"ufs={','.join(_tiss_ufs())}, tipos={','.join(tipos)}."
        )
    fontes.sort(key=lambda item: (item.competencia, item.nome_arquivo), reverse=True)
    return fontes[: int(os.getenv("ANS_TISS_MAX_FILES", "1"))]


async def _baixar_fonte(fonte: FonteDelta) -> dict[str, str]:
    settings = get_settings()
    destino_dir = (
        Path(settings.ingestao_landing_path)
        / "delta_ans_100"
        / fonte.dataset_codigo
        / fonte.competencia
    )
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / fonte.nome_arquivo
    sha = hashlib.sha256()
    tamanho = 0

    if destino.exists() and settings.ans_allow_landing_cache:
        with destino.open("rb") as arquivo:
            for chunk in iter(lambda: arquivo.read(1024 * 1024), b""):
                sha.update(chunk)
                tamanho += len(chunk)
    else:
        timeout = httpx.Timeout(
            connect=settings.ans_http_connect_timeout_seconds,
            read=settings.ans_http_read_timeout_seconds,
            write=settings.ans_http_write_timeout_seconds,
            pool=settings.ans_http_pool_timeout_seconds,
        )
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": settings.ans_http_user_agent},
        ) as client:
            async with client.stream("GET", fonte.url) as response:
                response.raise_for_status()
                with destino.open("wb") as arquivo:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        arquivo.write(chunk)
                        sha.update(chunk)
                        tamanho += len(chunk)

    return {
        "dataset_codigo": fonte.dataset_codigo,
        "familia": fonte.familia,
        "url": fonte.url,
        "path": str(destino),
        "arquivo_origem": fonte.nome_arquivo,
        "hash_arquivo": sha.hexdigest(),
        "tamanho_bytes": str(tamanho),
    }


async def _registrar_arquivo_fonte(
    fonte: FonteDelta,
    payload: dict[str, str],
    status: str,
    erro: str | None = None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.arquivo_fonte_ans (
                    dataset_codigo, familia, url, caminho_landing, nome_arquivo,
                    hash_arquivo, tamanho_bytes, baixado_em, status, erro_mensagem,
                    tentativa, updated_at
                ) values (
                    :dataset_codigo, :familia, :url, :caminho_landing, :nome_arquivo,
                    :hash_arquivo, :tamanho_bytes, now(), :status, :erro_mensagem,
                    1, now()
                )
                on conflict do nothing
                """
            ),
            {
                "dataset_codigo": fonte.dataset_codigo,
                "familia": fonte.familia,
                "url": fonte.url,
                "caminho_landing": payload.get("path"),
                "nome_arquivo": payload.get("arquivo_origem") or fonte.nome_arquivo,
                "hash_arquivo": payload.get("hash_arquivo"),
                "tamanho_bytes": int(payload.get("tamanho_bytes") or 0),
                "status": status,
                "erro_mensagem": erro,
            },
        )
        try:
            await session.execute(
                text(
                    """
                    update plataforma.arquivo_fonte_ans
                    set status = :status,
                        erro_mensagem = :erro_mensagem,
                        caminho_landing = coalesce(:caminho_landing, caminho_landing),
                        updated_at = now()
                    where id = (
                        select id
                        from plataforma.arquivo_fonte_ans
                        where dataset_codigo = :dataset_codigo
                          and url = :url
                          and (
                            hash_arquivo is not distinct from :hash_arquivo
                            or :hash_arquivo is null
                          )
                        order by
                          case
                            when status in ('baixado', 'carregado', 'baixado_sem_parser')
                            then 0
                            else 1
                          end,
                          created_at desc
                        limit 1
                    )
                    """
                ),
                {
                    "dataset_codigo": fonte.dataset_codigo,
                    "url": fonte.url,
                    "hash_arquivo": payload.get("hash_arquivo"),
                    "caminho_landing": payload.get("path"),
                    "status": status,
                    "erro_mensagem": erro,
                },
            )
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def _registrar_tentativa(
    *,
    dag_id: str,
    task_id: str,
    dominio: str,
    dataset_codigo: str,
    fonte_url: str | None = None,
    arquivo_nome: str | None = None,
    arquivo_hash: str | None = None,
    competencia: int | None = None,
    status: str,
    motivo: str | None = None,
    linhas_lidas: int = 0,
    linhas_validas: int = 0,
    linhas_inseridas: int = 0,
    tabela_destino: str | None = None,
    erro_tipo: str | None = None,
    erro_mensagem: str | None = None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.tentativa_carga_ans (
                    dag_id, task_id, dominio, dataset_codigo, fonte_url,
                    arquivo_nome, arquivo_hash, competencia, status, motivo,
                    linhas_lidas, linhas_validas, linhas_inseridas,
                    tabela_destino, erro_tipo, erro_mensagem,
                    iniciado_em, finalizado_em
                ) values (
                    :dag_id, :task_id, :dominio, :dataset_codigo, :fonte_url,
                    :arquivo_nome, :arquivo_hash, :competencia, :status, :motivo,
                    :linhas_lidas, :linhas_validas, :linhas_inseridas,
                    :tabela_destino, :erro_tipo, :erro_mensagem,
                    now(), now()
                )
                """
            ),
            {
                "dag_id": dag_id,
                "task_id": task_id,
                "dominio": dominio,
                "dataset_codigo": dataset_codigo,
                "fonte_url": fonte_url,
                "arquivo_nome": arquivo_nome,
                "arquivo_hash": arquivo_hash,
                "competencia": competencia,
                "status": status,
                "motivo": motivo,
                "linhas_lidas": linhas_lidas,
                "linhas_validas": linhas_validas,
                "linhas_inseridas": linhas_inseridas,
                "tabela_destino": tabela_destino,
                "erro_tipo": erro_tipo,
                "erro_mensagem": erro_mensagem,
            },
        )
        await session.commit()


def _competencia_iso(valor: str) -> str:
    digitos = "".join(ch for ch in str(valor) if ch.isdigit())
    return digitos[:6] if len(digitos) >= 6 else str(valor)


def _inteiro(valor: object) -> int | None:
    digitos = re.sub(r"[^0-9-]", "", str(valor or ""))
    if not digitos or digitos == "-":
        return None
    return int(digitos)


def _decimal(valor: object) -> Decimal | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    texto = texto.replace(".", "").replace(",", ".") if "," in texto else texto
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def _data_iso(valor: object) -> date | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def _normalizar_registros(
    dataset_codigo: str,
    registros: list[dict[str, str]],
    competencia: str,
    arquivo_origem: str,
) -> list[dict[str, str]]:
    normalizador = _NORMALIZADORES.get(dataset_codigo)
    saida = (
        [normalizador(r, competencia, arquivo_origem) for r in registros]
        if normalizador
        else registros
    )
    for registro in saida:
        registro.setdefault("competencia", _inteiro(_competencia_iso(competencia)))
    return saida


def _produto_caracteristica(row: dict[str, str], competencia: str, _: str) -> dict[str, str]:
    return {
        "registro_ans": row.get("REGISTRO_OPERADORA") or row.get("CD_OPERADORA") or "",
        "codigo_produto": row.get("CD_PLANO") or row.get("CD_PRODUTO") or "",
        "nome_produto": row.get("NM_PLANO") or row.get("NM_PRODUTO") or "",
        "segmentacao": row.get("SGMT_ASSISTENCIAL") or row.get("SEGMENTACAO") or "",
        "tipo_contratacao": row.get("CONTRATACAO") or row.get("TIPO_CONTRATACAO") or "",
        "abrangencia_geografica": row.get("ABRANGENCIA_COBERTURA") or "",
        "cobertura_area": row.get("COBERTURA") or row.get("MUNICIPIOS_COBERTURA") or "",
        "modalidade": row.get("GR_MODALIDADE") or row.get("MODALIDADE") or "",
        "uf_comercializacao": row.get("SG_UF") or row.get("UF_COMERCIALIZACAO") or "",
        "competencia": _inteiro(_competencia_iso(row.get("DT_ATUALIZACAO") or competencia)),
    }


def _produto_tabela_auxiliar(
    row: dict[str, str], competencia: str, arquivo_origem: str
) -> dict[str, str | int | None]:
    id_area_geografica = row.get("ID_DETALHE_AREA_GEOGRAFICA") or row.get("ID_PLANO") or ""
    return {
        "competencia": _inteiro(_competencia_iso(competencia)),
        "registro_ans": row.get("REGISTRO_OPERADORA") or row.get("CD_OPERADORA"),
        "codigo_produto": id_area_geografica[:20],
        "tipo_tabela": "DETALHAMENTO_MUNICIPIOS",
        "descricao_tabela": Path(arquivo_origem).stem,
        "codigo_item": row.get("CD_MUNICIPIO") or row.get("SG_UF"),
        "descricao_item": row.get("NM_MUNICIPIO") or row.get("NM_REGIAO") or row.get("SG_UF"),
    }


def _historico_plano(row: dict[str, str], competencia: str, _: str) -> dict[str, str]:
    return {
        "registro_ans": row.get("CD_OPERADORA") or row.get("REGISTRO_ANS") or "",
        "codigo_plano": row.get("CD_PLANO") or "",
        "nome_plano": row.get("NM_PLANO") or "",
        "situacao": row.get("DE_SITUACAO_PRINCIPAL") or row.get("SITUACAO") or "",
        "data_situacao": _data_iso(row.get("DT_INICIO_STATUS") or row.get("DT_SITUACAO")),
        "segmentacao": row.get("SEGMENTACAO") or "",
        "tipo_contratacao": row.get("TIPO_CONTRATACAO") or "",
        "abrangencia_geografica": row.get("ABRANGENCIA") or "",
        "uf": (row.get("UF") or "")[:2],
        "competencia": _inteiro(_competencia_iso(competencia)),
    }


def _plano_servico_opcional(row: dict[str, str], competencia: str, _: str) -> dict:
    return {
        "competencia": _inteiro(_competencia_iso(competencia)),
        "registro_ans": row.get("CD_OPERADORA") or row.get("REGISTRO_OPERADORA"),
        "codigo_plano": row.get("ID_PLANO") or row.get("CD_PLANO"),
        "codigo_servico": row.get("CD_SERVICO_OPCIONAL") or row.get("CD_SERVICO"),
        "descricao_servico": row.get("SERVICO_OPCIONAL") or row.get("DS_SERVICO"),
        "tipo_servico": "SERVICO_OPCIONAL",
    }


def _quadro_auxiliar(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict:
    tipo = row.get("DE_CORRESPONSABILIDADE") or Path(arquivo_origem).stem
    return {
        "competencia": _inteiro(_competencia_iso(competencia)),
        "registro_ans": row.get("CD_OPERADORA") or row.get("REGISTRO_ANS"),
        "codigo_plano": row.get("CD_PLANO"),
        "tipo_corresponsabilidade": tipo,
        "percentual_corresponsabilidade": _decimal(row.get("PCT_CORRESPONSABILIDADE")),
        "valor_corresponsabilidade": _decimal(row.get("VL_SALDO_FINAL")),
        "descricao": " | ".join(
            item
            for item in (
                row.get("DE_CLASSIFICACAO"),
                row.get("DE_PGTO_CORR_CEDIDA"),
                row.get("DE_CONTRATACAO_PLANO"),
                row.get("TP_VIGENCIA_PLANO"),
                row.get("DE_FINANCIAMENTO_PLANO"),
            )
            if item
        ),
    }


def _tuss(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict[str, str]:
    vigencia_fim = row.get("Data de fim de vigência") or row.get("DT_FIM_VIGENCIA") or ""
    vigente = True
    if vigencia_fim:
        try:
            vigente = datetime.fromisoformat(vigencia_fim).date() >= date.today()
        except ValueError:
            vigente = True
    return {
        "codigo_tuss": row.get("Código do Termo") or row.get("CD_TUSS") or row.get("CODIGO") or "",
        "descricao": row.get("Termo") or row.get("DS_TUSS") or row.get("DESCRICAO") or "",
        "versao_tuss": _competencia_iso(competencia) or "oficial",
        "vigencia_inicio": _data_iso(
            row.get("Data de início de vigência") or row.get("DT_INICIO_VIGENCIA")
        ),
        "vigencia_fim": _data_iso(vigencia_fim),
        "is_tuss_vigente": vigente,
        "grupo": Path(arquivo_origem).stem,
        "subgrupo": row.get("NOME TÉCNICO") or row.get("Classe de Risco") or "",
    }


def _sip(row: dict[str, str], competencia: str, _: str) -> dict[str, str]:
    return {
        "competencia": _inteiro(_competencia_iso(row.get("ID_TRIMESTRE") or competencia)),
        "registro_ans": row.get("REGISTRO_ANS") or row.get("CD_OPERADORA") or None,
        "cd_municipio": row.get("CD_MUNICIPIO") or None,
        "nm_municipio": row.get("NM_MUNICIPIO") or None,
        "sg_uf": row.get("SG_UF") or None,
        "nm_regiao": row.get("NM_REGIAO") or None,
        "tipo_assistencial": row.get("DE_ITEM_ASST") or row.get("ID_ITEM_ASST") or "",
        "qt_beneficiarios": _inteiro(row.get("QT_BENEF_FORA_CARENCIA")),
        "qt_eventos": _inteiro(row.get("QT_EVENTOS")),
        "indicador_cobertura": None,
    }


def _tiss_amb(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict[str, str]:
    uf = arquivo_origem[:2] if len(arquivo_origem) >= 2 else ""
    return {
        "competencia": _inteiro(_competencia_iso(row.get("COMPETENCIA") or competencia)),
        "registro_ans": row.get("REGISTRO_ANS") or row.get("CD_OPERADORA") or None,
        "cd_municipio": row.get("CD_MUNICIPIO") or row.get("COD_MUNICIPIO") or None,
        "nm_municipio": row.get("NM_MUNICIPIO") or None,
        "sg_uf": row.get("SG_UF") or uf,
        "tipo_evento": (
            row.get("TIPO_EVENTO") or row.get("DE_ITEM_ASST") or Path(arquivo_origem).stem
        ),
        "qt_eventos": _inteiro(row.get("QT_EVENTOS") or row.get("QT_PROCEDIMENTOS")),
        "vl_pago": _decimal(row.get("VL_PAGO") or row.get("VL_DESPESA_ASST_LIQ")),
        "vl_informado": _decimal(row.get("VL_INFORMADO") or row.get("VL_APRESENTADO")),
    }


def _tiss_hosp(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict[str, str]:
    base = _tiss_amb(row, competencia, arquivo_origem)
    base["qt_internacoes"] = _inteiro(row.get("QT_INTERNACOES") or row.get("QT_EVENTOS"))
    base["qt_diarias"] = _inteiro(row.get("QT_DIARIAS"))
    base.pop("qt_eventos", None)
    return base


def _tiss_plano(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict[str, str]:
    uf = arquivo_origem[:2] if len(arquivo_origem) >= 2 else ""
    return {
        "competencia": _inteiro(_competencia_iso(row.get("COMPETENCIA") or competencia)),
        "registro_ans": row.get("REGISTRO_ANS") or row.get("CD_OPERADORA") or None,
        "codigo_plano": row.get("CD_PLANO") or row.get("CODIGO_PLANO") or None,
        "segmentacao": row.get("SEGMENTACAO") or row.get("SGMT_ASSISTENCIAL") or "",
        "tipo_contratacao": row.get("TIPO_CONTRATACAO") or row.get("CONTRATACAO") or "",
        "qt_beneficiarios": _inteiro(row.get("QT_BENEFICIARIOS")),
        "qt_eventos": _inteiro(row.get("QT_EVENTOS")),
        "vl_pago": _decimal(row.get("VL_PAGO") or row.get("VL_DESPESA_ASST_LIQ")),
        "sg_uf": uf,
    }


_NORMALIZADORES: dict[str, Callable[[dict[str, str], str, str], dict[str, str]]] = {
    "produto_caracteristica": _produto_caracteristica,
    "produto_tabela_auxiliar": _produto_tabela_auxiliar,
    "historico_plano": _historico_plano,
    "plano_servico_opcional": _plano_servico_opcional,
    "quadro_auxiliar_corresponsabilidade": _quadro_auxiliar,
    "tuss_oficial": _tuss,
    "sip_mapa_assistencial": _sip,
    "tiss_ambulatorial": _tiss_amb,
    "tiss_hospitalar": _tiss_hosp,
    "tiss_dados_plano": _tiss_plano,
}


async def _carregar_direto(
    dataset_codigo: str,
    arquivo_origem: str,
    hash_arquivo: str,
    registros: list[dict],
    *,
    layout_id: str = "layout_delta_ans_real",
    layout_versao_id: str = "layout_delta_ans_real:v1",
) -> dict:
    lote = await carregar_dataset_bruto(
        dataset_codigo,
        registros,
        arquivo_origem=arquivo_origem,
        layout_id=layout_id,
        layout_versao_id=layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura="sha256:delta-ans-real-normalizado",
        colunas_mapeadas=[],
    )
    return {
        "status": "carregado",
        "lote_id": lote.lote_id,
        "tabela_destino": lote.tabela_destino,
        "total_registros": lote.total_registros,
    }


async def _hash_ja_carregado(dataset_codigo: str, hash_arquivo: str) -> bool:
    async with SessionLocal() as session:
        resultado = await session.execute(
            text(
                """
                select 1
                from plataforma.lote_ingestao
                where dataset = :dataset
                  and hash_arquivo = :hash_arquivo
                  and status in ('sucesso', 'sucesso_com_alertas')
                limit 1
                """
            ),
            {"dataset": dataset_codigo, "hash_arquivo": hash_arquivo},
        )
        return resultado.scalar_one_or_none() is not None


async def _carregar_direto_streaming(
    *,
    fonte: FonteDelta,
    path: Path,
    hash_arquivo: str,
    normalizar: bool,
    layout_id: str = "layout_delta_ans_real",
    layout_versao_id: str = "layout_delta_ans_real:v1",
) -> dict:
    if await _hash_ja_carregado(fonte.dataset_codigo, hash_arquivo):
        lote_id = str(uuid4())
        await registrar_lote_ingestao(
            lote_id=lote_id,
            dataset_codigo=fonte.dataset_codigo,
            competencia=fonte.competencia,
            arquivo_origem=fonte.nome_arquivo,
            hash_arquivo=hash_arquivo,
            hash_estrutura="sha256:delta-ans-real-normalizado",
            versao_layout=layout_versao_id,
            status="ignorado_duplicata",
            total_linhas_raw=0,
            total_aprovadas=0,
            total_quarentena=0,
            origem_execucao="delta_ans_streaming",
            erro_mensagem="Arquivo ja carregado anteriormente por hash_arquivo.",
        )
        return {
            "status": "carregado",
            "lote_id": lote_id,
            "tabela_destino": fonte.dataset_codigo,
            "total_registros": 0,
        }

    lote_id = str(uuid4())
    total_linhas = 0
    total_aprovadas = 0
    competencias_fora_janela_registradas: set[int] = set()
    janela_carga = None
    try:
        from ingestao.app.janela_carga import (
            DatasetNaoTemporalError,
            PoliticaDatasetNaoEncontradaError,
            obter_janela,
        )

        janela_carga = await obter_janela(
            POLITICA_DATASET_ALIAS.get(fonte.dataset_codigo, fonte.dataset_codigo)
        )
    except (DatasetNaoTemporalError, PoliticaDatasetNaoEncontradaError):
        janela_carga = None

    for batch in _iter_arquivo(path):
        total_linhas += len(batch)
        registros = (
            _normalizar_registros(
                fonte.dataset_codigo,
                batch,
                fonte.competencia,
                fonte.nome_arquivo,
            )
            if normalizar
            else batch
        )
        if janela_carga is not None:
            from ingestao.app.janela_carga import (
                competencia_dentro_janela,
                normalizar_competencia,
                registrar_decisao,
            )

            coluna_competencia = janela_carga.coluna_competencia or "competencia"
            registros_dentro_janela = []
            for item in registros:
                valor_competencia = item.get(coluna_competencia) or item.get("competencia")
                try:
                    competencia_item = normalizar_competencia(valor_competencia)
                except (TypeError, ValueError):
                    continue
                if competencia_dentro_janela(competencia_item, janela_carga):
                    registros_dentro_janela.append(item)
                    continue
                if competencia_item not in competencias_fora_janela_registradas:
                    await registrar_decisao(
                        janela_carga.dataset_codigo,
                        competencia_item,
                        "ignorado_fora_janela",
                        janela_carga,
                        "Registro fora da janela dinamica de carga.",
                    )
                    competencias_fora_janela_registradas.add(competencia_item)
            registros = registros_dentro_janela
        aprovados = [
            item
            for item in registros
            if any(valor is not None and str(valor).strip() for valor in item.values())
        ]
        if not aprovados:
            continue
        total_aprovadas += await carregar_dataset_bruto_em_batches(
            fonte.dataset_codigo,
            aprovados,
            arquivo_origem=fonte.nome_arquivo,
            layout_id=layout_id,
            layout_versao_id=layout_versao_id,
            hash_arquivo=hash_arquivo,
            hash_estrutura="sha256:delta-ans-real-normalizado",
            lote_id=lote_id,
        )

    status_lote = "sucesso" if total_linhas == total_aprovadas else "sucesso_com_alertas"
    await registrar_lote_ingestao(
        lote_id=lote_id,
        dataset_codigo=fonte.dataset_codigo,
        competencia=fonte.competencia,
        arquivo_origem=fonte.nome_arquivo,
        hash_arquivo=hash_arquivo,
        hash_estrutura="sha256:delta-ans-real-normalizado",
        versao_layout=layout_versao_id,
        status=status_lote,
        total_linhas_raw=total_linhas,
        total_aprovadas=total_aprovadas,
        total_quarentena=max(0, total_linhas - total_aprovadas),
        origem_execucao="delta_ans_streaming",
    )
    await registrar_job_carga(
        dataset_codigo=fonte.dataset_codigo,
        hash_arquivo=hash_arquivo,
        status=status_lote,
        total_processado=total_aprovadas,
        total_erro=max(0, total_linhas - total_aprovadas),
        camada="bronze",
    )
    return {
        "status": "carregado",
        "lote_id": lote_id,
        "tabela_destino": fonte.dataset_codigo,
        "total_registros": total_aprovadas,
    }


async def _processar_fonte(
    fonte: FonteDelta,
    *,
    normalizar: bool = True,
    direto: bool = False,
) -> dict:
    payload: dict[str, str] = {}
    try:
        coluna_periodo = coluna_periodo_dataset(fonte.dataset_codigo)
        if coluna_periodo and await dataset_periodo_ja_carregado(
            fonte.dataset_codigo,
            fonte.competencia,
        ):
            await _registrar_tentativa(
                dag_id=f"ingestao_delta_ans.{fonte.dataset_codigo}",
                task_id="verificar_periodo_existente",
                dominio=fonte.familia,
                dataset_codigo=fonte.dataset_codigo,
                fonte_url=fonte.url,
                arquivo_nome=fonte.nome_arquivo,
                competencia=_inteiro(_competencia_iso(fonte.competencia)),
                status="ARQUIVO_JA_CARREGADO",
                motivo=(
                    f"Periodo {fonte.competencia} ja existe em bronze; "
                    "carga idempotente ignorada antes do download."
                ),
                tabela_destino=fonte.dataset_codigo,
            )
            return {
                "status": "carregado",
                "lote_id": None,
                "tabela_destino": fonte.dataset_codigo,
                "total_registros": 0,
                "arquivo": fonte.nome_arquivo,
                "motivo": "periodo_ja_carregado",
            }
        payload = await _baixar_fonte(fonte)
        await _registrar_arquivo_fonte(fonte, payload, "baixado")
        path = Path(payload["path"])
        if direto:
            resultado = await _carregar_direto_streaming(
                fonte=fonte,
                path=path,
                hash_arquivo=payload["hash_arquivo"],
                normalizar=normalizar,
            )
        else:
            registros = _ler_arquivo(path)
            if normalizar:
                registros = _normalizar_registros(
                    fonte.dataset_codigo,
                    registros,
                    fonte.competencia,
                    fonte.nome_arquivo,
                )
            if direto:
                resultado = await _carregar_direto(
                    fonte.dataset_codigo,
                    fonte.nome_arquivo,
                    payload["hash_arquivo"],
                    registros,
                )
            else:
                resultado = await processar_arquivo_bruto(
                    dataset_codigo=fonte.dataset_codigo,
                    nome_arquivo=fonte.nome_arquivo,
                    hash_arquivo=payload["hash_arquivo"],
                    registros=registros,
                )
        status = "carregado" if resultado.get("status") == "carregado" else "erro_parser"
        await _registrar_arquivo_fonte(fonte, payload, status, str(resultado.get("motivos") or ""))
        return {**resultado, "arquivo": fonte.nome_arquivo}
    except Exception as exc:
        erro = str(exc)[:500]
        status = "erro_carga" if payload else "erro_download"
        await _registrar_arquivo_fonte(fonte, payload, status, erro)
        raise


async def _ingerir_fontes(
    *,
    dataset_codigo: str,
    familia: str,
    competencia: str,
    base_url: str,
    padrao: str | None = None,
    direto: bool = False,
) -> dict:
    try:
        fontes = await _resolver_fontes(
            dataset_codigo=dataset_codigo,
            familia=familia,
            competencia=competencia,
            base_url=base_url,
            padrao=padrao,
        )
    except (RuntimeError, httpx.HTTPStatusError) as exc:
        mensagem = str(exc)
        if isinstance(exc, RuntimeError) and "Nenhum arquivo tabular encontrado" not in mensagem:
            raise
        await _registrar_tentativa(
            dag_id=f"ingestao_delta_ans.{dataset_codigo}",
            task_id="resolver_fontes",
            dominio=familia,
            dataset_codigo=dataset_codigo,
            fonte_url=base_url,
            competencia=_inteiro(_competencia_iso(competencia)),
            status="FONTE_INDISPONIVEL",
            motivo="Fonte ANS sem arquivo tabular disponivel para a carga solicitada.",
            erro_tipo=type(exc).__name__,
            erro_mensagem=mensagem[:500],
        )
        return {
            "status": "sem_fonte",
            "dataset_codigo": dataset_codigo,
            "arquivos": 0,
            "total_registros": 0,
            "resultados": [],
            "motivo": mensagem,
        }
    resultados = []
    for fonte in fontes:
        resultados.append(await _processar_fonte(fonte, direto=direto))
    total = sum(int(item.get("total_registros") or 0) for item in resultados)
    return {
        "status": (
            "carregado"
            if all(r.get("status") == "carregado" for r in resultados)
            else "parcial"
        ),
        "dataset_codigo": dataset_codigo,
        "arquivos": len(resultados),
        "total_registros": total,
        "resultados": resultados,
    }


# ---------------------------------------------------------------------------
# Onda 1 - Produtos e Planos
# ---------------------------------------------------------------------------


async def executar_ingestao_produto_caracteristica(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="produto_caracteristica",
        familia="produtos_planos",
        competencia=competencia,
        base_url=_url("caracteristicas_produtos_saude_suplementar-008/"),
        padrao=r"pda-008-caracteristicas_produtos_saude_suplementar\.csv$",
        direto=True,
    )


async def executar_ingestao_produto_tabela_auxiliar(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="produto_tabela_auxiliar",
        familia="produtos_planos",
        competencia=competencia,
        base_url=_url("caracteristicas_produtos_saude_suplementar-008/"),
        padrao=r"pda-008-tabela_auxiliar_de_detalhamento_de_municipios\.csv$",
        direto=True,
    )


async def executar_ingestao_historico_plano(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="historico_plano",
        familia="produtos_planos",
        competencia=competencia,
        base_url=_url("historico_planos_saude/"),
        padrao=r"HISTORICO_PLANOS\.csv$",
        direto=True,
    )


async def executar_ingestao_plano_servico_opcional(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="plano_servico_opcional",
        familia="produtos_planos",
        competencia=competencia,
        base_url=_url("servicos_opcionais_planos_saude/"),
        padrao=r"planos_servicos_opcionais\.csv$",
        direto=True,
    )


async def executar_ingestao_quadro_auxiliar_corresponsabilidade(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="quadro_auxiliar_corresponsabilidade",
        familia="produtos_planos",
        competencia=competencia,
        base_url=_url("quadros_auxiliares_de_corresponsabilidade/"),
        padrao=r"QUADRO.*CORRESPONSABILIDADE.*\.csv$",
        direto=True,
    )


# ---------------------------------------------------------------------------
# Onda 2 - TUSS Oficial
# ---------------------------------------------------------------------------


async def executar_ingestao_tuss_oficial(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="tuss_oficial",
        familia="tuss",
        competencia=competencia,
        base_url=_url("terminologia_unificada_saude_suplementar_TUSS/TUSS.zip"),
        direto=True,
    )


# ---------------------------------------------------------------------------
# Onda 3 - TISS Subfamilias
# ---------------------------------------------------------------------------


async def executar_ingestao_tiss_ambulatorial(competencia: str) -> dict:
    fontes = await _resolver_fontes_tiss(
        dataset_codigo="tiss_ambulatorial",
        familia="tiss",
        competencia=competencia,
        subfamilia="AMBULATORIAL",
        marcador_nome="AMB",
    )
    resultados = [await _processar_fonte(fonte, direto=True) for fonte in fontes]
    return {"status": "carregado", "dataset_codigo": "tiss_ambulatorial", "resultados": resultados}


async def executar_ingestao_tiss_hospitalar(competencia: str) -> dict:
    fontes = await _resolver_fontes_tiss(
        dataset_codigo="tiss_hospitalar",
        familia="tiss",
        competencia=competencia,
        subfamilia="HOSPITALAR",
        marcador_nome="HOSP",
    )
    resultados = [await _processar_fonte(fonte, direto=True) for fonte in fontes]
    return {"status": "carregado", "dataset_codigo": "tiss_hospitalar", "resultados": resultados}


async def executar_ingestao_tiss_dados_plano(competencia: str) -> dict:
    fontes = await _resolver_fontes_tiss(
        dataset_codigo="tiss_dados_plano",
        familia="tiss",
        competencia=competencia,
        subfamilia="DADOS_DE_PLANOS",
        marcador_nome="DADOS",
    )
    resultados = [await _processar_fonte(fonte, direto=True) for fonte in fontes]
    return {"status": "carregado", "dataset_codigo": "tiss_dados_plano", "resultados": resultados}


# ---------------------------------------------------------------------------
# Onda 4 - SIP
# ---------------------------------------------------------------------------


async def executar_ingestao_sip_mapa_assistencial(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="sip_mapa_assistencial",
        familia="sip",
        competencia=competencia,
        base_url=_url("SIP/"),
        padrao=r"sip_mapa_assistencial_20\d{4}\.csv$",
        direto=True,
    )


# ---------------------------------------------------------------------------
# Onda 5 - Ressarcimento SUS
# ---------------------------------------------------------------------------


async def executar_ingestao_ressarcimento_beneficiario_abi(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ressarcimento_beneficiario_abi",
        familia="ressarcimento_sus",
        competencia=competencia,
        base_url=_url("beneficiarios_identificados_sus_abi/"),
    )


async def executar_ingestao_ressarcimento_sus_operadora_plano(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ressarcimento_sus_operadora_plano",
        familia="ressarcimento_sus",
        competencia=competencia,
        base_url=_url("dados_ressarcimento_SUS_operadora_planos_saude/"),
    )


async def executar_ingestao_ressarcimento_hc(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ressarcimento_hc",
        familia="ressarcimento_sus",
        competencia=competencia,
        base_url=_url("hc_ressarcimento_sus/"),
    )


async def executar_ingestao_ressarcimento_cobranca_arrecadacao(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ressarcimento_cobranca_arrecadacao",
        familia="ressarcimento_sus",
        competencia=competencia,
        base_url=_url("ressarcimento_ao_SUS_cobranca_arrecadacao/"),
    )


async def executar_ingestao_ressarcimento_indice_pagamento(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ressarcimento_indice_pagamento",
        familia="ressarcimento_sus",
        competencia=competencia,
        base_url=_url("ressarcimento_ao_SUS_indice_efetivo_pagamento/"),
    )


# ---------------------------------------------------------------------------
# Onda 6 - Precificacao, NTRP e Reajustes
# ---------------------------------------------------------------------------


async def executar_ingestao_ntrp_area_comercializacao(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ntrp_area_comercializacao",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("area_comercializacao_planos_ntrp/"),
    )


async def executar_ingestao_painel_precificacao(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="painel_precificacao",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("painel_precificacao-053/"),
        direto=True,
    )


async def executar_ingestao_percentual_reajuste_agrupamento(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="percentual_reajuste_agrupamento",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("percentuais_de_reajuste_de_agrupamento-055/"),
    )


async def executar_ingestao_ntrp_vcm_faixa_etaria(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="ntrp_vcm_faixa_etaria",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("nota_tecnica_ntrp_vcm_faixa_etaria/"),
    )


async def executar_ingestao_valor_comercial_medio_municipio(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="valor_comercial_medio_municipio",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("valor_comercial_medio_por_municipio_NTRP-054/"),
    )


async def executar_ingestao_faixa_preco(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="faixa_preco",
        familia="precificacao_ntrp",
        competencia=competencia,
        base_url=_url("faixa_de_preco/"),
    )


# ---------------------------------------------------------------------------
# Onda 7 - Rede, Prestadores e Acreditacao
# ---------------------------------------------------------------------------


async def executar_ingestao_operadora_cancelada(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="operadora_cancelada",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("operadoras_de_plano_de_saude_canceladas/"),
    )


async def executar_ingestao_operadora_acreditada(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="operadora_acreditada",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("operadoras_acreditadas/"),
    )


async def executar_ingestao_prestador_acreditado(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="prestador_acreditado",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("prestadores_acreditados/"),
    )


async def executar_ingestao_produto_prestador_hospitalar(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="produto_prestador_hospitalar",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("produtos_e_prestadores_hospitalares/"),
        direto=True,
    )


async def executar_ingestao_operadora_prestador_nao_hospitalar(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="operadora_prestador_nao_hospitalar",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("operadoras_e_prestadores_nao_hospitalares/"),
        direto=True,
    )


async def executar_ingestao_solicitacao_alteracao_rede_hospitalar(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="solicitacao_alteracao_rede_hospitalar",
        familia="rede_prestadores",
        competencia=competencia,
        base_url=_url("solicitacoes_alteracao_rede_hospitalar-046/"),
    )


# ---------------------------------------------------------------------------
# Onda 8 - Regulatorios Complementares
# ---------------------------------------------------------------------------


async def executar_ingestao_penalidade_operadora(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="penalidade_operadora",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("penalidades_aplicadas_a_operadoras/"),
    )


async def executar_ingestao_monitoramento_garantia_atendimento(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="monitoramento_garantia_atendimento",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("monitoramento_garantia_atendimento/"),
    )


async def executar_ingestao_peona_sus(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="peona_sus",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("peona_sus/"),
    )


async def executar_ingestao_promoprev(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="promoprev",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("promoprev-052/"),
    )


async def executar_ingestao_rpc(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="rpc",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("RPC/"),
    )


async def executar_ingestao_iap(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="iap",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("IAP/"),
    )


async def executar_ingestao_pfa(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="pfa",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("PFA/"),
    )


async def executar_ingestao_programa_qualificacao_institucional(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="programa_qualificacao_institucional",
        familia="regulatorios_complementares",
        competencia=competencia,
        base_url=_url("programa_de_qualificacao_institucional/"),
    )


# ---------------------------------------------------------------------------
# Onda 9 - Beneficiarios e Cobertura
# ---------------------------------------------------------------------------


async def executar_ingestao_beneficiario_regiao_geografica(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="beneficiario_regiao_geografica",
        familia="beneficiarios_cobertura",
        competencia=competencia,
        base_url=_url("dados_de_beneficiarios_por_regiao_geografica/"),
    )


async def executar_ingestao_beneficiario_informacao_consolidada(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="beneficiario_informacao_consolidada",
        familia="beneficiarios_cobertura",
        competencia=competencia,
        base_url=_url("informacoes_consolidadas_de_beneficiarios-024/"),
    )


async def executar_ingestao_taxa_cobertura_plano(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="taxa_cobertura_plano",
        familia="beneficiarios_cobertura",
        competencia=competencia,
        base_url=_url("taxa_de_cobertura_de_planos_de_saude-047/"),
    )


# ---------------------------------------------------------------------------
# Onda 10 - Prudencial, Regime Especial, Taxa Resolutividade
# ---------------------------------------------------------------------------


def _prudencial(row: dict[str, str], competencia: str, _: str) -> dict:
    dt = str(row.get("DT_TRIMESTRE_REFERENCIA") or "").strip()
    trim = ""
    if len(dt) >= 7:
        ano = dt[:4]
        mes = int(dt[5:7]) if dt[5:7].isdigit() else 0
        trim_num = ((mes - 1) // 3 + 1) if mes else 1
        trim = f"{trim_num}T{ano}"
    return {
        "trimestre": trim or competencia,
        "registro_ans": row.get("REGISTRO_OPERADORA") or "",
        "situacao_prudencial": row.get("TP_CLASSIFICACAO") or "",
        "margem_solvencia": None,
        "capital_minimo_requerido": None,
        "capital_disponivel": None,
        "indice_liquidez": None,
        "fonte_publicacao": "ans_ftp",
    }


def _regime_especial(row: dict[str, str], competencia: str, _: str) -> dict:
    ano = str(row.get("ANO") or "").strip()
    return {
        "trimestre": f"1T{ano}" if ano else competencia,
        "registro_ans": str(row.get("REGISTRO_OPERADORA") or "").strip(),
        "tipo_regime": str(row.get("RESOLUCAO_OPERACIONAL") or "").strip(),
        "data_inicio": _data_iso(row.get("DATA_PUBLICACAO")),
        "data_fim": None,
        "descricao": str(row.get("RAZAO_SOCIAL") or "").strip(),
        "fonte_publicacao": "ans_ftp",
    }


def _taxa_resolutividade(row: dict[str, str], competencia: str, _: str) -> dict:
    comp_str = str(row.get("CD_COMPETENCIA") or competencia).strip()
    return {
        "trimestre": _competencia_iso(comp_str),
        "registro_ans": str(row.get("CD_REGISTRO_ANS") or "").strip(),
        "modalidade": str(row.get("TP_NATUREZA") or "").strip(),
        "taxa_resolutividade": _decimal(
            str(row.get("VL_TR") or "0").replace(",", ".")
        ),
        "n_reclamacao_resolvida": _inteiro(row.get("NR_NUMERADOR")),
        "n_reclamacao_total": _inteiro(row.get("NR_DENOMINADOR")),
        "fonte_publicacao": "ans_ftp",
    }


def _glosa(row: dict[str, str], competencia: str, _: str) -> dict:
    periodo = str(row.get("CD_PERIODO") or competencia).strip()
    return {
        "competencia": _competencia_iso(periodo.replace("-", "")),
        "registro_ans": str(row.get("REGISTRO_OPERADORA") or "").strip(),
        "tipo_glosa": str(row.get("CD_INDICADOR") or row.get("NM_INDICADOR") or "").strip(),
        "qt_glosa": _inteiro(row.get("QT_GLOSA") or row.get("NR_GUIAS_SEM_RETORNO")),
        "valor_glosa": _decimal(
            str(row.get("VL_GLOSA") or row.get("VL_GUIAS_SEM_RETORNO") or "0").replace(",", ".")
        ),
        "valor_faturado": _decimal(
            str(row.get("VL_FATURADO") or "0").replace(",", ".")
        ),
        "fonte_publicacao": "ans_ftp",
    }


def _diops(row: dict[str, str], competencia: str, arquivo_origem: str) -> dict:
    dt = str(row.get("DATA") or "").strip()
    trim = ""
    if len(dt) >= 7:
        # Suporta YYYY-MM-DD e DD/MM/YYYY (formato antigo pre-2024)
        if len(dt) >= 10 and dt[2] == "/" and dt[5] == "/":
            # DD/MM/YYYY → reordenar para extração consistente
            ano = dt[6:10]
            mes = int(dt[3:5]) if dt[3:5].isdigit() else 0
        else:
            ano = dt[:4]
            mes = int(dt[5:7]) if dt[5:7].isdigit() else 0
        trim_num = ((mes - 1) // 3 + 1) if mes else 1
        trim = f"{trim_num}T{ano}"
    return {
        "trimestre": trim or competencia,
        "registro_ans": str(row.get("REG_ANS") or "").strip(),
        "cnpj": str(row.get("CNPJ") or "").strip(),
        "ativo_total": _decimal(row.get("ATIVO_TOTAL") or row.get("VL_SALDO_FINAL")),
        "passivo_total": None,
        "patrimonio_liquido": None,
        "receita_total": None,
        "despesa_total": None,
        "resultado_periodo": None,
        "provisao_tecnica": None,
        "margem_solvencia_calculada": None,
        "fonte_publicacao": "ans_ftp_diops",
    }


_NORMALIZADORES.update({
    "prudencial_operadora_trimestral": _prudencial,
    "regime_especial_operadora_trimestral": _regime_especial,
    "taxa_resolutividade_operadora_trimestral": _taxa_resolutividade,
    "glosa_operadora_mensal": _glosa,
    "diops_operadora_trimestral": _diops,
})


async def executar_ingestao_prudencial_operadora(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="prudencial_operadora_trimestral",
        familia="financeiro",
        competencia=competencia,
        base_url=_url("classificacao_prudencial-056/pda-056-classificacao_prudencial.csv"),
        direto=True,
    )


async def executar_ingestao_regime_especial_direcao_tecnica(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="regime_especial_operadora_trimestral",
        familia="regulatorio",
        competencia=competencia,
        base_url=_url("regimes_especiais_direcao_tecnica/pda-040-regimes_especiais_direcao_tecnica.csv"),
        direto=True,
    )


async def executar_ingestao_taxa_resolutividade_operadora(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="taxa_resolutividade_operadora_trimestral",
        familia="regulatorio",
        competencia=competencia,
        base_url=_url("taxa_de_resolutividade/pda-048-taxa_de_resolutividade.csv"),
        direto=True,
    )


async def executar_ingestao_glosa_operadora(competencia: str) -> dict:
    return await _ingerir_fontes(
        dataset_codigo="glosa_operadora_mensal",
        familia="financeiro",
        competencia=competencia,
        base_url=_url("painel_de_glosas-057/dados/"),
        direto=True,
    )


async def executar_ingestao_diops_operadora(competencia: str) -> dict:
    ano = (competencia or "")[:4] or str(date.today().year - 1)
    ano_fechado_anterior = str(date.today().year - 1)
    if not re.fullmatch(r"20\d{2}", ano) or int(ano) >= date.today().year:
        ano = str(date.today().year - 1)
    try:
        return await _ingerir_fontes(
            dataset_codigo="diops_operadora_trimestral",
            familia="financeiro",
            competencia=competencia,
            base_url=_url(f"demonstracoes_contabeis/{ano}/"),
            padrao=r"\dT20\d{2}\.zip$",
            direto=True,
        )
    except Exception:
        if ano == ano_fechado_anterior:
            raise
        return await _ingerir_fontes(
            dataset_codigo="diops_operadora_trimestral",
            familia="financeiro",
            competencia=competencia,
            base_url=_url(f"demonstracoes_contabeis/{ano_fechado_anterior}/"),
            padrao=r"\dT20\d{2}\.zip$",
            direto=True,
        )
