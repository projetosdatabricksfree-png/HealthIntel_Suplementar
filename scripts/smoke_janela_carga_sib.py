from __future__ import annotations

import asyncio
import json

from ingestao.app.janela_carga import (
    HistoricoForaDaJanelaError,
    assegurar_dentro_da_janela_ou_falhar,
    obter_janela,
)


async def _validar_bloqueio(competencia: int, janela) -> str:
    try:
        await assegurar_dentro_da_janela_ou_falhar(competencia, janela)
    except HistoricoForaDaJanelaError:
        return "bloqueada"
    return "permitida"


async def main() -> None:
    janela = await obter_janela("sib_operadora")

    status_permitida = "erro"
    await assegurar_dentro_da_janela_ou_falhar(202602, janela)
    status_permitida = "permitida"

    status_abaixo = await _validar_bloqueio(202412, janela)
    status_limite_superior = await _validar_bloqueio(202701, janela)

    resumo = {
        "dataset_codigo": janela.dataset_codigo,
        "janela_minima": janela.competencia_minima,
        "janela_maxima_exclusiva": janela.competencia_maxima_exclusiva,
        "competencia_202602": status_permitida,
        "competencia_202412": status_abaixo,
        "competencia_202701": status_limite_superior,
    }
    print(json.dumps(resumo, ensure_ascii=False, sort_keys=True))

    if status_permitida != "permitida":
        raise SystemExit("Competencia 202602 deveria ser permitida.")
    if status_abaixo != "bloqueada":
        raise SystemExit("Competencia 202412 deveria ser bloqueada.")
    if status_limite_superior != "bloqueada":
        raise SystemExit("Competencia 202701 deveria ser bloqueada pelo limite superior.")


if __name__ == "__main__":
    asyncio.run(main())
