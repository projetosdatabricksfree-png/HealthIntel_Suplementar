from __future__ import annotations

import asyncio

from ingestao.app.carregar_postgres import carregar_cadop_bruto


async def main() -> None:
    await carregar_cadop_bruto(
        [
            {
                "registro_ans": "123456",
                "cnpj": "12345678000190",
                "razao_social": "Operadora Demo S/A",
                "nome_fantasia": "Operadora Demo",
                "modalidade": "medicina_de_grupo",
                "cidade": "Sao Paulo",
                "uf": "SP",
                "competencia": 202501,
            }
        ],
        arquivo_origem="cadop_demo_202501.csv",
        layout_id="layout_cadop_csv",
        layout_versao_id="layout_cadop_csv:v1",
        hash_arquivo="hash_demo_cadop_202501",
        hash_estrutura="estrutura_demo_cadop_202501",
    )


if __name__ == "__main__":
    asyncio.run(main())
