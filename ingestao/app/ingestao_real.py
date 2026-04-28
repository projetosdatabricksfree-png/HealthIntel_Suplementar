from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from ingestao.app.config import get_settings
from ingestao.app.identificar_layout import identificar_layout
from ingestao.app.landing import baixar_arquivo
from ingestao.app.pipeline_bronze import (
    processar_arquivo_bruto,
    processar_arquivo_bruto_streaming,
)

# ---------------------------------------------------------------------------
# Legacy helpers (preserved for demo/seeds/small files)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Legacy flows (preserved — used by seeds/demo/small files)
# ---------------------------------------------------------------------------

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
    from ingestao.app.janela_carga import (
        assegurar_dentro_da_janela_ou_falhar,
        garantir_particoes_dataset,
        normalizar_competencia,
        obter_janela,
    )

    janela = await obter_janela("sib_operadora")
    competencia_normalizada = normalizar_competencia(competencia)
    await garantir_particoes_dataset(janela)
    await assegurar_dentro_da_janela_ou_falhar(
        competencia_normalizada,
        janela,
        permitir_historico=False,
    )
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


# ---------------------------------------------------------------------------
# Streaming / Batch helpers (new — for real heavy ingestion)
# ---------------------------------------------------------------------------

def iterar_csv_zip(
    path_zip: Path,
    *,
    encoding: str | None = None,
    batch_size: int = 5000,
) -> Iterator[list[dict[str, str]]]:
    """
    Yield batches de dicts de um CSV dentro de ZIP sem carregar todo o arquivo em memória.

    Regras:
    - Abrir o ZIP com zipfile.ZipFile.
    - Selecionar o primeiro arquivo interno com extensão .csv, .txt ou similar.
    - Abrir o membro com pacote.open(nome), não usar pacote.read(nome).
    - Usar io.TextIOWrapper para decodificar stream.
    - Usar csv.DictReader.
    - Acumular somente até batch_size e yield.
    - Ao final, yield do batch residual.
    """
    enc = encoding or "utf-8-sig"

    with zipfile.ZipFile(path_zip) as pacote:
        candidatos = [
            nome for nome in pacote.namelist()
            if not nome.endswith("/")
            and nome.lower().endswith((".csv", ".txt"))
        ]
        if not candidatos:
            raise ValueError(f"Nenhum CSV/TXT encontrado no ZIP: {path_zip}")

        nome_csv = candidatos[0]
        with pacote.open(nome_csv, "r") as binario:
            texto = io.TextIOWrapper(binario, encoding=enc, newline="")
            sample = texto.read(4096)
            texto.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
            except csv.Error:
                dialect = csv.excel
                dialect.delimiter = ";"

            reader = csv.DictReader(texto, dialect=dialect)
            batch: list[dict[str, str]] = []

            for row in reader:
                batch.append(dict(row))
                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch


# ---------------------------------------------------------------------------
# Streaming SIB flow
# ---------------------------------------------------------------------------

