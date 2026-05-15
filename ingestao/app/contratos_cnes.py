from __future__ import annotations

SCHEMA_CNES = {
    "obrigatorios": {"cnes", "cd_municipio"},
}


def validar_linha_cnes(row: dict) -> tuple[bool, str | None]:
    ausentes = [c for c in SCHEMA_CNES["obrigatorios"] if row.get(c) in (None, "")]
    if ausentes:
        return False, f"campos obrigatorios ausentes: {', '.join(sorted(ausentes))}"
    cnes_str = "".join(filter(str.isdigit, str(row.get("cnes", ""))))
    if not cnes_str or len(cnes_str) > 7:
        return False, f"cnes invalido: {row.get('cnes')!r}"
    municipio = "".join(filter(str.isdigit, str(row.get("cd_municipio", ""))))
    if not municipio:
        return False, "cd_municipio deve conter digitos"
    return True, None
