from __future__ import annotations

SCHEMA_SIB_OPERADORA = {
    "obrigatorios": {"competencia", "registro_ans", "beneficiario_total"},
    "inteiros": {"competencia", "beneficiario_medico", "beneficiario_odonto", "beneficiario_total"},
}

SCHEMA_SIB_MUNICIPIO = {
    "obrigatorios": {"competencia", "registro_ans", "codigo_ibge", "beneficiario_total"},
    "inteiros": {"competencia", "beneficiario_medico", "beneficiario_odonto", "beneficiario_total"},
}


def validar_linha_sib(row: dict, schema: dict) -> tuple[bool, str | None]:
    ausentes = [campo for campo in schema["obrigatorios"] if row.get(campo) in (None, "")]
    if ausentes:
        return False, f"campos obrigatorios ausentes: {', '.join(sorted(ausentes))}"
    for campo in schema.get("inteiros", set()):
        valor = row.get(campo)
        if valor in (None, ""):
            continue
        try:
            int(valor)
        except (TypeError, ValueError):
            return False, f"campo {campo} deve ser inteiro"
    return True, None
