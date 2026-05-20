"""Testes unitários dos validadores brasileiros (CNPJ, telefone)."""

from api.app.util.validators_br import (
    normalizar_cnpj,
    normalizar_telefone,
    validar_cnpj,
    validar_telefone_br,
)


def test_validar_cnpj_valido_sem_pontuacao():
    assert validar_cnpj("53936542000137") is True


def test_validar_cnpj_valido_com_pontuacao():
    assert validar_cnpj("53.936.542/0001-37") is True


def test_validar_cnpj_invalido_dv_errado():
    assert validar_cnpj("53936542000138") is False


def test_validar_cnpj_invalido_repetido():
    assert validar_cnpj("11111111111111") is False


def test_validar_cnpj_invalido_tamanho_errado():
    assert validar_cnpj("123") is False
    assert validar_cnpj("") is False


def test_normalizar_cnpj_strip_pontuacao():
    assert normalizar_cnpj("53.936.542/0001-37") == "53936542000137"


def test_validar_telefone_celular_11():
    assert validar_telefone_br("(11) 98765-4321") is True


def test_validar_telefone_fixo_10():
    assert validar_telefone_br("(11) 3456-7890") is True


def test_validar_telefone_com_55():
    assert validar_telefone_br("+55 11 98765-4321") is True


def test_validar_telefone_invalido_curto():
    assert validar_telefone_br("123") is False


def test_validar_telefone_invalido_ddd_zero():
    assert validar_telefone_br("(01) 98765-4321") is False


def test_normalizar_telefone():
    assert normalizar_telefone("(11) 98765-4321") == "11987654321"
