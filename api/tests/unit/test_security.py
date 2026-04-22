from api.app.core.security import gerar_hash_sha256, hash_ip


def test_gerar_hash_sha256_deve_ser_deterministico() -> None:
    assert gerar_hash_sha256("abc") == gerar_hash_sha256("abc")


def test_hash_ip_deve_retornar_none_sem_ip() -> None:
    assert hash_ip(None) is None
