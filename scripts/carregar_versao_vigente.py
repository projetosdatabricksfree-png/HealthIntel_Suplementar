from __future__ import annotations

import argparse
import asyncio
from datetime import date
from pathlib import Path

from ingestao.app.carga_versao_vigente import carregar_arquivo_versao_vigente


def _parse_data(valor: str | None) -> date | None:
    if not valor:
        return None
    return date.fromisoformat(valor)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega dataset de referência/snapshot como última versão vigente."
    )
    parser.add_argument("--dataset", required=True, help="dataset_codigo em politica_dataset")
    parser.add_argument("--arquivo", required=True, help="Caminho local do CSV/TXT/ZIP")
    parser.add_argument("--versao", required=True, help="Identificador da versão vigente")
    parser.add_argument("--url-fonte", help="URL/caminho de origem oficial para auditoria")
    parser.add_argument("--publicado-em", help="Data de publicação oficial YYYY-MM-DD")
    return parser.parse_args()


async def main_async() -> None:
    args = parse_args()
    resultado = await carregar_arquivo_versao_vigente(
        args.dataset,
        Path(args.arquivo),
        versao=args.versao,
        url_fonte=args.url_fonte,
        publicado_em=_parse_data(args.publicado_em),
    )
    print(
        "status={status} dataset={dataset} tabela={tabela} versao={versao} "
        "linhas_carregadas={linhas} linhas_removidas={removidas} hash={hash_arquivo}".format(
            status=resultado.status_manifesto,
            dataset=resultado.dataset_codigo,
            tabela=resultado.tabela_destino,
            versao=resultado.versao,
            linhas=resultado.linhas_carregadas,
            removidas=resultado.linhas_removidas,
            hash_arquivo=resultado.hash_arquivo,
        )
    )


if __name__ == "__main__":
    asyncio.run(main_async())
