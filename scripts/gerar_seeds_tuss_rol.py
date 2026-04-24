from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "healthintel_dbt" / "seeds"


@dataclass(frozen=True)
class TussRow:
    codigo_tuss: str
    descricao: str
    grupo: str
    subgrupo: str
    capitulo: str
    vigencia_inicio: str
    vigencia_fim: str


@dataclass(frozen=True)
class RolRow:
    codigo_tuss: str
    descricao: str
    segmento: str
    obrigatorio_medico: str
    obrigatorio_odonto: str
    carencia_dias: int
    vigencia_inicio: str
    vigencia_fim: str


BASE_GRUPOS = [
    ("01", "Consultas", "Atendimento"),
    ("02", "Exames", "Diagnostico"),
    ("03", "Terapias", "Reabilitacao"),
    ("04", "Cirurgias", "Procedimentos"),
    ("05", "Internacoes", "Hospitalar"),
    ("06", "Obstetricia", "Parto"),
    ("07", "Odontologia", "Odonto"),
]

CAPITULOS = {
    "01": "Atendimento",
    "02": "Diagnostico",
    "03": "Terapia",
    "04": "Procedimento",
    "05": "Hospitalar",
    "06": "Materno-infantil",
    "07": "Odontologico",
}


def _escrever_csv(path: Path, cabecalho: list[str], linhas: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
        writer.writeheader()
        writer.writerows(linhas)


def gerar_tuss(total_codigos: int = 3500) -> list[TussRow]:
    linhas: list[TussRow] = []
    for indice in range(1, total_codigos + 1):
        grupo_codigo, grupo_desc, subgrupo_base = BASE_GRUPOS[(indice - 1) % len(BASE_GRUPOS)]
        codigo_tuss = f"{indice:06d}"
        linhas.append(
            TussRow(
                codigo_tuss=codigo_tuss,
                descricao=f"{grupo_desc.upper()} {indice:04d}",
                grupo=grupo_desc.upper(),
                subgrupo=f"{subgrupo_base.upper()} {(indice % 9) + 1}",
                capitulo=CAPITULOS[grupo_codigo],
                vigencia_inicio="2024-01-01",
                vigencia_fim="",
            )
        )
    return linhas


def gerar_rol(tuss: list[TussRow]) -> list[RolRow]:
    linhas: list[RolRow] = []
    for indice, item in enumerate(tuss, start=1):
        linhas.append(
            RolRow(
                codigo_tuss=item.codigo_tuss,
                descricao=item.descricao,
                segmento="MEDICO" if indice % 3 else "ODONTO",
                obrigatorio_medico="SIM" if indice % 2 else "NAO",
                obrigatorio_odonto="SIM" if indice % 5 == 0 else "NAO",
                carencia_dias=30 if indice % 4 else 180,
                vigencia_inicio="2024-01-01",
                vigencia_fim="",
            )
        )
    return linhas


def main() -> None:
    tuss = gerar_tuss()
    rol = gerar_rol(tuss)

    _escrever_csv(
        SEEDS / "ref_tuss.csv",
        [
            "codigo_tuss",
            "descricao",
            "grupo",
            "subgrupo",
            "capitulo",
            "vigencia_inicio",
            "vigencia_fim",
        ],
        [row.__dict__ for row in tuss],
    )
    _escrever_csv(
        SEEDS / "ref_rol_procedimento.csv",
        [
            "codigo_tuss",
            "descricao",
            "segmento",
            "obrigatorio_medico",
            "obrigatorio_odonto",
            "carencia_dias",
            "vigencia_inicio",
            "vigencia_fim",
        ],
        [row.__dict__ for row in rol],
    )


if __name__ == "__main__":
    main()
