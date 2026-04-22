from collections.abc import Callable


def aplicar_alias(coluna_origem: str, aliases: dict[str, str]) -> str:
    try:
        return aliases[coluna_origem]
    except KeyError as exc:
        raise ValueError(f"Alias nao cadastrado para a coluna {coluna_origem}") from exc


def traduzir_registros(
    registros: list[dict],
    colunas_mapeadas: list[dict],
    transformacoes: dict[str, Callable] | None = None,
) -> list[dict]:
    mapa = {item["origem"]: item["destino_raw"] for item in colunas_mapeadas}
    transformacoes = transformacoes or {}
    traduzidos: list[dict] = []
    for registro in registros:
        linha: dict = {}
        for coluna_origem, valor in registro.items():
            if coluna_origem not in mapa:
                continue
            destino = mapa[coluna_origem]
            transformacao = transformacoes.get(destino)
            linha[destino] = transformacao(valor) if transformacao else valor
        traduzidos.append(linha)
    return traduzidos
