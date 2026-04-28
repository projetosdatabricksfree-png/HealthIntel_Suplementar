from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from sqlalchemy import text

from ingestao.app.carga_versao_vigente import carregar_arquivo_versao_vigente
from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.versao_vigente import obter_versao_vigente


def _criar_csv(path: Path, codigo_base: int) -> None:
    path.write_text(
        "\n".join(
            [
                "codigo_tuss;descricao;grupo;subgrupo;capitulo",
                f"{codigo_base};Consulta vigente;CONSULTAS;ATENDIMENTO;AMBULATORIAL",
                f"{codigo_base + 1};Exame vigente;EXAMES;DIAGNOSTICO;DIAGNOSTICO",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


async def main_async() -> None:
    with tempfile.TemporaryDirectory(prefix="healthintel_tuss_") as tempdir:
        arquivo_v1 = Path(tempdir) / "tuss_v1.csv"
        arquivo_v2 = Path(tempdir) / "tuss_v2.csv"
        _criar_csv(arquivo_v1, 101010)
        _criar_csv(arquivo_v2, 202020)

        async with SessionLocal() as session:
            transacao = await session.begin()
            try:
                resultado_v1 = await carregar_arquivo_versao_vigente(
                    "tuss_procedimento",
                    arquivo_v1,
                    versao="smoke_2026_01",
                    url_fonte="https://www.gov.br/ans/smoke/tuss_v1.csv",
                    conn=session,
                )
                resultado_v2 = await carregar_arquivo_versao_vigente(
                    "tuss_procedimento",
                    arquivo_v2,
                    versao="smoke_2026_02",
                    url_fonte="https://www.gov.br/ans/smoke/tuss_v2.csv",
                    conn=session,
                )
                versao_vigente = await obter_versao_vigente("tuss_procedimento", session)
                total_versoes_raw = await session.scalar(
                    text(
                        """
                        select count(distinct versao_dataset)
                        from bruto_ans.tuss_procedimento
                        """
                    )
                )
                total_vigentes = await session.scalar(
                    text(
                        """
                        select count(*)
                        from plataforma.versao_dataset_vigente
                        where dataset_codigo = 'tuss_procedimento'
                          and vigente is true
                        """
                    )
                )
                if resultado_v1.linhas_carregadas != 2:
                    raise RuntimeError("Carga inicial TUSS nao carregou 2 linhas.")
                if resultado_v2.linhas_carregadas != 2:
                    raise RuntimeError("Carga nova TUSS nao carregou 2 linhas.")
                if resultado_v2.linhas_removidas != 2:
                    raise RuntimeError("Carga nova TUSS nao removeu a versao anterior.")
                if versao_vigente is None or versao_vigente.versao != "smoke_2026_02":
                    raise RuntimeError("Manifesto vigente TUSS nao aponta para a ultima versao.")
                if int(total_versoes_raw or 0) != 1:
                    raise RuntimeError("Raw TUSS manteve mais de uma versao_dataset.")
                if int(total_vigentes or 0) != 1:
                    raise RuntimeError("Manifesto TUSS tem quantidade invalida de vigentes.")

                print(
                    "ok smoke_versao_vigente_tuss "
                    f"vigente={versao_vigente.versao} "
                    f"raw_versoes={total_versoes_raw} "
                    f"manifesto_vigentes={total_vigentes}"
                )
            finally:
                await transacao.rollback()


if __name__ == "__main__":
    asyncio.run(main_async())
