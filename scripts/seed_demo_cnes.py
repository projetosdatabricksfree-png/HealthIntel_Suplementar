from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from itertools import cycle

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal, carregar_cnes_bruto

MUNICIPIOS = [
    ("3550308", "SAO PAULO", "SP"),
    ("3106200", "BELO HORIZONTE", "MG"),
    ("3304557", "RIO DE JANEIRO", "RJ"),
    ("5300108", "BRASILIA", "DF"),
    ("2611606", "RECIFE", "PE"),
]

TIPOS = [
    ("01", "HOSPITAL GERAL"),
    ("02", "CLINICA ESPECIALIZADA"),
    ("03", "UNIDADE BASICA"),
    ("04", "PRONTO ATENDIMENTO"),
]


async def _limpar_demo() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                delete from bruto_ans.cnes_estabelecimento
                where _arquivo_origem like 'cnes_demo_%'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.versao_dataset
                where dataset = 'cnes_estabelecimento'
                  and status = 'demo_local_cnes'
                """
            )
        )
        await session.execute(
            text(
                """
                delete from plataforma.job
                where nome_job = 'seed_demo_cnes'
                """
            )
        )
        await session.commit()


def _gerar_registros() -> list[dict[str, object]]:
    registros: list[dict[str, object]] = []
    cnes_seq = 7000000
    for municipio, tipo in zip(cycle(MUNICIPIOS), cycle(TIPOS), strict=False):
        if len(registros) >= 60:
            break
        cd_municipio, nm_municipio, sg_uf = municipio
        tipo_codigo, tipo_desc = tipo
        indice = len(registros) + 1
        registros.append(
            {
                "competencia": "202501",
                "cnes": str(cnes_seq + indice),
                "cnpj": f"{indice:014d}",
                "razao_social": f"ESTABELECIMENTO DEMO {indice:03d}",
                "nome_fantasia": f"UNIDADE DEMO {indice:03d}",
                "sg_uf": sg_uf,
                "cd_municipio": cd_municipio,
                "nm_municipio": nm_municipio,
                "tipo_unidade": tipo_codigo,
                "tipo_unidade_desc": tipo_desc,
                "esfera_administrativa": "MUNICIPAL",
                "vinculo_sus": indice % 2 == 0,
                "leitos_existentes": 10 + indice,
                "leitos_sus": 6 + (indice % 5),
                "latitude": -23.5 + (indice / 1000),
                "longitude": -46.6 - (indice / 1000),
                "situacao": "ATIVO",
                "fonte_publicacao": "cnes_demo_202501",
            }
        )
    return registros


async def main() -> None:
    await _limpar_demo()
    registros = _gerar_registros()
    await carregar_cnes_bruto(
        registros,
        arquivo_origem="cnes_demo_202501.csv",
        layout_id="layout_cnes_estabelecimento_csv",
        layout_versao_id="layout_cnes_estabelecimento_csv:v1",
        hash_arquivo="demo_hash_cnes",
        hash_estrutura="demo_hash_estrutura_cnes",
    )
    print(
        {
            "status": "ok",
            "registros": len(registros),
            "competencia": "202501",
            "gerado_em": datetime.now(tz=UTC).isoformat(),
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
