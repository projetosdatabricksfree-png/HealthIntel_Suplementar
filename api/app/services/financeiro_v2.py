from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.financeiro_v2 import (
    FinanceiroOperadoraResponse,
    ScoreV2OperadoraResponse,
)
from api.app.schemas.meta import MetaEnvelope

settings = get_settings()


async def _obter_cache(chave: str) -> dict | None:
    try:
        valor = await redis_client.get(chave)
    except Exception:
        return None
    if not valor:
        return None
    return json.loads(valor)


async def _salvar_cache(chave: str, payload: dict) -> None:
    try:
        await redis_client.set(
            chave,
            json.dumps(payload, default=str),
            ex=settings.app_cache_ttl_segundos,
        )
    except Exception:
        return


async def _resolver_meta_dataset(session, dataset: str, fallback_competencia: str) -> dict:
    result = await session.execute(
        text(
            """
            select
                coalesce(competencia, :fallback_competencia) as competencia,
                versao
            from plataforma.versao_dataset
            where dataset = :dataset
            order by carregado_em desc
            limit 1
            """
        ),
        {"dataset": dataset, "fallback_competencia": fallback_competencia},
    )
    row = result.mappings().first()
    if not row:
        return {
            "competencia_referencia": str(fallback_competencia),
            "versao_dataset": f"{dataset}_v1",
        }
    return {
        "competencia_referencia": str(row["competencia"] or fallback_competencia),
        "versao_dataset": row["versao"],
    }


def _normalizar_componentes(valor: object) -> dict[str, float]:
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return {chave: float(item) for chave, item in valor.items()}
    if isinstance(valor, str):
        try:
            parsed = json.loads(valor)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return {chave: float(item) for chave, item in parsed.items()}
    return {}


async def detalhar_financeiro_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
) -> dict:
    cache_key = f"financeiro:{registro_ans}:{competencia or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"registro_ans": registro_ans.zfill(6)}
    filtro_competencia = ""
    if competencia:
        filtro_competencia = "and competencia = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    trimestre_referencia,
                    ativo_total,
                    passivo_total,
                    patrimonio_liquido,
                    receita_total,
                    despesa_total,
                    resultado_periodo,
                    resultado_operacional,
                    provisao_tecnica,
                    margem_solvencia_calculada,
                    sinistro_total,
                    contraprestacao_total,
                    sinistralidade_bruta,
                    ressarcimento_sus,
                    evento_indenizavel,
                    sinistralidade_liquida,
                    taxa_sinistralidade_calculada,
                    indice_sinistralidade,
                    margem_liquida_pct,
                    cobertura_provisao,
                    resultado_operacional_bruto,
                    score_financeiro_base,
                    rating_financeiro,
                    vda_valor_devido,
                    vda_valor_pago,
                    vda_saldo_devedor,
                    vda_situacao_cobranca,
                    vda_inadimplente,
                    vda_meses_inadimplente_consecutivos,
                    vda_data_vencimento,
                    qt_glosa,
                    valor_glosa,
                    valor_faturado,
                    glosa_taxa_glosa_calculada,
                    severidade_glosa,
                    tipos_glosa,
                    versao_dataset
                from api_ans.api_financeiro_operadora_mensal
                where registro_ans = :registro_ans
                {filtro_competencia}
                order by competencia desc
                limit 24
                """
            ),
            params,
        )
        rows = result.mappings().all()
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "FINANCEIRO_NAO_ENCONTRADO",
                    "mensagem": "Nao ha serie financeira para o registro ANS informado.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(
            session,
            "financeiro_v2",
            rows[0]["competencia"],
        )

    dados = [FinanceiroOperadoraResponse(**row).model_dump() for row in rows]
    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=meta_dataset["competencia_referencia"],
            versao_dataset=meta_dataset["versao_dataset"],
            total=len(dados),
            pagina=1,
            por_pagina=len(dados),
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload


async def detalhar_score_v2_operadora(
    registro_ans: str,
    *,
    competencia: str | None = None,
) -> dict:
    cache_key = f"score_v2:{registro_ans}:{competencia or 'latest'}"
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict[str, object] = {"registro_ans": registro_ans.zfill(6)}
    filtro_competencia = ""
    if competencia:
        filtro_competencia = "and competencia = :competencia"
        params["competencia"] = competencia

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    operadora_id,
                    registro_ans,
                    nome,
                    nome_fantasia,
                    modalidade,
                    uf_sede,
                    competencia,
                    trimestre_financeiro,
                    score_core,
                    score_regulatorio,
                    score_financeiro_trimestral,
                    inadimplente,
                    saldo_devedor,
                    valor_devido,
                    valor_pago,
                    situacao_cobranca,
                    taxa_glosa_calculada,
                    valor_glosa_total,
                    valor_faturado_total,
                    penalizacao_vda,
                    penalizacao_glosa,
                    score_penalizacoes,
                    score_v2_base,
                    score_v2,
                    rating,
                    componentes,
                    versao_metodologia
                from api_ans.api_score_v2_operadora_mensal
                where registro_ans = :registro_ans
                {filtro_competencia}
                order by competencia desc
                limit 24
                """
            ),
            params,
        )
        rows = result.mappings().all()
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "SCORE_V2_NAO_ENCONTRADO",
                    "mensagem": "Nao ha score v2 para o registro ANS informado.",
                },
            )
        meta_dataset = await _resolver_meta_dataset(
            session,
            "score_v2",
            rows[0]["competencia"],
        )

    dados = []
    for row in rows:
        payload_linha = dict(row)
        payload_linha["componentes"] = _normalizar_componentes(payload_linha.get("componentes"))
        dados.append(ScoreV2OperadoraResponse(**payload_linha).model_dump())

    payload = {
        "dados": dados,
        "meta": MetaEnvelope(
            competencia_referencia=meta_dataset["competencia_referencia"],
            versao_dataset=meta_dataset["versao_dataset"],
            total=len(dados),
            pagina=1,
            por_pagina=len(dados),
        ).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await _salvar_cache(cache_key, payload)
    return payload
