"""Ingestão Sprint 41 — Delta ANS 100%.

Módulo de ingestão para datasets ANS que ainda não existiam no projeto.
Segue o mesmo padrão de ingestao_real.py: baixar arquivo, identificar layout,
processar via pipeline_bronze.

Famílias cobertas neste módulo:
- Produtos e planos (produto_caracteristica, historico_plano, plano_servico_opcional,
  quadro_auxiliar_corresponsabilidade)
- TUSS oficial (tuss_terminologia_oficial)
- TISS subfamílias (tiss_ambulatorial, tiss_hospitalar, tiss_dados_plano)
- SIP (sip_mapa_assistencial)
- Ressarcimento SUS (5 subfamílias)
- Precificação/NTRP (6 subfamílias)
- Rede/Prestadores (6 subfamílias)
- Regulatórios complementares (8 subfamílias)
- Beneficiários/cobertura (3 subfamílias)
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from ingestao.app.landing import baixar_arquivo
from ingestao.app.pipeline_bronze import processar_arquivo_bruto

_ANS_FTP = "https://dadosabertos.ans.gov.br/FTP/PDA"


def _url(caminho: str) -> str:
    return f"{_ANS_FTP}/{caminho.lstrip('/')}"


async def _ingerir_csv(
    dataset_codigo: str,
    competencia: str,
    url: str,
) -> dict:
    from ingestao.app.ingestao_real import _ler_csv_bytes

    arquivo = await baixar_arquivo(dataset_codigo, competencia, url)
    path = Path(arquivo["path"])

    if path.suffix.lower() == ".zip":
        registros: list[dict[str, str]] = []
        with zipfile.ZipFile(path) as zf:
            for nome in zf.namelist():
                if nome.lower().endswith((".csv", ".txt")):
                    registros.extend(_ler_csv_bytes(zf.read(nome)))
    else:
        registros = _ler_csv_bytes(path.read_bytes())

    for r in registros:
        r.setdefault("competencia", competencia)

    return await processar_arquivo_bruto(
        dataset_codigo=dataset_codigo,
        nome_arquivo=arquivo["arquivo_origem"],
        hash_arquivo=arquivo["hash_arquivo"],
        registros=registros,
    )


# ---------------------------------------------------------------------------
# Onda 1 — Produtos e Planos
# ---------------------------------------------------------------------------


async def executar_ingestao_produto_caracteristica(competencia: str) -> dict:
    return await _ingerir_csv(
        "produto_caracteristica",
        competencia,
        _url("caracteristicas_produtos_saude_suplementar-008/"),
    )


async def executar_ingestao_historico_plano(competencia: str) -> dict:
    return await _ingerir_csv(
        "historico_plano",
        competencia,
        _url("historico_planos_saude/"),
    )


async def executar_ingestao_plano_servico_opcional(competencia: str) -> dict:
    return await _ingerir_csv(
        "plano_servico_opcional",
        competencia,
        _url("servicos_opcionais_planos_saude/"),
    )


async def executar_ingestao_quadro_auxiliar_corresponsabilidade(competencia: str) -> dict:
    return await _ingerir_csv(
        "quadro_auxiliar_corresponsabilidade",
        competencia,
        _url("quadros_auxiliares_de_corresponsabilidade/"),
    )


# ---------------------------------------------------------------------------
# Onda 2 — TUSS Oficial
# ---------------------------------------------------------------------------


async def executar_ingestao_tuss_oficial(competencia: str) -> dict:
    """Carrega TUSS.zip — extrai CSV interno e popula tuss_terminologia_oficial."""
    from ingestao.app.ingestao_real import _ler_csv_bytes

    url = _url("terminologia_unificada_saude_suplementar_TUSS/TUSS.zip")
    arquivo = await baixar_arquivo("tuss_oficial", competencia, url)
    path = Path(arquivo["path"])

    registros: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        for nome in zf.namelist():
            if nome.lower().endswith((".csv", ".txt")):
                registros.extend(_ler_csv_bytes(zf.read(nome)))

    import datetime

    hoje = datetime.date.today()
    for r in registros:
        vigencia_fim_raw = str(r.get("vigencia_fim") or r.get("DT_FIM_VIGENCIA") or "").strip()
        if vigencia_fim_raw:
            try:
                from datetime import datetime as dt

                vf = dt.strptime(vigencia_fim_raw, "%d/%m/%Y").date()
                r["is_tuss_vigente"] = "true" if vf >= hoje else "false"
                r["vigencia_fim"] = vf.isoformat()
            except ValueError:
                r["is_tuss_vigente"] = "true"
        else:
            r["is_tuss_vigente"] = "true"
        r.setdefault("competencia", competencia)

    return await processar_arquivo_bruto(
        dataset_codigo="tuss_oficial",
        nome_arquivo=arquivo["arquivo_origem"],
        hash_arquivo=arquivo["hash_arquivo"],
        registros=registros,
    )


# ---------------------------------------------------------------------------
# Onda 3 — TISS Subfamílias
# ---------------------------------------------------------------------------


async def executar_ingestao_tiss_ambulatorial(competencia: str) -> dict:
    return await _ingerir_csv(
        "tiss_ambulatorial",
        competencia,
        _url(f"TISS/AMBULATORIAL/{competencia}.zip"),
    )


async def executar_ingestao_tiss_hospitalar(competencia: str) -> dict:
    return await _ingerir_csv(
        "tiss_hospitalar",
        competencia,
        _url(f"TISS/HOSPITALAR/{competencia}.zip"),
    )


async def executar_ingestao_tiss_dados_plano(competencia: str) -> dict:
    return await _ingerir_csv(
        "tiss_dados_plano",
        competencia,
        _url(f"TISS/DADOS_DE_PLANOS/{competencia}.zip"),
    )


# ---------------------------------------------------------------------------
# Onda 4 — SIP
# ---------------------------------------------------------------------------


async def executar_ingestao_sip_mapa_assistencial(competencia: str) -> dict:
    return await _ingerir_csv(
        "sip_mapa_assistencial",
        competencia,
        _url("SIP/"),
    )


# ---------------------------------------------------------------------------
# Onda 5 — Ressarcimento SUS
# ---------------------------------------------------------------------------


async def executar_ingestao_ressarcimento_beneficiario_abi(competencia: str) -> dict:
    return await _ingerir_csv(
        "ressarcimento_beneficiario_abi",
        competencia,
        _url("beneficiarios_identificados_sus_abi/"),
    )


async def executar_ingestao_ressarcimento_sus_operadora_plano(competencia: str) -> dict:
    return await _ingerir_csv(
        "ressarcimento_sus_operadora_plano",
        competencia,
        _url("dados_ressarcimento_SUS_operadora_planos_saude/"),
    )


async def executar_ingestao_ressarcimento_hc(competencia: str) -> dict:
    return await _ingerir_csv(
        "ressarcimento_hc",
        competencia,
        _url("hc_ressarcimento_sus/"),
    )


async def executar_ingestao_ressarcimento_cobranca_arrecadacao(competencia: str) -> dict:
    return await _ingerir_csv(
        "ressarcimento_cobranca_arrecadacao",
        competencia,
        _url("ressarcimento_ao_SUS_cobranca_arrecadacao/"),
    )


async def executar_ingestao_ressarcimento_indice_pagamento(competencia: str) -> dict:
    return await _ingerir_csv(
        "ressarcimento_indice_pagamento",
        competencia,
        _url("ressarcimento_ao_SUS_indice_efetivo_pagamento/"),
    )


# ---------------------------------------------------------------------------
# Onda 6 — Precificação, NTRP e Reajustes
# ---------------------------------------------------------------------------


async def executar_ingestao_ntrp_area_comercializacao(competencia: str) -> dict:
    return await _ingerir_csv(
        "ntrp_area_comercializacao",
        competencia,
        _url("area_comercializacao_planos_ntrp/"),
    )


async def executar_ingestao_painel_precificacao(competencia: str) -> dict:
    return await _ingerir_csv(
        "painel_precificacao",
        competencia,
        _url("painel_precificacao-053/"),
    )


async def executar_ingestao_percentual_reajuste_agrupamento(competencia: str) -> dict:
    return await _ingerir_csv(
        "percentual_reajuste_agrupamento",
        competencia,
        _url("percentuais_de_reajuste_de_agrupamento-055/"),
    )


async def executar_ingestao_ntrp_vcm_faixa_etaria(competencia: str) -> dict:
    return await _ingerir_csv(
        "ntrp_vcm_faixa_etaria",
        competencia,
        _url("nota_tecnica_ntrp_vcm_faixa_etaria/"),
    )


async def executar_ingestao_valor_comercial_medio_municipio(competencia: str) -> dict:
    return await _ingerir_csv(
        "valor_comercial_medio_municipio",
        competencia,
        _url("valor_comercial_medio_por_municipio_NTRP-054/"),
    )


async def executar_ingestao_faixa_preco(competencia: str) -> dict:
    return await _ingerir_csv(
        "faixa_preco",
        competencia,
        _url("faixa_de_preco/"),
    )


# ---------------------------------------------------------------------------
# Onda 7 — Rede, Prestadores e Acreditação
# ---------------------------------------------------------------------------


async def executar_ingestao_operadora_cancelada(competencia: str) -> dict:
    return await _ingerir_csv(
        "operadora_cancelada",
        competencia,
        _url("operadoras_de_plano_de_saude_canceladas/"),
    )


async def executar_ingestao_operadora_acreditada(competencia: str) -> dict:
    return await _ingerir_csv(
        "operadora_acreditada",
        competencia,
        _url("operadoras_acreditadas/"),
    )


async def executar_ingestao_prestador_acreditado(competencia: str) -> dict:
    return await _ingerir_csv(
        "prestador_acreditado",
        competencia,
        _url("prestadores_acreditados/"),
    )


async def executar_ingestao_produto_prestador_hospitalar(competencia: str) -> dict:
    return await _ingerir_csv(
        "produto_prestador_hospitalar",
        competencia,
        _url("produtos_e_prestadores_hospitalares/"),
    )


async def executar_ingestao_operadora_prestador_nao_hospitalar(competencia: str) -> dict:
    return await _ingerir_csv(
        "operadora_prestador_nao_hospitalar",
        competencia,
        _url("operadoras_e_prestadores_nao_hospitalares/"),
    )


async def executar_ingestao_solicitacao_alteracao_rede_hospitalar(competencia: str) -> dict:
    return await _ingerir_csv(
        "solicitacao_alteracao_rede_hospitalar",
        competencia,
        _url("solicitacoes_alteracao_rede_hospitalar-046/"),
    )


# ---------------------------------------------------------------------------
# Onda 8 — Regulatórios Complementares
# ---------------------------------------------------------------------------


async def executar_ingestao_penalidade_operadora(competencia: str) -> dict:
    return await _ingerir_csv(
        "penalidade_operadora",
        competencia,
        _url("penalidades_aplicadas_a_operadoras/"),
    )


async def executar_ingestao_monitoramento_garantia_atendimento(competencia: str) -> dict:
    return await _ingerir_csv(
        "monitoramento_garantia_atendimento",
        competencia,
        _url("monitoramento_garantia_atendimento/"),
    )


async def executar_ingestao_peona_sus(competencia: str) -> dict:
    return await _ingerir_csv(
        "peona_sus",
        competencia,
        _url("peona_sus/"),
    )


async def executar_ingestao_promoprev(competencia: str) -> dict:
    return await _ingerir_csv(
        "promoprev",
        competencia,
        _url("promoprev-052/"),
    )


async def executar_ingestao_rpc(competencia: str) -> dict:
    return await _ingerir_csv(
        "rpc",
        competencia,
        _url(f"RPC/{competencia}.zip"),
    )


async def executar_ingestao_iap(competencia: str) -> dict:
    return await _ingerir_csv(
        "iap",
        competencia,
        _url("IAP/"),
    )


async def executar_ingestao_pfa(competencia: str) -> dict:
    return await _ingerir_csv(
        "pfa",
        competencia,
        _url("PFA/"),
    )


async def executar_ingestao_programa_qualificacao_institucional(competencia: str) -> dict:
    return await _ingerir_csv(
        "programa_qualificacao_institucional",
        competencia,
        _url("programa_de_qualificacao_institucional/"),
    )


# ---------------------------------------------------------------------------
# Onda 9 — Beneficiários e Cobertura
# ---------------------------------------------------------------------------


async def executar_ingestao_beneficiario_regiao_geografica(competencia: str) -> dict:
    return await _ingerir_csv(
        "beneficiario_regiao_geografica",
        competencia,
        _url("dados_de_beneficiarios_por_regiao_geografica/"),
    )


async def executar_ingestao_beneficiario_informacao_consolidada(competencia: str) -> dict:
    return await _ingerir_csv(
        "beneficiario_informacao_consolidada",
        competencia,
        _url("informacoes_consolidadas_de_beneficiarios-024/"),
    )


async def executar_ingestao_taxa_cobertura_plano(competencia: str) -> dict:
    return await _ingerir_csv(
        "taxa_cobertura_plano",
        competencia,
        _url("taxa_de_cobertura_de_planos_de_saude-047/"),
    )
