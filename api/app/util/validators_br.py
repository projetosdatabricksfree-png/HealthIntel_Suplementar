"""Validadores e normalizadores para dados brasileiros (CNPJ, telefone)."""

from __future__ import annotations

import re

_CNPJ_PESOS_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_CNPJ_PESOS_2 = [6] + _CNPJ_PESOS_1


def normalizar_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj or "")


def validar_cnpj(cnpj: str) -> bool:
    digits = normalizar_cnpj(cnpj)
    if len(digits) != 14 or digits == digits[0] * 14:
        return False

    base = digits[:12]
    soma1 = sum(int(base[i]) * _CNPJ_PESOS_1[i] for i in range(12))
    dv1 = 0 if soma1 % 11 < 2 else 11 - (soma1 % 11)
    if dv1 != int(digits[12]):
        return False

    base2 = base + str(dv1)
    soma2 = sum(int(base2[i]) * _CNPJ_PESOS_2[i] for i in range(13))
    dv2 = 0 if soma2 % 11 < 2 else 11 - (soma2 % 11)
    return dv2 == int(digits[13])


def normalizar_telefone(tel: str) -> str:
    return re.sub(r"\D", "", tel or "")


def validar_telefone_br(tel: str) -> bool:
    digits = normalizar_telefone(tel)
    if not (10 <= len(digits) <= 13):
        return False
    if digits.startswith("55"):
        digits = digits[2:]
    if len(digits) not in (10, 11):
        return False
    ddd = int(digits[:2])
    return 11 <= ddd <= 99
