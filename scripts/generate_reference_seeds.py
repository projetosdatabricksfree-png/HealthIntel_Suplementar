from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "healthintel_dbt" / "seeds"


UFS = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapa"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceara"),
    ("DF", "Distrito Federal"),
    ("ES", "Espirito Santo"),
    ("GO", "Goias"),
    ("MA", "Maranhao"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Para"),
    ("PB", "Paraiba"),
    ("PR", "Parana"),
    ("PE", "Pernambuco"),
    ("PI", "Piaui"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondonia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "Sao Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

MODALIDADES = [
    ("MEDICINA_DE_GRUPO", "Medicina de grupo"),
    ("COOPERATIVA_MEDICA", "Cooperativa medica"),
    ("FILANTROPICA", "Filantropica"),
    ("AUTOGESTAO", "Autogestao"),
    ("SEGURADORA_ESPECIALIZADA_EM_SAUDE", "Seguradora especializada em saude"),
    ("ADMINISTRADORA_DE_BENEFICIOS", "Administradora de beneficios"),
    ("ODONTOLOGIA_DE_GRUPO", "Odontologia de grupo"),
    ("COOPERATIVA_ODONTOLOGICA", "Cooperativa odontologica"),
]


def escrever_csv(path: Path, cabecalho: list[str], linhas: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
        writer.writeheader()
        writer.writerows(linhas)


def gerar_competencias() -> None:
    linhas: list[dict[str, object]] = []
    ano, mes = 2015, 1
    while (ano, mes) <= (2030, 12):
        linhas.append({"competencia": f"{ano}{mes:02d}", "ano": ano, "mes": mes})
        mes += 1
        if mes == 13:
            mes = 1
            ano += 1
    escrever_csv(SEEDS / "ref_competencia.csv", ["competencia", "ano", "mes"], linhas)


def gerar_ufs() -> None:
    escrever_csv(
        SEEDS / "ref_uf.csv",
        ["uf", "nome"],
        [{"uf": uf, "nome": nome} for uf, nome in UFS],
    )


def gerar_modalidades() -> None:
    escrever_csv(
        SEEDS / "ref_modalidade.csv",
        ["modalidade", "descricao"],
        [{"modalidade": modalidade, "descricao": descricao} for modalidade, descricao in MODALIDADES],
    )


def gerar_municipios() -> None:
    response = httpx.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
        timeout=60.0,
    )
    response.raise_for_status()
    municipios = response.json()

    linhas = []
    for municipio in municipios:
        uf = None
        regiao = None
        microrregiao = municipio.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}
        uf_info = mesorregiao.get("UF") or {}
        if uf_info:
            uf = uf_info.get("sigla")
            regiao = uf_info.get("regiao", {}).get("nome")
        if not uf:
            regiao_imediata = municipio.get("regiao-imediata") or {}
            regiao_intermediaria = regiao_imediata.get("regiao-intermediaria") or {}
            uf_info = regiao_intermediaria.get("UF") or {}
            uf = uf_info.get("sigla")
            regiao = uf_info.get("regiao", {}).get("nome")
        linhas.append(
            {
                "codigo_ibge": str(municipio["id"]).zfill(7),
                "nm_municipio": municipio["nome"].upper(),
                "sg_uf": (uf or "NA").upper(),
                "nm_regiao": (regiao or "NAO INFORMADA").upper(),
            }
        )
    linhas.sort(key=lambda linha: linha["codigo_ibge"])
    escrever_csv(
        SEEDS / "ref_municipio_ibge.csv",
        ["codigo_ibge", "nm_municipio", "sg_uf", "nm_regiao"],
        linhas,
    )


def main() -> None:
    gerar_ufs()
    gerar_modalidades()
    gerar_competencias()
    gerar_municipios()


if __name__ == "__main__":
    main()
