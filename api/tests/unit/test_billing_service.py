from api.app.services.billing import calcular_totais_fatura, formatar_centavos


def test_calcular_totais_fatura_sem_excedente() -> None:
    resultado = calcular_totais_fatura(
        requisicoes_faturaveis=4200,
        franquia_requisicoes_mes=5000,
        preco_base_centavos=249000,
        preco_excedente_mil_requisicoes_centavos=3500,
    )

    assert resultado["requisicoes_excedentes"] == 0
    assert resultado["blocos_excedentes"] == 0
    assert resultado["valor_excedente_centavos"] == 0
    assert resultado["valor_total_centavos"] == 249000


def test_calcular_totais_fatura_com_excedente_arredonda_bloco() -> None:
    resultado = calcular_totais_fatura(
        requisicoes_faturaveis=6201,
        franquia_requisicoes_mes=5000,
        preco_base_centavos=249000,
        preco_excedente_mil_requisicoes_centavos=3500,
    )

    assert resultado["requisicoes_excedentes"] == 1201
    assert resultado["blocos_excedentes"] == 2
    assert resultado["valor_excedente_centavos"] == 7000
    assert resultado["valor_total_centavos"] == 256000


def test_formatar_centavos_retorna_string_monetaria() -> None:
    assert formatar_centavos(256000) == "R$ 2.560,00"
