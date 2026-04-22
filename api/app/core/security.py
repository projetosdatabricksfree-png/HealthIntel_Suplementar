from hashlib import sha256


def gerar_hash_sha256(valor: str) -> str:
    return sha256(valor.encode("utf-8")).hexdigest()


def hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return gerar_hash_sha256(ip)
