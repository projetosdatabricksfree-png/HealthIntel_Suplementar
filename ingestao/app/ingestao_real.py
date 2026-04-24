from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

from ingestao.app.config import get_settings
from ingestao.app.landing import baixar_arquivo
from ingestao.app.pipeline_bronze import processar_arquivo_bruto


def _detectar_encoding(conteudo: bytes) -> str:
    for encoding in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            conteudo.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("desconhecido", b"", 0, 1, "encoding nao suportado")


def _ler_csv_bytes(conteudo: bytes) -> list[dict[str, str]]:
    encoding = _detectar_encoding(conteudo)
    texto = conteudo.decode(encoding)
    amostra = texto[:4096]
    dialect = csv.Sniffer().sniff(amostra, delimiters=";,|,\t")
    reader = csv.DictReader(io.StringIO(texto), dialect=dialect)
    return [dict(row) for row in reader]


async def executar_ingestao_cadop(competencia: str) -> dict:
    settings = get_settings()
    arquivo = await baixar_arquivo("cadop", competencia, settings.ans_cadop_url)
    registros = _ler_csv_bytes(Path(arquivo["path"]).read_bytes())
    for registro in registros:
        registro.setdefault("competencia", competencia)
    return await processar_arquivo_bruto(
        dataset_codigo="cadop",
        nome_arquivo=arquivo["arquivo_origem"],
        hash_arquivo=arquivo["hash_arquivo"],
        registros=registros,
    )


async def executar_ingestao_sib_uf(competencia: str, uf: str) -> dict:
    settings = get_settings()
    url = f"{settings.ans_sib_base_url.rstrip('/')}/sib_ativo_{uf.upper()}.zip"
    arquivo = await baixar_arquivo("sib_operadora", competencia, url)
    registros: list[dict[str, str]] = []
    with zipfile.ZipFile(arquivo["path"]) as pacote:
        for nome in pacote.namelist():
            if not nome.lower().endswith((".csv", ".txt")):
                continue
            registros.extend(_ler_csv_bytes(pacote.read(nome)))
    for registro in registros:
        registro.setdefault("competencia", competencia)
    return await processar_arquivo_bruto(
        dataset_codigo="sib_operadora",
        nome_arquivo=arquivo["arquivo_origem"],
        hash_arquivo=arquivo["hash_arquivo"],
        registros=registros,
    )
