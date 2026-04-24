from __future__ import annotations

SCHEMA_CADOP = {
    "obrigatorios": {"registro_ans", "razao_social", "cnpj"},
}


def validar_linha_cadop(row: dict) -> tuple[bool, str | None]:
    ausentes = [campo for campo in SCHEMA_CADOP["obrigatorios"] if row.get(campo) in (None, "")]
    if ausentes:
        return False, f"campos obrigatorios ausentes: {', '.join(sorted(ausentes))}"
    cnpj = "".join(filter(str.isdigit, str(row.get("cnpj", ""))))
    if len(cnpj) != 14:
        return False, "cnpj deve conter 14 digitos"
    return True, None
