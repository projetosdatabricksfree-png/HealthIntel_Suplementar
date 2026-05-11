from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import Request
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.dependencia import verificar_entitlement_historico
from api.app.services.historico_sob_demanda import (
    CompetenciaHistoricaNaoAutorizadaError,
    EntitlementHistoricoAusenteError,
    ExportacaoHistoricaNaoPermitidaError,
    PaginacaoHistoricaInvalidaError,
    validar_acesso_competencia,
    validar_paginacao_historica,
)
from api.tests._psql import aplicar_arquivo

ROOT = Path(__file__).resolve().parents[3]

CLIENTE_PADRAO = "90000000-0000-0000-0000-000000000001"
CLIENTE_PREMIUM = "90000000-0000-0000-0000-000000000002"


@pytest.fixture(scope="module", autouse=True)
def _aplicar_bootstrap_historico() -> None:
    aplicar_arquivo(ROOT / "infra/postgres/init/033_fase7_historico_sob_demanda.sql")


async def _preparar_cliente(session, cliente_id: str, email: str) -> None:
    await session.execute(
        text(
            """
            insert into plataforma.cliente (
                id,
                nome,
                email,
                status,
                plano_id,
                status_cobranca,
                dia_fechamento
            ) values (
                cast(:cliente_id as uuid),
                :nome,
                :email,
                'ativo',
                '11111111-1111-1111-1111-111111111114',
                'em_dia',
                1
            )
            on conflict (email) do update set status = 'ativo'
            """
        ),
        {"cliente_id": cliente_id, "nome": email, "email": email},
    )


@pytest.fixture
async def sessao_historico():
    async with SessionLocal() as session:
        transacao = await session.begin()
        try:
            await _preparar_cliente(session, CLIENTE_PADRAO, "historico-padrao@teste.local")
            await _preparar_cliente(session, CLIENTE_PREMIUM, "historico-premium@teste.local")
            yield session
        finally:
            await transacao.rollback()


@pytest.mark.asyncio
async def test_cliente_padrao_competencia_hot_permitido(sessao_historico) -> None:
    assert await validar_acesso_competencia(
        CLIENTE_PADRAO,
        "sib_operadora",
        202602,
        sessao_historico,
    )


@pytest.mark.asyncio
async def test_cliente_padrao_historico_fora_hot_bloqueado(sessao_historico) -> None:
    with pytest.raises(EntitlementHistoricoAusenteError):
        await validar_acesso_competencia(
            CLIENTE_PADRAO,
            "sib_operadora",
            202401,
            sessao_historico,
        )


@pytest.mark.asyncio
async def test_cliente_premium_entitlement_cobrindo_faixa_permitido(sessao_historico) -> None:
    await sessao_historico.execute(
        text(
            """
            insert into plataforma.cliente_dataset_acesso (
                cliente_id,
                dataset_codigo,
                plano,
                acesso_historico,
                competencia_inicio,
                competencia_fim,
                ativo
            ) values (
                cast(:cliente_id as uuid),
                'sib_operadora',
                'premium_historico',
                true,
                202401,
                202412,
                true
            )
            """
        ),
        {"cliente_id": CLIENTE_PREMIUM},
    )

    assert await validar_acesso_competencia(
        CLIENTE_PREMIUM,
        "sib_operadora",
        202401,
        sessao_historico,
    )


@pytest.mark.asyncio
async def test_cliente_premium_entitlement_inativo_bloqueado(sessao_historico) -> None:
    await sessao_historico.execute(
        text(
            """
            insert into plataforma.cliente_dataset_acesso (
                cliente_id,
                dataset_codigo,
                plano,
                acesso_historico,
                competencia_inicio,
                competencia_fim,
                ativo
            ) values (
                cast(:cliente_id as uuid),
                'sib_operadora',
                'premium_historico',
                true,
                202401,
                202412,
                false
            )
            """
        ),
        {"cliente_id": CLIENTE_PREMIUM},
    )

    with pytest.raises(EntitlementHistoricoAusenteError):
        await validar_acesso_competencia(
            CLIENTE_PREMIUM,
            "sib_operadora",
            202401,
            sessao_historico,
        )


@pytest.mark.asyncio
async def test_cliente_premium_entitlement_nao_cobre_competencia_bloqueado(
    sessao_historico,
) -> None:
    await sessao_historico.execute(
        text(
            """
            insert into plataforma.cliente_dataset_acesso (
                cliente_id,
                dataset_codigo,
                plano,
                acesso_historico,
                competencia_inicio,
                competencia_fim,
                ativo
            ) values (
                cast(:cliente_id as uuid),
                'sib_operadora',
                'premium_historico',
                true,
                202401,
                202412,
                true
            )
            """
        ),
        {"cliente_id": CLIENTE_PREMIUM},
    )

    with pytest.raises(CompetenciaHistoricaNaoAutorizadaError):
        await validar_acesso_competencia(
            CLIENTE_PREMIUM,
            "sib_operadora",
            202301,
            sessao_historico,
        )


def test_validacao_paginacao_limite_maior_que_1000_bloqueia() -> None:
    with pytest.raises(PaginacaoHistoricaInvalidaError):
        validar_paginacao_historica(1001)


def test_exportacao_completa_sem_permissao_bloqueia() -> None:
    with pytest.raises(ExportacaoHistoricaNaoPermitidaError):
        validar_paginacao_historica(1000, modo="csv_completo")


@pytest.mark.asyncio
async def test_dependency_bloqueia_historico_sem_entitlement(monkeypatch) -> None:
    scope = {"type": "http", "method": "GET", "path": "/v1/premium/historico"}
    request = Request(scope)
    request.state.cliente_id = CLIENTE_PADRAO

    async def _bloquear(cliente_id, dataset_codigo, competencia):
        raise EntitlementHistoricoAusenteError("sem entitlement")

    monkeypatch.setattr(
        "api.app.services.historico_sob_demanda.validar_acesso_competencia",
        _bloquear,
    )

    with pytest.raises(Exception) as exc_info:
        await verificar_entitlement_historico(
            request,
            dataset_codigo="sib_operadora",
            competencia=202401,
            limite=100,
        )

    assert getattr(exc_info.value, "status_code", None) == 403
