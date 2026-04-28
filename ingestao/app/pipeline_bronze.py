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


async def processar_arquivo_bruto_streaming(
    *,
    dataset_codigo: str,
    nome_arquivo: str,
    hash_arquivo: str,
    iterador_batches,
    lote_id: str,
    layout_id: str,
    layout_versao_id: str,
    hash_estrutura: str,
    batch_size: int = 5000,
    colunas_mapeadas: list[dict] | None = None,
) -> dict:
    from ingestao.app.carregar_postgres import (
        carregar_dataset_bruto_em_batches,
        registrar_lote_ingestao,
        registrar_quarentena,
    )

    total_linhas_raw = 0
    total_aprovadas = 0
    total_quarentena = 0
    competencia_carregada: int | None = None

    for batch in iterador_batches:
        total_linhas_raw += len(batch)
        registros_traduzidos = traduzir_registros(
            batch, colunas_mapeadas or [], transformacoes=TRANSFORMACOES_PADRAO
        )
        aprovados = [
            r for r in registros_traduzidos
            if any(v is not None and str(v).strip() for v in r.values())
        ]
        rejeitados = [
            r for r in registros_traduzidos
            if not any(v is not None and str(v).strip() for v in r.values())
        ]

        if aprovados:
            if competencia_carregada is None:
                from ingestao.app.janela_carga import normalizar_competencia

                valor_competencia = aprovados[0].get("competencia")
                if valor_competencia is not None:
                    competencia_carregada = normalizar_competencia(valor_competencia)
            inseridos = await carregar_dataset_bruto_em_batches(
                dataset_codigo,
                aprovados,
                arquivo_origem=nome_arquivo,
                layout_id=layout_id,
                layout_versao_id=layout_versao_id,
                hash_arquivo=hash_arquivo,
                hash_estrutura=hash_estrutura,
                lote_id=lote_id,
                colunas_mapeadas=colunas_mapeadas,
            )
            total_aprovadas += inseridos

        for _ in rejeitados:
            await registrar_quarentena(
                dataset_codigo=dataset_codigo,
                arquivo_origem=nome_arquivo,
                hash_arquivo=hash_arquivo,
                hash_estrutura=hash_estrutura,
                motivo="Registro vazio ou invalido no streaming",
            )
            total_quarentena += 1

    status = "sucesso_com_alertas" if total_quarentena > 0 else "sucesso"
    await registrar_lote_ingestao(
        lote_id=lote_id,
        dataset_codigo=dataset_codigo,
        competencia=None,
        arquivo_origem=nome_arquivo,
        hash_arquivo=hash_arquivo,
        hash_estrutura=hash_estrutura,
        versao_layout=layout_versao_id,
        status=status,
        total_linhas_raw=total_linhas_raw,
        total_aprovadas=total_aprovadas,
        total_quarentena=total_quarentena,
        origem_execucao="streaming_pipeline",
    )
    if competencia_carregada is not None:
        from ingestao.app.janela_carga import (
            DatasetNaoTemporalError,
            PoliticaDatasetNaoEncontradaError,
            obter_janela,
            registrar_decisao,
        )

        try:
            janela = await obter_janela(dataset_codigo)
        except (DatasetNaoTemporalError, PoliticaDatasetNaoEncontradaError):
            janela = None
        if janela is not None:
            await registrar_decisao(
                dataset_codigo,
                competencia_carregada,
                "carregado",
                janela,
                "Carga streaming concluida dentro da janela dinamica.",
            )

    return {
        "status": status,
        "lote_id": lote_id,
        "total_linhas_raw": total_linhas_raw,
        "total_aprovadas": total_aprovadas,
        "total_quarentena": total_quarentena,
    }