async def executar_ingestao_sib_uf_streaming(
    competencia: str,
    uf: str,
    *,
    batch_size: int | None = None,
) -> dict:
    """
    Fluxo SIB streaming:
    - baixa ZIP;
    - calcula hash;
    - verifica duplicidade;
    - cria 1 lote por arquivo;
    - processa N batches;
    - fecha o lote com contadores acumulados;
    - segunda execução deve virar ignorado_duplicata.
    """
    from ingestao.app.janela_carga import (
        assegurar_dentro_da_janela_ou_falhar,
        garantir_particoes_dataset,
        normalizar_competencia,
        obter_janela,
    )

    janela = await obter_janela("sib_operadora")
    competencia_normalizada = normalizar_competencia(competencia)
    await garantir_particoes_dataset(janela)
    await assegurar_dentro_da_janela_ou_falhar(
        competencia_normalizada,
        janela,
        permitir_historico=False,
    )
    settings = get_settings()
    bs = batch_size or settings.ans_sib_batch_size
    url = f"{settings.ans_sib_base_url.rstrip('/')}/sib_ativo_{uf.upper()}.zip"

    arquivo = await baixar_arquivo("sib_operadora", competencia, url)
    path_zip = Path(arquivo["path"])
    hash_arquivo = arquivo["hash_arquivo"]
    nome_arquivo = arquivo["arquivo_origem"]

    # Check for duplicate before processing
    from sqlalchemy import text

    from ingestao.app.carregar_postgres import SessionLocal, registrar_lote_ingestao

    async with SessionLocal() as session:
        dup_result = await session.execute(
            text("""
                select 1
                from plataforma.lote_ingestao
                where dataset = :dataset
                  and hash_arquivo = :hash_arquivo
                  and status in ('sucesso', 'sucesso_com_alertas')
                limit 1
            """),
            {"dataset": "sib_operadora", "hash_arquivo": hash_arquivo},
        )
        duplicado = dup_result.scalar_one_or_none() is not None

    if duplicado:
        lote_id = str(uuid4())
        await registrar_lote_ingestao(
            lote_id=lote_id,
            dataset_codigo="sib_operadora",
            competencia=competencia,
            arquivo_origem=nome_arquivo,
            hash_arquivo=hash_arquivo,
            hash_estrutura=None,
            versao_layout=None,
            status="ignorado_duplicata",
            total_linhas_raw=0,
            total_aprovadas=0,
            total_quarentena=0,
            origem_execucao="streaming_sib",
            erro_mensagem=(
                "Lote duplicado rejeitado por hash_arquivo "
                "com carga anterior bem-sucedida."
            ),
        )
        return {
            "status": "ignorado_duplicata",
            "lote_id": lote_id,
            "hash_arquivo": hash_arquivo,
            "uf": uf,
        }

    # Detect columns from first batch to identify layout
    iterador = iterar_csv_zip(path_zip, batch_size=bs)
    primeiro_batch = next(iterador, None)
    if not primeiro_batch:
        return {
            "status": "vazio",
            "hash_arquivo": hash_arquivo,
            "uf": uf,
        }

    colunas_detectadas = list(primeiro_batch[0].keys())
    identificacao = await identificar_layout("sib_operadora", colunas_detectadas, nome_arquivo)

    if (
        not identificacao.compativel
        or not identificacao.layout_id
        or not identificacao.layout_versao_id
    ):
        from ingestao.app.carregar_postgres import registrar_quarentena

        quarentena_id = await registrar_quarentena(
            dataset_codigo="sib_operadora",
            arquivo_origem=nome_arquivo,
            hash_arquivo=hash_arquivo,
            hash_estrutura=identificacao.assinatura_colunas,
            motivo="; ".join(identificacao.motivos) or "Layout incompativel para o arquivo.",
        )
        return {
            "status": "quarentena",
            "quarentena_id": quarentena_id,
            "motivos": identificacao.motivos,
            "uf": uf,
        }

    lote_id = str(uuid4())



    def _batches_completos():
        yield primeiro_batch
        yield from iterador

    # Add competencia to each row
    def _batches_com_competencia():
        for batch in _batches_completos():
            for registro in batch:
                registro.setdefault("competencia", competencia)
            yield batch

    resultado = await processar_arquivo_bruto_streaming(
        dataset_codigo="sib_operadora",
        nome_arquivo=nome_arquivo,
        hash_arquivo=hash_arquivo,
        iterador_batches=_batches_com_competencia(),
        lote_id=lote_id,
        layout_id=identificacao.layout_id,
        layout_versao_id=identificacao.layout_versao_id,
        hash_estrutura=identificacao.assinatura_colunas,
        batch_size=bs,
        colunas_mapeadas=identificacao.colunas_mapeadas,
    )

    return {
        **resultado,
        "uf": uf,
        "hash_arquivo": hash_arquivo,
    }
