import pytest

from ingestao.app.aplicar_alias import aplicar_alias, traduzir_registros


def test_aplicar_alias_existente() -> None:
    aliases = {"competência": "competencia"}
    assert aplicar_alias("competência", aliases) == "competencia"


def test_aplicar_alias_inexistente() -> None:
    with pytest.raises(ValueError):
        aplicar_alias("data_inicio", {"competencia": "competencia"})


def test_traduzir_registros_para_destino_raw() -> None:
    registros = [
        {"competência": "202603", "Registro ANS": "123"},
        {"competência": "202604", "Registro ANS": "456"},
    ]
    colunas_mapeadas = [
        {"origem": "competência", "destino_raw": "competencia"},
        {"origem": "Registro ANS", "destino_raw": "registro_ans"},
    ]

    traduzidos = traduzir_registros(
        registros,
        colunas_mapeadas,
        transformacoes={
            "competencia": lambda valor: int(valor),
            "registro_ans": lambda valor: str(valor).zfill(6),
        },
    )

    assert traduzidos == [
        {"competencia": 202603, "registro_ans": "000123"},
        {"competencia": 202604, "registro_ans": "000456"},
    ]
