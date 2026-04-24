from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import urlparse

EXTENSOES_TABULARES = {".csv", ".txt"}
EXTENSOES_ZIP = {".zip"}
EXTENSOES_DOCUMENTO = {".pdf", ".xls", ".xlsx", ".json", ".xml"}
EXTENSOES_SUPORTADAS = EXTENSOES_TABULARES | EXTENSOES_ZIP | EXTENSOES_DOCUMENTO

FAMILIAS_PRIORITARIAS = {
    "cadop",
    "sib",
    "tiss",
    "sip",
    "igr",
    "idss",
    "nip",
    "diops",
    "rpc",
    "caderno_ss",
    "plano",
}


def _normalizar_segmento(valor: str) -> str:
    return (
        valor.lower()
        .replace("%20", "_")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("__", "_")
    )


def _inferir_familia(caminho: str) -> str:
    caminho_norm = _normalizar_segmento(caminho)
    regras = [
        ("operadoras_de_plano_de_saude_ativas", "cadop"),
        ("relatorio_cadop", "cadop"),
        ("dados_de_beneficiarios", "sib"),
        ("sib_", "sib"),
        ("/tiss/", "tiss"),
        ("tiss", "tiss"),
        ("/sip/", "sip"),
        ("sip", "sip"),
        ("/igr/", "igr"),
        ("igr", "igr"),
        ("idss", "idss"),
        ("nip", "nip"),
        ("reclam", "nip"),
        ("diops", "diops"),
        ("economico", "diops"),
        ("financeir", "diops"),
        ("/rpc/", "rpc"),
        ("ressarcimento", "rpc"),
        ("caderno_ss", "caderno_ss"),
        ("caderno", "caderno_ss"),
        ("plano", "plano"),
    ]
    for marcador, familia in regras:
        if marcador in caminho_norm:
            return familia
    return "desconhecido"


def _inferir_dataset(caminho: str, nome_arquivo: str | None, familia: str) -> str:
    caminho_norm = _normalizar_segmento(caminho)
    nome_norm = _normalizar_segmento(nome_arquivo or "")

    if familia == "cadop":
        return "cadop_operadoras_ativas"
    if familia == "sib":
        if "municipio" in caminho_norm or "municipio" in nome_norm:
            return "sib_ativo_municipio"
        return "sib_ativo_uf"
    if familia == "tiss":
        if "ambulatorial" in caminho_norm:
            return "tiss_ambulatorial"
        if "hospitalar" in caminho_norm:
            return "tiss_hospitalar"
        if "dicionario" in caminho_norm or "dicion" in caminho_norm:
            return "tiss_dicionario"
        return "tiss_generico"
    if familia == "sip":
        return "sip_generico"
    if familia == "igr":
        return "igr_generico"
    if familia == "idss":
        return "idss_generico"
    if familia == "nip":
        return "nip_reclamacao_generico"
    if familia == "diops":
        return "diops_economico_financeiro"
    if familia == "rpc":
        return "rpc_generico"
    if familia == "caderno_ss":
        return "caderno_ss_generico"
    if familia == "plano":
        return "plano_generico"
    return "ans_pda_generico"


def _inferir_tipo_arquivo(extensao: str) -> str:
    if extensao in EXTENSOES_TABULARES:
        return "tabular"
    if extensao in EXTENSOES_ZIP:
        return "zip"
    if extensao in EXTENSOES_DOCUMENTO:
        return extensao.removeprefix(".")
    if not extensao:
        return "diretorio"
    return "desconhecido"


def classificar_fonte_ans(url: str, nome_arquivo: str | None = None) -> dict:
    parsed = urlparse(url)
    path = PurePosixPath(parsed.path)
    nome = nome_arquivo or (path.name if path.name else None)
    extensao = path.suffix.lower() if nome else ""
    familia = _inferir_familia(parsed.path)
    dataset_codigo = _inferir_dataset(parsed.path, nome, familia)
    tipo_arquivo = _inferir_tipo_arquivo(extensao)
    escopo = "sector_core" if familia in FAMILIAS_PRIORITARIAS else "all_ftp"
    prioridade = 10 if familia in {"cadop", "sib", "tiss"} else 30
    if familia not in FAMILIAS_PRIORITARIAS:
        prioridade = 100

    return {
        "familia": familia,
        "dataset_codigo": dataset_codigo,
        "tipo_arquivo": tipo_arquivo,
        "extensao": extensao.removeprefix("."),
        "escopo": escopo,
        "prioridade": prioridade,
    }


def fonte_pertence_ao_escopo(fonte: dict, escopo: str) -> bool:
    if escopo == "all_ftp":
        return True
    return str(fonte.get("escopo") or "") == "sector_core"
