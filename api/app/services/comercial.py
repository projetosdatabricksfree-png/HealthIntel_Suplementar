import json

from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client
from api.app.schemas.comercial import (
    FinanceiroItem,
    GlosaItem,
    HistoricoPlanoItem,
    IgrItem,
    IdssItem,
    NipItem,
    ProdutoPlanoItem,
    PrudencialItem,
    RegimeEspecialItem,
    RegulatorioItem,
)
from api.app.schemas.meta import MetaEnvelope
from api.app.services.cobertura_temporal import (
    adicionar_filtro_anual,
    adicionar_filtro_mensal,
    adicionar_filtro_trimestral,
    anexar_janela_temporal,
)

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
        await redis_client.set(chave, json.dumps(payload, default=str), ex=settings.app_cache_ttl_segundos)
    except Exception:
        return


def _where(filtros: list[str]) -> str:
    return " where " + " and ".join(filtros) if filtros else ""


async def listar_produtos_planos(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    competencia: int | None = None,
    competencia_inicio: int | None = None,
    competencia_fim: int | None = None,
    situacao_plano: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"produtos_planos:{pagina}:{por_pagina}:{registro_ans or ''}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}:{situacao_plano or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    if situacao_plano:
        params["situacao_plano"] = situacao_plano
        filtros.append("situacao_plano = :situacao_plano")
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_produto_plano{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(competencia)::text from consumo_ans.consumo_produto_plano"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select registro_ans, codigo_produto, nome_produto, segmentacao, tipo_contratacao, abrangencia_geografica, modalidade, uf_comercializacao, competencia, situacao_plano, data_situacao from consumo_ans.consumo_produto_plano{where} order by competencia desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [ProdutoPlanoItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_produto_plano_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/produtos-planos")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_historico_planos(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    competencia: int | None = None,
    competencia_inicio: int | None = None,
    competencia_fim: int | None = None,
    situacao: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"historico_planos:{pagina}:{por_pagina}:{registro_ans or ''}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}:{situacao or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    if situacao:
        params["situacao"] = situacao
        filtros.append("situacao = :situacao")
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_historico_plano{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(competencia)::text from consumo_ans.consumo_historico_plano"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select registro_ans, codigo_plano, nome_plano, situacao, data_situacao, segmentacao, tipo_contratacao, abrangencia_geografica, uf, competencia from consumo_ans.consumo_historico_plano{where} order by competencia desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [HistoricoPlanoItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_historico_plano_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/historico-planos")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_regulatorio(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
    nivel_alerta: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"regulatorio:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}:{nivel_alerta or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    if nivel_alerta:
        params["nivel_alerta"] = nivel_alerta
        filtros.append("nivel_alerta = :nivel_alerta")
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_regulatorio_operadora_trimestre{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from consumo_ans.consumo_regulatorio_operadora_trimestre"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select trimestre, registro_ans, razao_social, modalidade, qtd_reclamacoes, indice_reclamacao, demandas_nip, taxa_resolutividade, nivel_alerta, tendencia_regulatoria from consumo_ans.consumo_regulatorio_operadora_trimestre{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [RegulatorioItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_regulatorio_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/regulatorio")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_igr(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"igr:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_igr{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from consumo_ans.consumo_igr"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select trimestre, registro_ans, modalidade, porte, total_reclamacoes, beneficiarios, igr, meta_igr, atingiu_meta from consumo_ans.consumo_igr{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [IgrItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_igr_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/igr")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_nip(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"nip:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_nip{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from consumo_ans.consumo_nip"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select trimestre, registro_ans, modalidade, demandas_nip, demandas_resolvidas, beneficiarios, taxa_intermediacao_resolvida, taxa_resolutividade from consumo_ans.consumo_nip{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [NipItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_nip_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/nip")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_idss(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    ano_base: int | None = None,
    ano_inicio: int | None = None,
    ano_fim: int | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"idss:{pagina}:{por_pagina}:{registro_ans or ''}:{ano_base or ''}:"
        f"{ano_inicio or ''}:{ano_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_anual(
        filtros,
        params,
        "ano_base",
        ano_base=ano_base,
        ano_inicio=ano_inicio,
        ano_fim=ano_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_idss{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(ano_base)::text from consumo_ans.consumo_idss"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select ano_base, registro_ans, idss_total, idqs, idga, idsm, idgr, faixa_idss, versao_metodologia from consumo_ans.consumo_idss{where} order by ano_base desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [IdssItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_idss_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/idss")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_financeiro(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"financeiro:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from consumo_ans.consumo_financeiro_operadora_trimestre{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from consumo_ans.consumo_financeiro_operadora_trimestre"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select trimestre, registro_ans, razao_social, nome_fantasia, modalidade, uf, receita_total, despesa_total, resultado_periodo, resultado_operacional, patrimonio_liquido, sinistralidade_bruta, sinistralidade_liquida, rating_financeiro, versao_financeira from consumo_ans.consumo_financeiro_operadora_trimestre{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [FinanceiroItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="consumo_financeiro_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/financeiro")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_prudencial(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"prudencial:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from api_ans.api_prudencial_operadora_trimestral{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from api_ans.api_prudencial_operadora_trimestral"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select registro_ans, trimestre, margem_solvencia, capital_minimo_requerido, capital_disponivel, indice_liquidez, situacao_prudencial, situacao_inadequada, fonte_publicacao, versao_dataset from api_ans.api_prudencial_operadora_trimestral{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [PrudencialItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="api_prudencial_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/prudencial")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_regime_especial(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    trimestre: str | None = None,
    trimestre_inicio: str | None = None,
    trimestre_fim: str | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"regime_especial:{pagina}:{por_pagina}:{registro_ans or ''}:{trimestre or ''}:"
        f"{trimestre_inicio or ''}:{trimestre_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_trimestral(
        filtros,
        params,
        "trimestre",
        trimestre=trimestre,
        trimestre_inicio=trimestre_inicio,
        trimestre_fim=trimestre_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from api_ans.api_regime_especial_operadora_trimestral{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(trimestre) from api_ans.api_regime_especial_operadora_trimestral"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select registro_ans, nome, modalidade, uf_sede, trimestre, trimestre_fim, tipo_regime, ativo, duracao_trimestres, data_inicio, data_fim, descricao, versao_dataset from api_ans.api_regime_especial_operadora_trimestral{where} order by trimestre desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [RegimeEspecialItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="api_regime_especial_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/regime-especial")
    await _salvar_cache(cache_key, payload)
    return payload


async def listar_glosa(
    *,
    pagina: int = 1,
    por_pagina: int = 50,
    registro_ans: str | None = None,
    competencia: int | None = None,
    competencia_inicio: int | None = None,
    competencia_fim: int | None = None,
) -> dict:
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    offset = (pagina - 1) * por_pagina
    cache_key = (
        f"glosa:{pagina}:{por_pagina}:{registro_ans or ''}:{competencia or ''}:"
        f"{competencia_inicio or ''}:{competencia_fim or ''}"
    )
    cached = await _obter_cache(cache_key)
    if cached:
        cached.setdefault("meta", {})["cache"] = "hit"
        return cached

    params: dict = {"limit": por_pagina, "offset": offset}
    filtros: list[str] = []
    if registro_ans:
        params["registro_ans"] = registro_ans
        filtros.append("registro_ans = :registro_ans")
    adicionar_filtro_mensal(
        filtros,
        params,
        "competencia",
        competencia=competencia,
        competencia_inicio=competencia_inicio,
        competencia_fim=competencia_fim,
    )
    where = _where(filtros)

    async with SessionLocal() as session:
        total = int((await session.execute(text(f"select count(*) from api_ans.api_glosa_operadora_mensal{where}"), params)).scalar_one())
        ref = (await session.execute(text("select max(competencia)::text from api_ans.api_glosa_operadora_mensal"))).scalar_one() or "atual"
        rows = (await session.execute(
            text(f"select registro_ans, competencia, tipo_glosa, qt_glosa, valor_glosa, valor_faturado, taxa_glosa_calculada, fonte_publicacao, versao_dataset from api_ans.api_glosa_operadora_mensal{where} order by competencia desc, registro_ans limit :limit offset :offset"),
            params,
        )).mappings().all()

    payload = {
        "dados": [GlosaItem(**r).model_dump() for r in rows],
        "meta": MetaEnvelope(competencia_referencia=ref, versao_dataset="api_glosa_v1", total=total, pagina=pagina, por_pagina=por_pagina).model_dump(),
    }
    payload["meta"]["cache"] = "miss"
    await anexar_janela_temporal(payload, "/v1/glosa")
    await _salvar_cache(cache_key, payload)
    return payload
