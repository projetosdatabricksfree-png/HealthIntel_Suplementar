import json
import math
import re
import secrets
from calendar import monthrange
from datetime import UTC, date, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.core.security import gerar_hash_sha256
from api.app.schemas.billing import BillingFechamentoRequest, BillingUpgradeRequest, ChaveCriacaoRequest

REFERENCIA_REGEX = re.compile(r"^\d{4}-\d{2}$")


def normalizar_referencia(referencia: str) -> str:
    if not REFERENCIA_REGEX.match(referencia):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo_erro": "REFERENCIA_INVALIDA",
                "mensagem": "Use o formato YYYY-MM para a referencia de billing.",
            },
        )
    ano, mes = referencia.split("-")
    if not 1 <= int(mes) <= 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo_erro": "REFERENCIA_INVALIDA",
                "mensagem": "Mes fora do intervalo permitido para billing.",
            },
        )
    return referencia


def calcular_totais_fatura(
    *,
    requisicoes_faturaveis: int,
    franquia_requisicoes_mes: int,
    preco_base_centavos: int,
    preco_excedente_mil_requisicoes_centavos: int,
) -> dict:
    requisicoes_excedentes = max(requisicoes_faturaveis - franquia_requisicoes_mes, 0)
    blocos_excedentes = math.ceil(requisicoes_excedentes / 1000) if requisicoes_excedentes else 0
    valor_excedente_centavos = (
        blocos_excedentes * preco_excedente_mil_requisicoes_centavos
        if preco_excedente_mil_requisicoes_centavos
        else 0
    )
    valor_total_centavos = preco_base_centavos + valor_excedente_centavos
    return {
        "requisicoes_excedentes": requisicoes_excedentes,
        "blocos_excedentes": blocos_excedentes,
        "valor_excedente_centavos": valor_excedente_centavos,
        "valor_total_centavos": valor_total_centavos,
    }


def formatar_centavos(valor_centavos: int) -> str:
    valor = f"{valor_centavos / 100:,.2f}"
    valor = valor.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {valor}"


def _periodo_referencia(referencia: str) -> tuple[date, date, datetime, datetime]:
    ano, mes = (int(item) for item in referencia.split("-"))
    ultimo_dia = monthrange(ano, mes)[1]
    inicio_date = date(ano, mes, 1)
    fim_date = date(ano, mes, ultimo_dia)
    inicio_dt = datetime(ano, mes, 1, tzinfo=UTC)
    if mes == 12:
        fim_exclusivo = datetime(ano + 1, 1, 1, tzinfo=UTC)
    else:
        fim_exclusivo = datetime(ano, mes + 1, 1, tzinfo=UTC)
    return inicio_date, fim_date, inicio_dt, fim_exclusivo


def _proximo_plano(planos_ordenados: list[dict], ordem_atual: int) -> dict | None:
    for plano in planos_ordenados:
        if plano["ordem_upgrade"] > ordem_atual and plano["permite_upgrade_automatico"]:
            return plano
    return None


def _gerar_api_key_rotacionada() -> str:
    return f"hi_rot_{secrets.token_urlsafe(24)}"


