from typing import Callable

from ingestao.app.aplicar_alias import traduzir_registros
from ingestao.app.carregar_postgres import carregar_dataset_bruto, registrar_quarentena
from ingestao.app.identificar_layout import identificar_layout

TRANSFORMACOES_PADRAO: dict[str, Callable] = {
    "competencia": lambda valor: int("".join(filter(str.isdigit, str(valor)))[:6]),
    "registro_ans": lambda valor: str(valor).strip().zfill(6),
    "cnpj": lambda valor: "".join(filter(str.isdigit, str(valor))),
    "cd_municipio": lambda valor: str("".join(filter(str.isdigit, str(valor)))).zfill(7),
    "segmento": lambda valor: str(valor).strip().upper(),
    "tipo_prestador": lambda valor: str(valor).strip().upper(),
    "uf": lambda valor: str(valor).strip().upper()[:2],
    "trimestre": lambda valor: str(valor).strip().upper().replace(" ", ""),
    "tipo_lista": lambda valor: str(valor).strip().lower(),
}


async def processar_arquivo_bruto(
    *,
    dataset_codigo: str,
    nome_arquivo: str,
    hash_arquivo: str,
    registros: list[dict],
) -> dict:
    colunas_detectadas = list(registros[0].keys()) if registros else []
    identificacao = await identificar_layout(dataset_codigo, colunas_detectadas, nome_arquivo)
    if (
        not identificacao.compativel
        or not identificacao.layout_id
        or not identificacao.layout_versao_id
    ):
        motivo = "; ".join(identificacao.motivos) or "Layout incompativel para o arquivo."
        quarentena_id = await registrar_quarentena(
            dataset_codigo=dataset_codigo,
            arquivo_origem=nome_arquivo,
            hash_arquivo=hash_arquivo,
            hash_estrutura=identificacao.assinatura_colunas,
            motivo=motivo,
        )
        return {
            "status": "quarentena",
            "quarentena_id": quarentena_id,
            "motivos": identificacao.motivos,
        }

    registros_traduzidos = traduzir_registros(
        registros, identificacao.colunas_mapeadas, transformacoes=TRANSFORMACOES_PADRAO
    )
    lote = await carregar_dataset_bruto(
        dataset_codigo,
        registros_traduzidos,
        arquivo_origem=nome_arquivo,
        layout_id=identificacao.layout_id,
        layout_versao_id=identificacao.layout_versao_id,
        hash_arquivo=hash_arquivo,
        hash_estrutura=identificacao.assinatura_colunas,
        colunas_mapeadas=identificacao.colunas_mapeadas,
    )
    return {
        "status": "carregado",
        "lote_id": lote.lote_id,
        "tabela_destino": lote.tabela_destino,
        "total_registros": lote.total_registros,
    }
