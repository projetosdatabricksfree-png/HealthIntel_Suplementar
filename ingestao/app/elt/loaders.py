from __future__ import annotations

import csv
import io
import json
import zipfile
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal

TABULAR_EXTENSOES = {"csv", "txt"}


def _detectar_encoding(path: Path) -> str:
    amostra = path.read_bytes()[:8192]
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            amostra.decode(encoding)
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


def _iter_csv(path: Path, *, batch_size: int = 5000) -> Iterator[list[tuple[int, dict]]]:
    encoding = _detectar_encoding(path)
    with path.open("r", encoding=encoding, newline="") as arquivo:
        amostra = arquivo.read(8192)
        arquivo.seek(0)
        reader = csv.DictReader(arquivo, dialect=_detectar_dialect(amostra))
        batch: list[tuple[int, dict]] = []
        for linha_origem, row in enumerate(reader, start=2):
            batch.append((linha_origem, dict(row)))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


def _iter_zip_csv(path: Path, *, batch_size: int = 5000) -> Iterator[list[tuple[int, dict]]]:
    with zipfile.ZipFile(path) as pacote:
        nomes = [
            nome
            for nome in pacote.namelist()
            if not nome.endswith("/") and nome.lower().endswith((".csv", ".txt"))
        ]
        for nome in nomes:
            with pacote.open(nome, "r") as binario:
                wrapper = io.TextIOWrapper(binario, encoding="utf-8-sig", newline="")
                amostra = wrapper.read(8192)
                wrapper.seek(0)
                reader = csv.DictReader(wrapper, dialect=_detectar_dialect(amostra))
                batch = []
                for linha_origem, row in enumerate(reader, start=2):
                    batch.append((linha_origem, dict(row)))
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
        if batch:
            yield batch


def _zip_tem_csv(path: Path) -> bool:
    with zipfile.ZipFile(path) as pacote:
        return any(
            not nome.endswith("/") and nome.lower().endswith((".csv", ".txt"))
            for nome in pacote.namelist()
        )


async def registrar_arquivo_generico(arquivo: dict, *, status_parser: str = "sem_parser") -> int:
    sql = text(
        """
        insert into bruto_ans.ans_arquivo_generico (
            dataset_codigo, familia, url, arquivo_origem, hash_arquivo,
            caminho_landing, tipo_arquivo, tamanho_bytes, status_parser
        ) values (
            :dataset_codigo, :familia, :url, :arquivo_origem, :hash_arquivo,
            :caminho_landing, :tipo_arquivo, :tamanho_bytes, :status_parser
        )
        """
    )
    async with SessionLocal() as session:
        await session.execute(
            sql,
            {
                "dataset_codigo": arquivo["dataset_codigo"],
                "familia": arquivo["familia"],
                "url": arquivo["url"],
                "arquivo_origem": arquivo["nome_arquivo"],
                "hash_arquivo": arquivo["hash_arquivo"],
                "caminho_landing": arquivo["caminho_landing"],
                "tipo_arquivo": arquivo.get("tipo_arquivo") or arquivo.get("extensao"),
                "tamanho_bytes": arquivo.get("tamanho_bytes"),
                "status_parser": status_parser,
            },
        )
        await session.commit()
    return 1


async def _inserir_linhas_genericas(arquivo: dict, batch: list[tuple[int, dict]]) -> int:
    if not batch:
        return 0
    sql = text(
        """
        insert into bruto_ans.ans_linha_generica (
            dataset_codigo, familia, arquivo_origem, hash_arquivo, linha_origem, dados
        ) values (
            :dataset_codigo, :familia, :arquivo_origem, :hash_arquivo,
            :linha_origem, cast(:dados as jsonb)
        )
        """
    )
    params = [
        {
            "dataset_codigo": arquivo["dataset_codigo"],
            "familia": arquivo["familia"],
            "arquivo_origem": arquivo["nome_arquivo"],
            "hash_arquivo": arquivo["hash_arquivo"],
            "linha_origem": linha_origem,
            "dados": json.dumps(dados, ensure_ascii=False, default=str),
        }
        for linha_origem, dados in batch
    ]
    async with SessionLocal() as session:
        await session.execute(sql, params)
        await session.commit()
    return len(params)


async def _marcar_status_arquivo(
    arquivo_id: str,
    status: str,
    erro_mensagem: str | None = None,
) -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                update plataforma.arquivo_fonte_ans
                set status = :status,
                    erro_mensagem = :erro_mensagem,
                    updated_at = now()
                where id = :id
                """
            ),
            {"id": arquivo_id, "status": status, "erro_mensagem": erro_mensagem},
        )
        await session.commit()


async def carregar_arquivo_tabular_generico(arquivo: dict) -> dict:
    path = Path(str(arquivo["caminho_landing"]))
    extensao = str(arquivo.get("extensao") or path.suffix.removeprefix(".")).lower()
    iterador = _iter_zip_csv(path) if extensao == "zip" else _iter_csv(path)
    total_linhas = 0
    try:
        for batch in iterador:
            total_linhas += await _inserir_linhas_genericas(arquivo, batch)
        await _marcar_status_arquivo(str(arquivo["id"]), "carregado")
    except Exception as exc:
        await _marcar_status_arquivo(str(arquivo["id"]), "erro_carga", str(exc))
        raise
    return {
        "status": "carregado",
        "linhas_carregadas": total_linhas,
        "dataset_codigo": arquivo["dataset_codigo"],
        "familia": arquivo["familia"],
    }


async def carregar_arquivo_ans(arquivo: dict) -> dict:
    path = Path(str(arquivo["caminho_landing"]))
    if not path.exists():
        msg = f"arquivo físico ausente na landing: {path}"
        await _marcar_status_arquivo(str(arquivo["id"]), "erro_carga", msg)
        return {
            "status": "erro_carga",
            "linhas_carregadas": 0,
            "dataset_codigo": arquivo["dataset_codigo"],
            "familia": arquivo["familia"],
            "erro": msg,
        }
    extensao = str(arquivo.get("extensao") or "").lower()
    tipo_arquivo = str(arquivo.get("tipo_arquivo") or "").lower()
    if extensao == "zip" and not _zip_tem_csv(path):
        await registrar_arquivo_generico(arquivo)
        await _marcar_status_arquivo(str(arquivo["id"]), "baixado_sem_parser")
        return {
            "status": "baixado_sem_parser",
            "linhas_carregadas": 0,
            "dataset_codigo": arquivo["dataset_codigo"],
            "familia": arquivo["familia"],
        }
    if extensao in TABULAR_EXTENSOES or extensao == "zip" or tipo_arquivo in {"tabular", "zip"}:
        return await carregar_arquivo_tabular_generico(arquivo)
    await registrar_arquivo_generico(arquivo)
    return {
        "status": "baixado_sem_parser",
        "linhas_carregadas": 0,
        "dataset_codigo": arquivo["dataset_codigo"],
        "familia": arquivo["familia"],
    }
