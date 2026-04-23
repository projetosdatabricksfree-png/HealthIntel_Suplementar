import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import (
    SessionLocal,
    carregar_cadop_bruto,
    carregar_sib_municipio_bruto,
    carregar_sib_operadora_bruto,
)


async def seed_demo() -> None:
    await carregar_cadop_bruto(
        [
            {
                "registro_ans": "123456",
                "cnpj": "12.345.678/0001-90",
                "razao_social": "Operadora Exemplo S/A",
                "nome_fantasia": "Operadora Exemplo",
                "modalidade": "medicina_de_grupo",
                "cidade": "Sao Paulo",
                "uf": "SP",
                "competencia": "202603",
            },
            {
                "registro_ans": "654321",
                "cnpj": "98.765.432/0001-10",
                "razao_social": "Vida Integral Assistencia Medica",
                "nome_fantasia": "Vida Integral",
                "modalidade": "cooperativa_medica",
                "cidade": "Belo Horizonte",
                "uf": "MG",
                "competencia": "202603",
            },
        ],
        arquivo_origem="cadop_demo.csv",
        layout_id="layout_cadop_demo",
        layout_versao_id="layout_cadop_demo_v1",
        hash_arquivo="hash_demo_cadop",
        hash_estrutura="estrutura_demo_cadop",
    )

    await carregar_sib_operadora_bruto(
        [
            {
                "competencia": "202602",
                "registro_ans": "123456",
                "beneficiario_medico": 1000,
                "beneficiario_odonto": 150,
                "beneficiario_total": 1150,
            },
            {
                "competencia": "202602",
                "registro_ans": "654321",
                "beneficiario_medico": 700,
                "beneficiario_odonto": 120,
                "beneficiario_total": 820,
            },
        ],
        arquivo_origem="sib_operadora_demo_202602.csv",
        layout_id="layout_sib_operadora_demo",
        layout_versao_id="layout_sib_operadora_demo_v1",
        hash_arquivo="hash_demo_sib_operadora_202602",
        hash_estrutura="estrutura_demo_sib_operadora",
    )

    await carregar_sib_operadora_bruto(
        [
            {
                "competencia": "202603",
                "registro_ans": "123456",
                "beneficiario_medico": 1050,
                "beneficiario_odonto": 180,
                "beneficiario_total": 1230,
            },
            {
                "competencia": "202603",
                "registro_ans": "654321",
                "beneficiario_medico": 710,
                "beneficiario_odonto": 130,
                "beneficiario_total": 840,
            },
        ],
        arquivo_origem="sib_operadora_demo_202603.csv",
        layout_id="layout_sib_operadora_demo",
        layout_versao_id="layout_sib_operadora_demo_v1",
        hash_arquivo="hash_demo_sib_operadora_202603",
        hash_estrutura="estrutura_demo_sib_operadora",
    )

    await carregar_sib_municipio_bruto(
        [
            {
                "competencia": "202603",
                "registro_ans": "123456",
                "codigo_ibge": "3550308",
                "municipio": "Sao Paulo",
                "uf": "SP",
                "beneficiario_medico": 900,
                "beneficiario_odonto": 140,
                "beneficiario_total": 1040,
            },
            {
                "competencia": "202603",
                "registro_ans": "654321",
                "codigo_ibge": "3106200",
                "municipio": "Belo Horizonte",
                "uf": "MG",
                "beneficiario_medico": 630,
                "beneficiario_odonto": 110,
                "beneficiario_total": 740,
            },
        ],
        arquivo_origem="sib_municipio_demo.csv",
        layout_id="layout_sib_municipio_demo",
        layout_versao_id="layout_sib_municipio_demo_v1",
        hash_arquivo="hash_demo_sib_municipio",
        hash_estrutura="estrutura_demo_sib_municipio",
    )

    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                insert into plataforma.job (
                    id,
                    dag_id,
                    nome_job,
                    fonte_ans,
                    status,
                    iniciado_em,
                    finalizado_em,
                    registro_processado,
                    registro_com_falha
                ) values (
                    :id,
                    :dag_id,
                    :nome_job,
                    :fonte_ans,
                    :status,
                    :iniciado_em,
                    :finalizado_em,
                    :registro_processado,
                    :registro_com_falha
                )
                on conflict do nothing
                """
            ),
            {
                "id": str(uuid4()),
                "dag_id": "dag_mestre_mensal",
                "nome_job": "seed_demo_core",
                "fonte_ans": "demo_local",
                "status": "sucesso",
                "iniciado_em": datetime.now(tz=UTC),
                "finalizado_em": datetime.now(tz=UTC),
                "registro_processado": 8,
                "registro_com_falha": 0,
            },
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_demo())
