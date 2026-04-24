from __future__ import annotations

import asyncio

from ingestao.app.carregar_postgres import (
    carregar_sib_municipio_bruto,
    carregar_sib_operadora_bruto,
)


async def main() -> None:
    await carregar_sib_operadora_bruto(
        [
            {
                "competencia": "202501",
                "registro_ans": "123456",
                "beneficiario_medico": 1000,
                "beneficiario_odonto": 100,
                "beneficiario_total": 1100,
            }
        ],
        arquivo_origem="sib_operadora_demo_202501.csv",
        layout_id="layout_sib_operadora_csv",
        layout_versao_id="layout_sib_operadora_csv:v1",
        hash_arquivo="hash_demo_sib_operadora_202501",
        hash_estrutura="estrutura_demo_sib_operadora_202501",
    )
    await carregar_sib_municipio_bruto(
        [
            {
                "competencia": "202501",
                "registro_ans": "123456",
                "codigo_ibge": "3550308",
                "municipio": "Sao Paulo",
                "uf": "SP",
                "beneficiario_medico": 900,
                "beneficiario_odonto": 90,
                "beneficiario_total": 990,
            }
        ],
        arquivo_origem="sib_municipio_demo_202501.csv",
        layout_id="layout_sib_municipio_csv",
        layout_versao_id="layout_sib_municipio_csv:v1",
        hash_arquivo="hash_demo_sib_municipio_202501",
        hash_estrutura="estrutura_demo_sib_municipio_202501",
    )


if __name__ == "__main__":
    asyncio.run(main())
