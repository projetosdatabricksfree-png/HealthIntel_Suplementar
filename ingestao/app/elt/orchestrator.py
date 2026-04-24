from __future__ import annotations

from ingestao.app.elt.catalogo import (
    listar_arquivos_para_carga,
    listar_fontes_para_download,
    salvar_fontes_descobertas,
)
from ingestao.app.elt.discovery import descobrir_fontes_ans
from ingestao.app.elt.downloader import baixar_fonte_ans
from ingestao.app.elt.loaders import carregar_arquivo_ans


def _normalizar_familias(familias: list[str] | None) -> list[str] | None:
    if not familias:
        return None
    return [familia.strip().lower() for familia in familias if familia.strip()]


async def executar_elt_discovery(
    *,
    escopo: str = "sector_core",
    max_depth: int = 5,
) -> dict:
    fontes = await descobrir_fontes_ans(max_depth=max_depth, escopo=escopo)
    salvas = await salvar_fontes_descobertas(fontes)
    familias = sorted({fonte["familia"] for fonte in fontes})
    return {
        "status": "ok",
        "escopo": escopo,
        "fontes_descobertas": len(fontes),
        "fontes_salvas": salvas,
        "familias": familias,
    }


async def executar_elt_extract_all(
    *,
    escopo: str = "sector_core",
    familias: list[str] | None = None,
    limite: int | None = None,
) -> dict:
    fontes = await listar_fontes_para_download(
        escopo=escopo,
        familias=_normalizar_familias(familias),
        limite=limite,
    )
    contadores = {
        "arquivos_baixados": 0,
        "arquivos_duplicados": 0,
        "arquivos_sem_parser": 0,
        "erros": 0,
    }
    resultados = []
    for fonte in fontes:
        resultado = await baixar_fonte_ans(fonte)
        resultados.append(resultado)
        status = resultado.get("status")
        if status == "baixado":
            contadores["arquivos_baixados"] += 1
        elif status == "ignorado_duplicata":
            contadores["arquivos_duplicados"] += 1
        elif status == "baixado_sem_parser":
            contadores["arquivos_sem_parser"] += 1
        elif str(status).startswith("erro"):
            contadores["erros"] += 1
    return {
        "status": "ok",
        "fontes_processadas": len(fontes),
        **contadores,
        "resultados": resultados,
    }


async def executar_elt_load_all(
    *,
    escopo: str = "sector_core",
    familias: list[str] | None = None,
    limite: int | None = None,
) -> dict:
    arquivos = await listar_arquivos_para_carga(
        escopo=escopo,
        familias=_normalizar_familias(familias),
        limite=limite,
    )
    contadores = {
        "arquivos_carregados": 0,
        "arquivos_sem_parser": 0,
        "linhas_carregadas": 0,
        "erros": 0,
    }
    resultados = []
    for arquivo in arquivos:
        try:
            resultado = await carregar_arquivo_ans(arquivo)
        except Exception as exc:
            contadores["erros"] += 1
            resultado = {
                "status": "erro_carga",
                "dataset_codigo": arquivo.get("dataset_codigo"),
                "familia": arquivo.get("familia"),
                "erro": str(exc),
            }
        resultados.append(resultado)
        if resultado.get("status") == "carregado":
            contadores["arquivos_carregados"] += 1
            contadores["linhas_carregadas"] += int(resultado.get("linhas_carregadas") or 0)
        elif resultado.get("status") == "baixado_sem_parser":
            contadores["arquivos_sem_parser"] += 1
    return {
        "status": "ok",
        "arquivos_processados": len(arquivos),
        **contadores,
        "resultados": resultados,
    }


async def executar_elt_all(
    *,
    escopo: str = "sector_core",
    familias: list[str] | None = None,
    limite: int | None = None,
    max_depth: int = 5,
) -> dict:
    discovery = await executar_elt_discovery(escopo=escopo, max_depth=max_depth)
    extract = await executar_elt_extract_all(escopo=escopo, familias=familias, limite=limite)
    load = await executar_elt_load_all(escopo=escopo, familias=familias, limite=limite)
    return {"status": "ok", "discovery": discovery, "extract": extract, "load": load}
