from healthintel_quality.validators.documentos import (
    classificar_documento,
    gerar_hash_documento,
    normalizar_cnpj,
    normalizar_cpf,
    validar_cnpj_digito,
    validar_cpf_digito,
)


def test_normalizar_cpf_remove_mascara_sem_completar_zeros() -> None:
    assert normalizar_cpf("529.982.247-25") == "52998224725"
    assert normalizar_cpf("  123  ") == "123"
    assert normalizar_cpf("") is None
    assert normalizar_cpf(None) is None


def test_normalizar_cnpj_remove_mascara_sem_completar_zeros() -> None:
    assert normalizar_cnpj("04.252.011/0001-10") == "04252011000110"
    assert normalizar_cnpj("abc") is None


def test_validar_cpf_digito_aceita_cpf_valido() -> None:
    assert validar_cpf_digito("529.982.247-25") is True
    assert validar_cpf_digito("111.444.777-35") is True


def test_validar_cpf_digito_rejeita_cpf_invalido() -> None:
    assert validar_cpf_digito("529.982.247-24") is False
    assert validar_cpf_digito("11111111111") is False
    assert validar_cpf_digito("123") is False
    assert validar_cpf_digito(None) is False


def test_validar_cnpj_digito_aceita_cnpj_valido() -> None:
    assert validar_cnpj_digito("04.252.011/0001-10") is True
    assert validar_cnpj_digito("40.688.134/0001-61") is True


def test_validar_cnpj_digito_rejeita_cnpj_invalido() -> None:
    assert validar_cnpj_digito("04.252.011/0001-11") is False
    assert validar_cnpj_digito("00000000000000") is False
    assert validar_cnpj_digito("123") is False
    assert validar_cnpj_digito(None) is False


def test_classificar_documento_retornar_tipo_apenas_para_documento_valido() -> None:
    assert classificar_documento("529.982.247-25") == "CPF"
    assert classificar_documento("04.252.011/0001-10") == "CNPJ"
    assert classificar_documento("04.252.011/0001-11") == "INVALIDO"
    assert classificar_documento(None) == "INVALIDO"


def test_gerar_hash_documento_usa_salt_parametrico() -> None:
    hash_a = gerar_hash_documento("04.252.011/0001-10", salt="salt-a")
    hash_a_repetido = gerar_hash_documento("04252011000110", salt="salt-a")
    hash_b = gerar_hash_documento("04.252.011/0001-10", salt="salt-b")

    assert hash_a == hash_a_repetido
    assert hash_a != hash_b
    assert hash_a is not None
    assert len(hash_a) == 64


def test_gerar_hash_documento_rejeita_documento_invalido() -> None:
    assert gerar_hash_documento("00000000000", salt="salt") is None
