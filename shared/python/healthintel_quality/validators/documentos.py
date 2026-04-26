"""Validacao tecnica de CPF, CNPJ e hashes documentais.

As funcoes deste modulo sao puramente locais: nao consultam APIs externas,
nao enriquecem cadastro e nao transformam CPF em produto publico.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterable
from typing import Literal

TipoDocumento = Literal["CPF", "CNPJ", "INVALIDO"]

_DIGITO_REGEX = re.compile(r"\D+")
_CPF_TAMANHO = 11
_CNPJ_TAMANHO = 14
_CNPJ_PESO_PRIMEIRO_DIGITO = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_CNPJ_PESO_SEGUNDO_DIGITO = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_HASH_SALT_ENV = "HEALTHINTEL_DOCUMENTO_HASH_SALT"


def _somente_digito(valor: object) -> str | None:
    if valor is None:
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    digito = _DIGITO_REGEX.sub("", texto)
    return digito or None


def _is_sequencia_invalida(documento: str) -> bool:
    return len(set(documento)) == 1


def _calcular_digito_verificador(digito_base: str, peso: Iterable[int]) -> int:
    soma = sum(
        int(digito) * multiplicador
        for digito, multiplicador in zip(digito_base, peso, strict=True)
    )
    resto = soma % 11
    verificador = 11 - resto
    return 0 if verificador >= 10 else verificador


def normalizar_cpf(valor: object) -> str | None:
    """Remove caracteres nao numericos de um CPF sem completar zeros."""

    return _somente_digito(valor)


def normalizar_cnpj(valor: object) -> str | None:
    """Remove caracteres nao numericos de um CNPJ sem completar zeros."""

    return _somente_digito(valor)


def validar_cpf_digito(valor: object) -> bool:
    """Valida tamanho, sequencia repetida e digitos verificadores de CPF."""

    cpf = normalizar_cpf(valor)
    if cpf is None or len(cpf) != _CPF_TAMANHO or _is_sequencia_invalida(cpf):
        return False

    primeiro_digito = _calcular_digito_verificador(cpf[:9], range(10, 1, -1))
    segundo_digito = _calcular_digito_verificador(cpf[:9] + str(primeiro_digito), range(11, 1, -1))

    return cpf[-2:] == f"{primeiro_digito}{segundo_digito}"


def validar_cnpj_digito(valor: object) -> bool:
    """Valida tamanho, sequencia repetida e digitos verificadores de CNPJ."""

    cnpj = normalizar_cnpj(valor)
    if cnpj is None or len(cnpj) != _CNPJ_TAMANHO or _is_sequencia_invalida(cnpj):
        return False

    primeiro_digito = _calcular_digito_verificador(cnpj[:12], _CNPJ_PESO_PRIMEIRO_DIGITO)
    segundo_digito = _calcular_digito_verificador(
        cnpj[:12] + str(primeiro_digito),
        _CNPJ_PESO_SEGUNDO_DIGITO,
    )

    return cnpj[-2:] == f"{primeiro_digito}{segundo_digito}"


def classificar_documento(valor: object) -> TipoDocumento:
    """Classifica documento somente quando o digito verificador e valido."""

    documento = _somente_digito(valor)
    if documento is None:
        return "INVALIDO"

    if len(documento) == _CPF_TAMANHO and validar_cpf_digito(documento):
        return "CPF"

    if len(documento) == _CNPJ_TAMANHO and validar_cnpj_digito(documento):
        return "CNPJ"

    return "INVALIDO"


def gerar_hash_documento(valor: object, *, salt: str | None = None) -> str | None:
    """Gera SHA-256 de documento valido com salt configuravel.

    Quando ``salt`` nao e informado, a funcao usa a variavel de ambiente
    ``HEALTHINTEL_DOCUMENTO_HASH_SALT``. A ausencia de salt explicito nao
    introduz segredo hardcoded; apenas preserva determinismo em validacoes.
    """

    tipo_documento = classificar_documento(valor)
    if tipo_documento == "INVALIDO":
        return None

    documento = _somente_digito(valor)
    salt_resolvido = os.getenv(_HASH_SALT_ENV, "") if salt is None else salt
    conteudo = f"{salt_resolvido}:{tipo_documento}:{documento}".encode("utf-8")
    return hashlib.sha256(conteudo).hexdigest()