async def _registrar_auditoria_cobranca(
    *,
    session,
    cliente_id: str | None,
    referencia: str | None,
    evento: str,
    ator: str,
    origem: str,
    payload: dict,
) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.auditoria_cobranca (
                id,
                cliente_id,
                referencia,
                evento,
                ator,
                origem,
                payload
            ) values (
                :id,
                cast(:cliente_id as uuid),
                :referencia,
                :evento,
                :ator,
                :origem,
                cast(:payload as jsonb)
            )
            """
        ),
        {
            "id": str(uuid4()),
            "cliente_id": cliente_id,
            "referencia": referencia,
            "evento": evento,
            "ator": ator,
            "origem": origem,
            "payload": json.dumps(payload, default=str),
        },
    )


async def listar_resumo_faturamento(referencia: str, cliente_id: str | None = None) -> dict:
    referencia = normalizar_referencia(referencia)
    filtro_cliente = ""
    params: dict[str, str] = {"referencia": referencia}
    if cliente_id:
        filtro_cliente = "and fatura.cliente_id = cast(:cliente_id as uuid)"
        params["cliente_id"] = cliente_id

    async with SessionLocal() as session:
        result = await session.execute(
            text(
                f"""
                select
                    fatura.referencia,
                    fatura.cliente_id,
                    cliente.nome as cliente_nome,
                    cliente.email,
                    fatura.plano_id,
                    plano.nome as plano_nome,
                    fatura.requisicoes_total,
                    fatura.requisicoes_faturaveis,
                    fatura.franquia_requisicoes_mes,
                    fatura.requisicoes_excedentes,
                    fatura.blocos_excedentes,
                    fatura.endpoints_faturaveis,
                    fatura.latencia_media_ms,
                    fatura.valor_base_centavos,
                    fatura.valor_excedente_centavos,
                    fatura.valor_total_centavos,
                    fatura.status,
                    ciclo.fechado_em
                from plataforma.fatura_consumo fatura
                inner join plataforma.cliente cliente
                    on cliente.id = fatura.cliente_id
                inner join plataforma.plano plano
                    on plano.id = fatura.plano_id
                inner join plataforma.ciclo_faturamento ciclo
                    on ciclo.id = fatura.ciclo_id
                where fatura.referencia = :referencia
                {filtro_cliente}
                order by fatura.valor_total_centavos desc, cliente.nome
                """
            ),
            params,
        )
        dados = []
        total_valor_centavos = 0
        for row in result.mappings():
            total_valor_centavos += int(row["valor_total_centavos"])
            dados.append(
                {
                    "referencia": row["referencia"],
                    "cliente_id": str(row["cliente_id"]),
                    "cliente_nome": row["cliente_nome"],
                    "email": row["email"],
                    "plano_id": str(row["plano_id"]),
                    "plano_nome": row["plano_nome"],
                    "requisicoes_total": int(row["requisicoes_total"]),
                    "requisicoes_faturaveis": int(row["requisicoes_faturaveis"]),
                    "franquia_requisicoes_mes": int(row["franquia_requisicoes_mes"]),
                    "requisicoes_excedentes": int(row["requisicoes_excedentes"]),
                    "blocos_excedentes": int(row["blocos_excedentes"]),
                    "endpoints_faturaveis": int(row["endpoints_faturaveis"]),
                    "latencia_media_ms": int(row["latencia_media_ms"]),
                    "valor_base_centavos": int(row["valor_base_centavos"]),
                    "valor_excedente_centavos": int(row["valor_excedente_centavos"]),
                    "valor_total_centavos": int(row["valor_total_centavos"]),
                    "valor_total_formatado": formatar_centavos(int(row["valor_total_centavos"])),
                    "status_fatura": row["status"],
                    "fechado_em": row["fechado_em"].isoformat() if row["fechado_em"] else None,
                }
            )
    return {
        "dados": dados,
        "meta": {
            "referencia": referencia,
            "total_clientes": len(dados),
            "valor_total_centavos": total_valor_centavos,
            "valor_total_formatado": formatar_centavos(total_valor_centavos),
        },
    }


async def fechar_ciclo_faturamento(payload: BillingFechamentoRequest) -> dict:
    referencia = normalizar_referencia(payload.referencia)
    inicio_date, fim_date, inicio_dt, fim_exclusivo = _periodo_referencia(referencia)

    filtro_cliente = ""
    params: dict[str, object] = {
        "inicio_periodo": inicio_dt,
        "fim_periodo_exclusivo": fim_exclusivo,
    }
    if payload.cliente_id:
        filtro_cliente = "and cliente.id = cast(:cliente_id as uuid)"
        params["cliente_id"] = payload.cliente_id

    async with SessionLocal() as session:
        planos_result = await session.execute(
            text(
                """
                select id, nome, ordem_upgrade, permite_upgrade_automatico
                from plataforma.plano
                where status = 'ativo'
                order by ordem_upgrade
                """
            )
        )
        planos_ordenados = [
            {
                "id": str(row["id"]),
                "nome": row["nome"],
                "ordem_upgrade": int(row["ordem_upgrade"]),
                "permite_upgrade_automatico": bool(row["permite_upgrade_automatico"]),
            }
            for row in planos_result.mappings()
        ]

        result = await session.execute(
            text(
                f"""
                select
                    cliente.id as cliente_id,
                    cliente.nome as cliente_nome,
                    cliente.email,
                    plano.id as plano_id,
                    plano.nome as plano_nome,
                    plano.preco_base_centavos,
                    plano.franquia_requisicoes_mes,
                    plano.preco_excedente_mil_requisicoes_centavos,
                    plano.ordem_upgrade,
                    coalesce(count(log.id), 0) as requisicoes_total,
                    coalesce(
                        count(log.id) filter (
                            where log.endpoint like '/v1/%'
                              and log.endpoint not like '/admin/%'
                              and log.codigo_status < 500
                              and log.codigo_status <> 429
                        ),
                        0
                    ) as requisicoes_faturaveis,
                    coalesce(
                        count(distinct log.endpoint) filter (
                            where log.endpoint like '/v1/%'
                              and log.endpoint not like '/admin/%'
                              and log.codigo_status < 500
                              and log.codigo_status <> 429
                        ),
                        0
                    ) as endpoints_faturaveis,
                    coalesce(
                        avg(log.latencia_ms) filter (
                            where log.endpoint like '/v1/%'
                              and log.endpoint not like '/admin/%'
                              and log.codigo_status < 500
                              and log.codigo_status <> 429
                        ),
                        0
                    )::integer as latencia_media_ms,
                    max(log.timestamp_req) as ultimo_consumo_em
                from plataforma.cliente cliente
                inner join plataforma.plano plano
                    on plano.id = cliente.plano_id
                left join plataforma.log_uso log
                    on log.cliente_id = cliente.id
                   and log.timestamp_req >= :inicio_periodo
                   and log.timestamp_req < :fim_periodo_exclusivo
                where cliente.status = 'ativo'
                {filtro_cliente}
                group by
                    cliente.id,
                    cliente.nome,
                    cliente.email,
                    plano.id,
                    plano.nome,
                    plano.preco_base_centavos,
                    plano.franquia_requisicoes_mes,
                    plano.preco_excedente_mil_requisicoes_centavos,
                    plano.ordem_upgrade
                order by cliente.nome
                """
            ),
            params,
        )
        dados = []
        total_valor_centavos = 0
        for row in result.mappings():
            totais = calcular_totais_fatura(
                requisicoes_faturaveis=int(row["requisicoes_faturaveis"]),
                franquia_requisicoes_mes=int(row["franquia_requisicoes_mes"]),
                preco_base_centavos=int(row["preco_base_centavos"]),
                preco_excedente_mil_requisicoes_centavos=int(
                    row["preco_excedente_mil_requisicoes_centavos"]
                ),
            )
            proximo_plano = _proximo_plano(planos_ordenados, int(row["ordem_upgrade"]))
            upgrade_recomendado = (
                totais["requisicoes_excedentes"] > 0 and proximo_plano is not None
            )
            regra_faturamento = {
                "tipo": "assinatura_mensal_com_excedente",
                "franquia_requisicoes_mes": int(row["franquia_requisicoes_mes"]),
                "preco_base_centavos": int(row["preco_base_centavos"]),
                "preco_excedente_mil_requisicoes_centavos": int(
                    row["preco_excedente_mil_requisicoes_centavos"]
                ),
                "criterio_faturavel": "endpoint_publico_/v1 + status_<500_exceto_429",
            }
            ciclo_result = await session.execute(
                text(
                    """
                    insert into plataforma.ciclo_faturamento (
                        id,
                        cliente_id,
                        referencia,
                        inicio_periodo,
                        fim_periodo,
                        status,
                        valor_estimado_centavos,
                        registros_faturaveis,
                        fechado_em
                    ) values (
                        :id,
                        cast(:cliente_id as uuid),
                        :referencia,
                        :inicio_periodo,
                        :fim_periodo,
                        :status,
                        :valor_estimado_centavos,
                        :registros_faturaveis,
                        now()
                    )
                    on conflict (cliente_id, referencia) do update set
                        inicio_periodo = excluded.inicio_periodo,
                        fim_periodo = excluded.fim_periodo,
                        status = excluded.status,
                        valor_estimado_centavos = excluded.valor_estimado_centavos,
                        registros_faturaveis = excluded.registros_faturaveis,
                        fechado_em = now(),
                        atualizado_em = now()
                    returning id
                    """
                ),
                {
                    "id": str(uuid4()),
                    "cliente_id": str(row["cliente_id"]),
                    "referencia": referencia,
                    "inicio_periodo": inicio_date,
                    "fim_periodo": fim_date,
                    "status": "fechado",
                    "valor_estimado_centavos": totais["valor_total_centavos"],
                    "registros_faturaveis": int(row["requisicoes_faturaveis"]),
                },
            )
            ciclo_id = str(ciclo_result.scalar_one())

            await session.execute(
                text(
                    """
                    insert into plataforma.fatura_consumo (
                        id,
                        ciclo_id,
                        cliente_id,
                        plano_id,
                        referencia,
                        requisicoes_total,
                        requisicoes_faturaveis,
                        franquia_requisicoes_mes,
                        requisicoes_excedentes,
                        blocos_excedentes,
                        endpoints_faturaveis,
                        latencia_media_ms,
                        valor_base_centavos,
                        valor_excedente_centavos,
                        valor_total_centavos,
                        status,
                        regra_faturamento
                    ) values (
                        :id,
                        cast(:ciclo_id as uuid),
                        cast(:cliente_id as uuid),
                        cast(:plano_id as uuid),
                        :referencia,
                        :requisicoes_total,
                        :requisicoes_faturaveis,
                        :franquia_requisicoes_mes,
                        :requisicoes_excedentes,
                        :blocos_excedentes,
                        :endpoints_faturaveis,
                        :latencia_media_ms,
                        :valor_base_centavos,
                        :valor_excedente_centavos,
                        :valor_total_centavos,
                        :status,
                        cast(:regra_faturamento as jsonb)
                    )
                    on conflict (cliente_id, referencia) do update set
                        ciclo_id = excluded.ciclo_id,
                        plano_id = excluded.plano_id,
                        requisicoes_total = excluded.requisicoes_total,
                        requisicoes_faturaveis = excluded.requisicoes_faturaveis,
                        franquia_requisicoes_mes = excluded.franquia_requisicoes_mes,
                        requisicoes_excedentes = excluded.requisicoes_excedentes,
                        blocos_excedentes = excluded.blocos_excedentes,
                        endpoints_faturaveis = excluded.endpoints_faturaveis,
                        latencia_media_ms = excluded.latencia_media_ms,
                        valor_base_centavos = excluded.valor_base_centavos,
                        valor_excedente_centavos = excluded.valor_excedente_centavos,
                        valor_total_centavos = excluded.valor_total_centavos,
                        status = excluded.status,
                        regra_faturamento = excluded.regra_faturamento,
                        atualizado_em = now()
                    """
                ),
                {
                    "id": str(uuid4()),
                    "ciclo_id": ciclo_id,
                    "cliente_id": str(row["cliente_id"]),
                    "plano_id": str(row["plano_id"]),
                    "referencia": referencia,
                    "requisicoes_total": int(row["requisicoes_total"]),
                    "requisicoes_faturaveis": int(row["requisicoes_faturaveis"]),
                    "franquia_requisicoes_mes": int(row["franquia_requisicoes_mes"]),
                    "requisicoes_excedentes": totais["requisicoes_excedentes"],
                    "blocos_excedentes": totais["blocos_excedentes"],
                    "endpoints_faturaveis": int(row["endpoints_faturaveis"]),
                    "latencia_media_ms": int(row["latencia_media_ms"]),
                    "valor_base_centavos": int(row["preco_base_centavos"]),
                    "valor_excedente_centavos": totais["valor_excedente_centavos"],
                    "valor_total_centavos": totais["valor_total_centavos"],
                    "status": "fechada",
                    "regra_faturamento": json.dumps(regra_faturamento),
                },
            )

            resumo = {
                "referencia": referencia,
                "cliente_id": str(row["cliente_id"]),
                "cliente_nome": row["cliente_nome"],
                "email": row["email"],
                "plano_id": str(row["plano_id"]),
                "plano_nome": row["plano_nome"],
                "requisicoes_total": int(row["requisicoes_total"]),
                "requisicoes_faturaveis": int(row["requisicoes_faturaveis"]),
                "franquia_requisicoes_mes": int(row["franquia_requisicoes_mes"]),
                "requisicoes_excedentes": totais["requisicoes_excedentes"],
                "blocos_excedentes": totais["blocos_excedentes"],
                "endpoints_faturaveis": int(row["endpoints_faturaveis"]),
                "latencia_media_ms": int(row["latencia_media_ms"]),
                "valor_base_centavos": int(row["preco_base_centavos"]),
                "valor_excedente_centavos": totais["valor_excedente_centavos"],
                "valor_total_centavos": totais["valor_total_centavos"],
                "valor_total_formatado": formatar_centavos(totais["valor_total_centavos"]),
                "ultimo_consumo_em": (
                    row["ultimo_consumo_em"].isoformat() if row["ultimo_consumo_em"] else None
                ),
                "upgrade_recomendado": upgrade_recomendado,
                "proximo_plano_sugerido": proximo_plano["nome"] if proximo_plano else None,
                "status_fatura": "fechada",
            }
            await _registrar_auditoria_cobranca(
                session=session,
                cliente_id=str(row["cliente_id"]),
                referencia=referencia,
                evento="ciclo_faturamento_fechado",
                ator=payload.ator,
                origem=payload.origem,
                payload=resumo | {"regra_faturamento": regra_faturamento},
            )
            dados.append(resumo)
            total_valor_centavos += totais["valor_total_centavos"]

        await session.commit()

    return {
        "dados": dados,
        "meta": {
            "referencia": referencia,
            "total_clientes": len(dados),
            "valor_total_centavos": total_valor_centavos,
            "valor_total_formatado": formatar_centavos(total_valor_centavos),
        },
    }


async def registrar_upgrade_plano(payload: BillingUpgradeRequest) -> dict:
    async with SessionLocal() as session:
        cliente_result = await session.execute(
            text(
                """
                select
                    cliente.id as cliente_id,
                    cliente.nome as cliente_nome,
                    cliente.plano_id as plano_atual_id,
                    plano.nome as plano_atual_nome,
                    plano.ordem_upgrade as plano_atual_ordem
                from plataforma.cliente cliente
                inner join plataforma.plano plano
                    on plano.id = cliente.plano_id
                where cliente.id = cast(:cliente_id as uuid)
                limit 1
                """
            ),
            {"cliente_id": payload.cliente_id},
        )
        cliente = cliente_result.mappings().first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "CLIENTE_NAO_ENCONTRADO",
                    "mensagem": "Cliente nao encontrado para upgrade.",
                },
            )

        plano_destino_result = await session.execute(
            text(
                """
                select id, nome, ordem_upgrade, permite_upgrade_automatico, status
                from plataforma.plano
                where id = cast(:plano_id as uuid)
                limit 1
                """
            ),
            {"plano_id": payload.plano_destino_id},
        )
        plano_destino = plano_destino_result.mappings().first()
        if not plano_destino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "codigo_erro": "PLANO_NAO_ENCONTRADO",
                    "mensagem": "Plano destino nao encontrado.",
                },
            )
        if plano_destino["status"] != "ativo":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo_erro": "PLANO_INATIVO",
                    "mensagem": "Plano destino nao esta ativo.",
                },
            )
        if str(plano_destino["id"]) == str(cliente["plano_atual_id"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo_erro": "PLANO_IGUAL",
                    "mensagem": "Cliente ja esta no plano informado.",
                },
            )
        if int(plano_destino["ordem_upgrade"]) <= int(cliente["plano_atual_ordem"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo_erro": "UPGRADE_INVALIDO",
                    "mensagem": (
                        "A operacao suporta apenas upgrade imediato "
                        "para um plano superior."
                    ),
                },
            )
        if not bool(plano_destino["permite_upgrade_automatico"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo_erro": "UPGRADE_MANUAL",
                    "mensagem": "Plano destino exige tramitacao manual/comercial.",
                },
            )

        await session.execute(
            text(
                """
                update plataforma.cliente
                set plano_id = cast(:plano_id as uuid)
                where id = cast(:cliente_id as uuid)
                """
            ),
            {"plano_id": str(plano_destino["id"]), "cliente_id": payload.cliente_id},
        )

        nova_chave_api = None
        if payload.rotacionar_chaves:
            update_result = await session.execute(
                text(
                    """
                    update plataforma.chave_api
                    set status = 'rotacionada'
                    where cliente_id = cast(:cliente_id as uuid)
                      and status = 'ativo'
                    """
                ),
                {"cliente_id": payload.cliente_id},
            )
            chaves_atualizadas = update_result.rowcount or 0
            nova_chave_api = _gerar_api_key_rotacionada()
            await session.execute(
                text(
                    """
                    insert into plataforma.chave_api (
                        id,
                        cliente_id,
                        plano_id,
                        hash_chave,
                        prefixo_chave,
                        status
                    ) values (
                        :id,
                        cast(:cliente_id as uuid),
                        cast(:plano_id as uuid),
                        :hash_chave,
                        :prefixo_chave,
                        'ativo'
                    )
                    """
                ),
                {
                    "id": str(uuid4()),
                    "cliente_id": payload.cliente_id,
                    "plano_id": str(plano_destino["id"]),
                    "hash_chave": gerar_hash_sha256(nova_chave_api),
                    "prefixo_chave": nova_chave_api[:10],
                },
            )
        else:
            update_result = await session.execute(
                text(
                    """
                    update plataforma.chave_api
                    set plano_id = cast(:plano_id as uuid)
                    where cliente_id = cast(:cliente_id as uuid)
                      and status = 'ativo'
                    """
                ),
                {"plano_id": str(plano_destino["id"]), "cliente_id": payload.cliente_id},
            )
            chaves_atualizadas = update_result.rowcount or 0

        await session.execute(
            text(
                """
                insert into plataforma.historico_plano (
                    id,
                    cliente_id,
                    plano_origem_id,
                    plano_destino_id,
                    tipo_movimentacao,
                    motivo,
                    origem,
                    solicitado_por,
                    chaves_atualizadas
                ) values (
                    :id,
                    cast(:cliente_id as uuid),
                    cast(:plano_origem_id as uuid),
                    cast(:plano_destino_id as uuid),
                    'upgrade',
                    :motivo,
                    :origem,
                    :solicitado_por,
                    :chaves_atualizadas
                )
                """
            ),
            {
                "id": str(uuid4()),
                "cliente_id": payload.cliente_id,
                "plano_origem_id": str(cliente["plano_atual_id"]),
                "plano_destino_id": str(plano_destino["id"]),
                "motivo": payload.motivo,
                "origem": payload.origem,
                "solicitado_por": payload.ator,
                "chaves_atualizadas": chaves_atualizadas,
            },
        )

        await _registrar_auditoria_cobranca(
            session=session,
            cliente_id=payload.cliente_id,
            referencia=datetime.now(tz=UTC).strftime("%Y-%m"),
            evento="upgrade_plano",
            ator=payload.ator,
            origem=payload.origem,
            payload={
                "cliente_id": payload.cliente_id,
                "cliente_nome": cliente["cliente_nome"],
                "plano_origem_id": str(cliente["plano_atual_id"]),
                "plano_origem_nome": cliente["plano_atual_nome"],
                "plano_destino_id": str(plano_destino["id"]),
                "plano_destino_nome": plano_destino["nome"],
                "motivo": payload.motivo,
                "rotacionar_chaves": payload.rotacionar_chaves,
                "chaves_atualizadas": chaves_atualizadas,
            },
        )
        await session.commit()

    return {
        "dados": {
            "cliente_id": payload.cliente_id,
            "plano_origem_id": str(cliente["plano_atual_id"]),
            "plano_origem_nome": cliente["plano_atual_nome"],
            "plano_destino_id": str(plano_destino["id"]),
            "plano_destino_nome": plano_destino["nome"],
            "motivo": payload.motivo,
            "upgrade_efetivado_em": datetime.now(tz=UTC).isoformat(),
            "chaves_atualizadas": chaves_atualizadas,
            "rotacionou_chaves": payload.rotacionar_chaves,
            "nova_chave_api": nova_chave_api,
        },
        "meta": {
            "ator": payload.ator,
            "origem": payload.origem,
        },
    }


async def criar_chave_api(cliente_id: str, payload: "ChaveCriacaoRequest") -> dict:
    """Cria chave API para um cliente existente. Retorna chave plain-text uma unica vez."""
    prefixo = ("hi_" + secrets.token_urlsafe(7).replace("-", "x").replace("_", "y"))[:10]
    corpo = secrets.token_urlsafe(32)
    chave_plain = f"{prefixo}_{corpo}"
    hash_chave = gerar_hash_sha256(chave_plain)

    async with SessionLocal() as session:
        cliente_row = await session.execute(
            text(
                "SELECT id, plano_id, status, nome FROM plataforma.cliente "
                "WHERE id = cast(:cliente_id as uuid) LIMIT 1"
            ),
            {"cliente_id": cliente_id},
        )
        cliente = cliente_row.mappings().first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"codigo": "CLIENTE_NAO_ENCONTRADO", "mensagem": f"Cliente {cliente_id} nao encontrado."},
            )
        if cliente["status"] != "ativo":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"codigo": "CLIENTE_INATIVO", "mensagem": "Nao e possivel criar chave para cliente inativo."},
            )

        plano_row = await session.execute(
            text("SELECT nome FROM plataforma.plano WHERE id = :plano_id LIMIT 1"),
            {"plano_id": cliente["plano_id"]},
        )
        plano = plano_row.mappings().first()
        plano_nome = plano["nome"] if plano else "desconhecido"

        chave_id = str(uuid4())
        await session.execute(
            text(
                """
                INSERT INTO plataforma.chave_api
                  (id, cliente_id, plano_id, hash_chave, prefixo_chave, status, criado_em)
                VALUES (
                  cast(:chave_id as uuid),
                  cast(:cliente_id as uuid),
                  :plano_id,
                  :hash_chave,
                  :prefixo_chave,
                  'ativo',
                  now()
                )
                """
            ),
            {
                "chave_id": chave_id,
                "cliente_id": cliente_id,
                "plano_id": str(cliente["plano_id"]),
                "hash_chave": hash_chave,
                "prefixo_chave": prefixo,
            },
        )

        await session.execute(
            text(
                """
                INSERT INTO plataforma.auditoria_cobranca
                  (id, evento, cliente_id, ator, origem, payload, criado_em)
                VALUES (
                  gen_random_uuid(),
                  'chave_criada',
                  cast(:cliente_id as uuid),
                  :ator,
                  'admin_billing',
                  cast(:payload as jsonb),
                  now()
                )
                """
            ),
            {
                "cliente_id": cliente_id,
                "ator": payload.ator,
                "payload": json.dumps({"chave_id": chave_id, "descricao": payload.descricao or f"Criada por {payload.ator}"}),
            },
        )
        await session.commit()

    return {
        "dados": {
            "chave_id": chave_id,
            "prefixo": prefixo,
            "chave_plain": chave_plain,
            "cliente_id": cliente_id,
            "plano": plano_nome,
            "criado_em": datetime.now(tz=UTC).isoformat(),
        },
        "meta": {
            "aviso": "Guarde a chave_plain em local seguro. Ela nao sera exibida novamente.",
            "ator": payload.ator,
        },
    }
