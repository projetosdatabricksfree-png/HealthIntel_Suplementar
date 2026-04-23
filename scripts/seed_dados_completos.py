#!/usr/bin/env python3
"""Seed volumoso — popula todas as tabelas bruto_ans com ~100 operadoras e múltiplos períodos."""
from __future__ import annotations

import asyncio
import random
from datetime import date

from ingestao.app.carregar_postgres import (
    carregar_cadop_bruto,
    carregar_diops_bruto,
    carregar_fip_bruto,
    carregar_glosa_bruto,
    carregar_idss_bruto,
    carregar_igr_bruto,
    carregar_nip_bruto,
    carregar_portabilidade_bruto,
    carregar_prudencial_bruto,
    carregar_rede_assistencial_bruto,
    carregar_regime_especial_bruto,
    carregar_rn623_lista_bruto,
    carregar_sib_municipio_bruto,
    carregar_sib_operadora_bruto,
    carregar_taxa_resolutividade_bruto,
    carregar_vda_bruto,
)

RNG = random.Random(42)

# ── Períodos ─────────────────────────────────────────────────────────────────

MESES = [
    "202401", "202402", "202403", "202404", "202405", "202406",
    "202407", "202408", "202409", "202410", "202411", "202412",
    "202501", "202502", "202503", "202504", "202505", "202506",
    "202507", "202508", "202509", "202510", "202511", "202512",
    "202601", "202602", "202603",
]

TRIMESTRES = ["2024T1", "2024T2", "2024T3", "2024T4", "2025T1", "2025T2", "2025T3", "2025T4"]
ANOS_IDSS = [2022, 2023, 2024]

MESES_RECENTES = MESES[-12:]      # últimos 12 meses
MESES_3 = MESES[-3:]              # últimos 3 meses

# ── Operadoras ────────────────────────────────────────────────────────────────
# (registro_ans, razao_social, nome_fantasia, modalidade, cnpj, cidade, uf)

OPERADORAS = [
    # Grandes operadoras conhecidas
    ("326305", "Amil Assistencia Medica Internacional SA", "Amil", "medicina_de_grupo", "29.978.814/0001-87", "Rio de Janeiro", "RJ"),
    ("005711", "Bradesco Saude SA", "Bradesco Saude", "seguradora_especializada_em_saude", "92.693.038/0001-17", "Sao Paulo", "SP"),
    ("006246", "Sul America Companhia de Seguro Saude", "SulAmerica", "seguradora_especializada_em_saude", "01.685.053/0001-56", "Rio de Janeiro", "RJ"),
    ("368253", "Unimed do Brasil Cooperativa Central", "Unimed Brasil", "cooperativa_medica", "81.955.106/0001-00", "Brasilia", "DF"),
    ("009440", "Porto Seguro Companhia de Seguros Gerais", "Porto Seguro Saude", "seguradora_especializada_em_saude", "61.198.164/0001-60", "Sao Paulo", "SP"),
    ("368786", "Hapvida Assistencia Medica Ltda", "Hapvida", "medicina_de_grupo", "04.829.754/0001-56", "Fortaleza", "CE"),
    ("359017", "Notre Dame Intermedica Saude SA", "Intermedica", "medicina_de_grupo", "44.649.812/0001-38", "Sao Paulo", "SP"),
    ("356064", "Prevent Senior Private Operadora de Saude Ltda", "Prevent Senior", "medicina_de_grupo", "09.395.880/0001-78", "Sao Paulo", "SP"),
    ("000701", "Golden Cross Assistencia Internacional de Saude Ltda", "Golden Cross", "medicina_de_grupo", "33.191.581/0001-76", "Rio de Janeiro", "RJ"),
    ("008079", "Omint Servicos de Saude Ltda", "Omint", "medicina_de_grupo", "43.069.291/0001-50", "Sao Paulo", "SP"),
    ("001210", "OdontoPrev SA", "OdontoPrev", "odontologia_de_grupo", "58.119.199/0001-51", "Barueri", "SP"),
    ("003115", "Unimed Belo Horizonte Cooperativa de Trabalho Medico", "Unimed BH", "cooperativa_medica", "17.238.958/0001-80", "Belo Horizonte", "MG"),
    ("004731", "Medial Saude SA", "Medial Saude", "medicina_de_grupo", "07.829.109/0001-72", "Sao Paulo", "SP"),
    ("300073", "Allianz Saude SA", "Allianz Saude", "seguradora_especializada_em_saude", "00.761.884/0001-47", "Sao Paulo", "SP"),
    ("410940", "Plena Saude Assistencia Medica Ltda", "Plena Saude", "medicina_de_grupo", "19.471.009/0001-65", "Sao Paulo", "SP"),
    ("362438", "Notredame Companhia de Seguros", "Notredame Seguros", "seguradora_especializada_em_saude", "02.390.110/0001-84", "Sao Paulo", "SP"),
    ("003743", "Unimed Campinas Cooperativa de Trabalho Medico", "Unimed Campinas", "cooperativa_medica", "45.999.704/0001-07", "Campinas", "SP"),
    ("321613", "Saude Caixa", "Saude Caixa", "autogestao", "00.360.305/0001-04", "Brasilia", "DF"),
    ("344079", "Cassi Caixa de Assistencia dos Funcionarios", "CASSI", "autogestao", "33.453.437/0001-26", "Brasilia", "DF"),
    ("348449", "Petrobras Distribuidora Plano de Assistencia Medica", "PDPLAN", "autogestao", "34.274.233/0001-02", "Rio de Janeiro", "RJ"),
    # Medicina de grupo
    ("314641", "Saude Mais Assistencia Medica Ltda", "Saude Mais", "medicina_de_grupo", "11.222.333/0001-44", "Salvador", "BA"),
    ("315678", "Vitta Saude Ltda", "Vitta", "medicina_de_grupo", "22.333.444/0001-55", "Curitiba", "PR"),
    ("316789", "MedFacil Assistencia Medica Ltda", "MedFacil", "medicina_de_grupo", "33.444.555/0001-66", "Porto Alegre", "RS"),
    ("317890", "Saude Total Operadora Ltda", "Saude Total", "medicina_de_grupo", "44.555.666/0001-77", "Recife", "PE"),
    ("318901", "Planassis Plano de Assistencia a Saude Ltda", "Planassis", "medicina_de_grupo", "55.666.777/0001-88", "Goiania", "GO"),
    ("319012", "Careplus Medicina de Grupo Ltda", "CarePlus", "medicina_de_grupo", "66.777.888/0001-99", "Sao Paulo", "SP"),
    ("320123", "Medprev Assistencia Medica Ltda", "MedPrev", "medicina_de_grupo", "77.888.999/0001-10", "Belo Horizonte", "MG"),
    ("321234", "HealthCare Operadora de Saude Ltda", "HealthCare", "medicina_de_grupo", "88.999.000/0001-21", "Fortaleza", "CE"),
    ("322345", "VidaSaude Assistencia Medica Ltda", "VidaSaude", "medicina_de_grupo", "11.000.111/0001-32", "Manaus", "AM"),
    ("323456", "Mais Saude Operadora Ltda", "Mais Saude", "medicina_de_grupo", "22.111.222/0001-43", "Florianopolis", "SC"),
    ("324567", "MedBrasil Assistencia Medica Ltda", "MedBrasil", "medicina_de_grupo", "33.222.333/0001-54", "Maceio", "AL"),
    ("325678", "Salus Assistencia Medica Ltda", "Salus", "medicina_de_grupo", "44.333.444/0001-65", "Natal", "RN"),
    ("327890", "Integras Operadora de Saude Ltda", "Integras", "medicina_de_grupo", "55.444.555/0001-76", "Joao Pessoa", "PB"),
    ("328901", "Sempre Saude Assistencia Medica Ltda", "Sempre Saude", "medicina_de_grupo", "66.555.666/0001-87", "Teresina", "PI"),
    ("329012", "MedNorte Assistencia Medica Ltda", "MedNorte", "medicina_de_grupo", "77.666.777/0001-98", "Belem", "PA"),
    # Cooperativa médica
    ("330123", "Unimed Curitiba Sociedade Cooperativa de Medicos", "Unimed Curitiba", "cooperativa_medica", "76.577.196/0001-79", "Curitiba", "PR"),
    ("331234", "Unimed Porto Alegre Cooperativa Medica", "Unimed POA", "cooperativa_medica", "88.122.000/0001-62", "Porto Alegre", "RS"),
    ("332345", "Unimed Recife Cooperativa de Trabalho Medico", "Unimed Recife", "cooperativa_medica", "08.738.079/0001-11", "Recife", "PE"),
    ("333456", "Unimed Fortaleza Cooperativa de Trabalho Medico", "Unimed Fortaleza", "cooperativa_medica", "07.141.401/0001-88", "Fortaleza", "CE"),
    ("334567", "Unimed Salvador Cooperativa de Trabalho Medico", "Unimed Salvador", "cooperativa_medica", "13.555.200/0001-99", "Salvador", "BA"),
    ("335678", "Unimed Goiania Cooperativa de Trabalho Medico", "Unimed Goiania", "cooperativa_medica", "01.432.980/0001-65", "Goiania", "GO"),
    ("336789", "Unimed Minas Federacao das Cooperativas Medicas", "Unimed Minas", "cooperativa_medica", "45.523.898/0001-05", "Belo Horizonte", "MG"),
    ("337890", "Uniodonto Cooperativa de Trabalho Odontologico", "Uniodonto", "cooperativa_odontologica", "00.459.321/0001-34", "Sao Paulo", "SP"),
    ("338901", "Unimed Ribeirao Preto Cooperativa de Trabalho Medico", "Unimed RP", "cooperativa_medica", "47.692.012/0001-00", "Ribeirao Preto", "SP"),
    ("339012", "Unimed Uberlandia Cooperativa de Trabalho Medico", "Unimed Uberlandia", "cooperativa_medica", "25.476.143/0001-45", "Uberlandia", "MG"),
    # Seguradora
    ("340123", "Caixa de Assistencia dos Advogados CAARJ", "CAARJ Saude", "autogestao", "33.452.116/0001-25", "Rio de Janeiro", "RJ"),
    ("341234", "Economus Instituto de Seguridade Social", "Economus", "autogestao", "48.038.538/0001-25", "Sao Paulo", "SP"),
    ("342345", "Funcef Fundacao dos Economiarios Federais", "FUNCEF Saude", "autogestao", "07.784.981/0001-56", "Brasilia", "DF"),
    ("343456", "Ticket Solucoes Ltda Plano de Saude", "Ticket Saude", "administradora_de_beneficios", "02.913.459/0001-00", "Sao Paulo", "SP"),
    ("344456", "MetLife Saude SA", "MetLife Saude", "seguradora_especializada_em_saude", "10.438.795/0001-08", "Sao Paulo", "SP"),
    ("345567", "Tokio Marine Saude SA", "Tokio Marine", "seguradora_especializada_em_saude", "33.041.252/0001-44", "Sao Paulo", "SP"),
    # Filantrópica
    ("346678", "Santa Casa de Misericordia de Sao Paulo Plano de Saude", "Santa Casa SP", "filantropica", "60.003.761/0001-61", "Sao Paulo", "SP"),
    ("347789", "Hospital das Clinicas da FMUSP Plano de Saude", "HC FMUSP", "filantropica", "69.682.204/0001-23", "Sao Paulo", "SP"),
    ("348890", "Beneficencia Portuguesa de Sao Paulo Plano de Saude", "BP Saude", "filantropica", "61.098.611/0001-73", "Sao Paulo", "SP"),
    ("349901", "Santa Casa de Belo Horizonte Plano de Saude", "Santa Casa BH", "filantropica", "19.234.567/0001-89", "Belo Horizonte", "MG"),
    ("350012", "Hospital Sao Lucas PUCRS Plano de Saude", "HSL PUCRS", "filantropica", "92.985.643/0001-78", "Porto Alegre", "RS"),
    ("351123", "APAE SP Plano de Saude", "APAE Saude", "filantropica", "60.930.791/0001-38", "Sao Paulo", "SP"),
    ("352234", "Irmandade da Santa Casa de Curitiba", "Santa Casa Curitiba", "filantropica", "76.590.001/0001-02", "Curitiba", "PR"),
    ("353345", "Hospital Sirio-Libanes Plano de Saude", "Sirio-Libanes", "filantropica", "60.194.990/0001-37", "Sao Paulo", "SP"),
    # Odontologia
    ("354456", "Dental Uni Cooperativa Odontologica", "Dental Uni", "cooperativa_odontologica", "07.219.345/0001-18", "Campinas", "SP"),
    ("355567", "Sorridents Odontologia de Grupo Ltda", "Sorridents", "odontologia_de_grupo", "08.134.987/0001-22", "Sao Paulo", "SP"),
    ("357789", "Odonto Empresas Cooperativa de Odontologia", "Odonto Empresas", "cooperativa_odontologica", "05.432.100/0001-44", "Curitiba", "PR"),
    ("358890", "UsiSaude Odontologia Ltda", "UsiSaude Odonto", "odontologia_de_grupo", "09.876.543/0001-66", "Belo Horizonte", "MG"),
    ("360012", "Odontogroup Assistencia Odontologica Ltda", "OdontoGroup", "odontologia_de_grupo", "12.234.567/0001-88", "Sao Paulo", "SP"),
    ("361123", "Dental Med Operadora Odontologica Ltda", "Dental Med", "odontologia_de_grupo", "23.345.678/0001-99", "Porto Alegre", "RS"),
    # Medicina de grupo (mais)
    ("362234", "LifeCenter Assistencia Medica Ltda", "LifeCenter", "medicina_de_grupo", "34.456.789/0001-10", "Sao Paulo", "SP"),
    ("363345", "AmorSaude Assistencia Medica Ltda", "AmorSaude", "medicina_de_grupo", "45.567.890/0001-21", "Rio de Janeiro", "RJ"),
    ("364456", "CuidarBem Operadora de Saude Ltda", "CuidarBem", "medicina_de_grupo", "56.678.901/0001-32", "Campinas", "SP"),
    ("365567", "MediPrime Assistencia Medica Ltda", "MediPrime", "medicina_de_grupo", "67.789.012/0001-43", "Curitiba", "PR"),
    ("366678", "PlanSaude Operadora Ltda", "PlanSaude", "medicina_de_grupo", "78.890.123/0001-54", "Salvador", "BA"),
    ("367789", "ClinicMed Assistencia Medica Ltda", "ClinicMed", "medicina_de_grupo", "89.901.234/0001-65", "Recife", "PE"),
    ("369901", "NordSaude Assistencia Medica Ltda", "NordSaude", "medicina_de_grupo", "90.012.345/0001-76", "Fortaleza", "CE"),
    ("370012", "AmazonSaude Operadora Ltda", "AmazonSaude", "medicina_de_grupo", "01.123.456/0001-87", "Manaus", "AM"),
    ("371123", "CentroMed Assistencia Medica Ltda", "CentroMed", "medicina_de_grupo", "12.234.568/0001-98", "Goiania", "GO"),
    ("372234", "BrasilSaude Operadora de Saude SA", "BrasilSaude", "medicina_de_grupo", "23.345.679/0001-09", "Brasilia", "DF"),
    ("373345", "FamiliaMed Assistencia Medica Ltda", "FamiliaMed", "medicina_de_grupo", "34.456.780/0001-20", "Florianopolis", "SC"),
    ("374456", "SaberSaude Operadora Ltda", "SaberSaude", "medicina_de_grupo", "45.567.891/0001-31", "Porto Velho", "RO"),
    ("375567", "TotalMed Assistencia Medica Ltda", "TotalMed", "medicina_de_grupo", "56.678.902/0001-42", "Macapa", "AP"),
    ("376678", "NovaMed Operadora de Saude Ltda", "NovaMed", "medicina_de_grupo", "67.789.013/0001-53", "Boa Vista", "RR"),
    # Cooperativa (mais)
    ("377789", "Unimed Marilia Cooperativa de Trabalho Medico", "Unimed Marilia", "cooperativa_medica", "44.783.217/0001-61", "Marilia", "SP"),
    ("378890", "Unimed Sorocaba Cooperativa de Trabalho Medico", "Unimed Sorocaba", "cooperativa_medica", "52.143.007/0001-83", "Sorocaba", "SP"),
    ("379901", "Unimed Londrina Cooperativa de Trabalho Medico", "Unimed Londrina", "cooperativa_medica", "75.456.234/0001-90", "Londrina", "PR"),
    ("380012", "Unimed Joao Pessoa Cooperativa de Trabalho Medico", "Unimed JP", "cooperativa_medica", "08.132.411/0001-55", "Joao Pessoa", "PB"),
    ("381123", "Unimed Natal Cooperativa de Trabalho Medico", "Unimed Natal", "cooperativa_medica", "03.560.218/0001-61", "Natal", "RN"),
    # Autogestão
    ("382234", "Petrobras Plano de Assistencia Medica", "PAMA Petrobras", "autogestao", "33.000.167/0001-01", "Rio de Janeiro", "RJ"),
    ("383345", "BB Saude Fundacao Banco do Brasil", "BB Saude", "autogestao", "00.406.803/0001-97", "Brasilia", "DF"),
    ("384456", "Itau Unibanco Plano de Saude", "Itau Saude", "autogestao", "60.872.504/0001-23", "Sao Paulo", "SP"),
    ("385567", "EMBRATEL Plano de Saude", "EMBRATEL Saude", "autogestao", "33.530.486/0001-29", "Rio de Janeiro", "RJ"),
    ("386678", "ELETROBRAS Plano de Saude", "ELETROBRAS Saude", "autogestao", "00.073.991/0001-68", "Rio de Janeiro", "RJ"),
    # Medicina de grupo - regionais
    ("387789", "MedGaucho Assistencia Medica Ltda", "MedGaucho", "medicina_de_grupo", "88.901.234/0001-77", "Porto Alegre", "RS"),
    ("388890", "MedSul Operadora Ltda", "MedSul", "medicina_de_grupo", "99.012.345/0001-88", "Florianopolis", "SC"),
    ("389901", "SaudeMinas Operadora de Saude Ltda", "SaudeMinas", "medicina_de_grupo", "10.123.456/0001-99", "Belo Horizonte", "MG"),
    ("390012", "PaulisMed Assistencia Medica Ltda", "PaulisMed", "medicina_de_grupo", "21.234.567/0001-00", "Sao Paulo", "SP"),
    ("391123", "CariocaMed Assistencia Medica Ltda", "CariocaMed", "medicina_de_grupo", "32.345.678/0001-11", "Rio de Janeiro", "RJ"),
    ("392234", "SaludeBahia Operadora Ltda", "SaludeBahia", "medicina_de_grupo", "43.456.789/0001-22", "Salvador", "BA"),
    ("393345", "MedCearense Assistencia Medica Ltda", "MedCearense", "medicina_de_grupo", "54.567.890/0001-33", "Fortaleza", "CE"),
    ("394456", "PernaMed Assistencia Medica Ltda", "PernaMed", "medicina_de_grupo", "65.678.901/0001-44", "Recife", "PE"),
    ("395567", "CapitalSaude Operadora Ltda", "CapitalSaude", "medicina_de_grupo", "76.789.012/0001-55", "Brasilia", "DF"),
    ("396678", "GrupoMed Assistencia Medica Ltda", "GrupoMed", "medicina_de_grupo", "87.890.123/0001-66", "Sao Paulo", "SP"),
    ("397789", "NacionalSaude Operadora SA", "NacionalSaude", "medicina_de_grupo", "98.901.234/0001-77", "Rio de Janeiro", "RJ"),
    ("398890", "FederalMed Assistencia Medica Ltda", "FederalMed", "medicina_de_grupo", "01.012.345/0001-88", "Brasilia", "DF"),
    ("399901", "SaúdeNet Operadora Digital Ltda", "SaudeNet", "medicina_de_grupo", "12.123.456/0001-99", "Sao Paulo", "SP"),
    ("400012", "PlusSaude Assistencia Medica Ltda", "PlusSaude", "medicina_de_grupo", "23.234.567/0001-00", "Campinas", "SP"),
]

# ── Municípios amostrados ─────────────────────────────────────────────────────

MUNICIPIOS = [
    ("3550308", "Sao Paulo", "SP"),
    ("3304557", "Rio de Janeiro", "RJ"),
    ("3106200", "Belo Horizonte", "MG"),
    ("4314902", "Porto Alegre", "RS"),
    ("4106902", "Curitiba", "PR"),
    ("2927408", "Salvador", "BA"),
    ("2304400", "Fortaleza", "CE"),
    ("2611606", "Recife", "PE"),
    ("5208707", "Goiania", "GO"),
    ("4209102", "Florianopolis", "SC"),
    ("1302603", "Manaus", "AM"),
    ("1501402", "Belem", "PA"),
    ("5300108", "Brasilia", "DF"),
    ("3509502", "Campinas", "SP"),
    ("3170206", "Uberlandia", "MG"),
    ("3543402", "Ribeirao Preto", "SP"),
    ("2408102", "Natal", "RN"),
    ("2800308", "Aracaju", "SE"),
    ("3205309", "Vitoria", "ES"),
    ("5002704", "Campo Grande", "MS"),
    ("5103403", "Cuiaba", "MT"),
    ("3518800", "Guarulhos", "SP"),
    ("3526902", "Maua", "SP"),
    ("3548708", "Santo Andre", "SP"),
    ("3552205", "Santos", "SP"),
    ("4113700", "Londrina", "PR"),
    ("4115200", "Maringa", "PR"),
    ("4316907", "Santa Maria", "RS"),
    ("4309209", "Caxias do Sul", "RS"),
    ("2910800", "Feira de Santana", "BA"),
]

SEGMENTOS = ["medico_hospitalar", "medico_hospitalar", "medico_hospitalar", "odontologico"]
TIPOS_PRESTADOR = ["hospital", "clinica", "laboratorio", "consultorio", "consultorio"]
TIPOS_GLOSA = ["nao_encontrado", "divergencia_codigo", "procedimento_nao_coberto", "prazo_expirado", "outros"]
TIPOS_REGIME = ["direcao_fiscal", "direcao_tecnica", "liquidacao_extrajudicial"]
SITUACOES_PRUDENCIAL = ["adequada", "adequada", "adequada", "atencao", "critica"]
SITUACOES_VDA = ["regular", "regular", "em_atraso", "em_parcelamento", "quitado"]
TIPOS_CONTRATACAO = ["coletivo_empresarial", "coletivo_empresarial", "coletivo_por_adesao", "individual_ou_familiar"]
FAIXAS_IDSS = ["A", "A", "B", "B", "B", "C", "C", "D", "E"]


def r_float(lo: float, hi: float, ndigits: int = 4) -> float:
    return round(RNG.uniform(lo, hi), ndigits)


def r_int(lo: int, hi: int) -> int:
    return RNG.randint(lo, hi)


def _layout(dataset: str) -> dict:
    return {
        "layout_id": f"layout_{dataset}_vol_v1",
        "layout_versao_id": f"layout_{dataset}_vol_v1_001",
        "hash_arquivo": f"hash_vol_{dataset}_{RNG.randint(100000, 999999)}",
        "hash_estrutura": f"struct_{dataset}_v1",
    }


# ── Seeders ───────────────────────────────────────────────────────────────────

async def seed_cadop() -> None:
    registros = []
    for reg_ans, razao, fantasia, modal, cnpj, cidade, uf in OPERADORAS:
        registros.append({
            "registro_ans": reg_ans,
            "cnpj": cnpj,
            "razao_social": razao,
            "nome_fantasia": fantasia,
            "modalidade": modal,
            "cidade": cidade,
            "uf": uf,
            "competencia": "202603",
        })
    meta = _layout("cadop")
    await carregar_cadop_bruto(
        registros,
        arquivo_origem="cadop_completo_202603.csv",
        **meta,
    )
    print(f"  cadop: {len(registros)} operadoras")


async def seed_sib_operadora() -> None:
    total = 0
    for mes in MESES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            is_odonto = "odonto" in modal
            base = r_int(500, 500_000)
            registros.append({
                "competencia": mes,
                "registro_ans": reg_ans,
                "beneficiario_medico": 0 if is_odonto else base,
                "beneficiario_odonto": base if is_odonto else r_int(0, base // 3),
                "beneficiario_total": base,
            })
        meta = _layout("sib_operadora")
        await carregar_sib_operadora_bruto(
            registros,
            arquivo_origem=f"sib_operadora_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  sib_operadora: {total} registros")


async def seed_sib_municipio() -> None:
    total = 0
    municipios_sample = MUNICIPIOS[:10]
    for mes in MESES_RECENTES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            is_odonto = "odonto" in modal
            for cd_mun, nm_mun, uf in municipios_sample:
                base = r_int(10, 5_000)
                registros.append({
                    "competencia": mes,
                    "registro_ans": reg_ans,
                    "codigo_ibge": cd_mun,
                    "municipio": nm_mun,
                    "uf": uf,
                    "beneficiario_medico": 0 if is_odonto else base,
                    "beneficiario_odonto": base if is_odonto else r_int(0, base // 5),
                    "beneficiario_total": base,
                })
        meta = _layout("sib_municipio")
        await carregar_sib_municipio_bruto(
            registros,
            arquivo_origem=f"sib_municipio_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  sib_municipio: {total} registros")


async def seed_igr() -> None:
    total = 0
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            igr_val = r_float(0.1, 5.0, 3)
            meta_igr = r_float(0.5, 3.0, 3)
            beneficiarios = r_int(1_000, 800_000)
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "modalidade": modal,
                "porte": RNG.choice(["grande", "medio", "pequeno"]),
                "total_reclamacoes": r_int(10, int(beneficiarios * igr_val / 1000) + 50),
                "beneficiarios": beneficiarios,
                "igr": igr_val,
                "meta_igr": meta_igr,
                "atingiu_meta": igr_val <= meta_igr,
                "fonte_publicacao": "ANS/painel_igr",
            })
        meta = _layout("igr")
        await carregar_igr_bruto(
            registros,
            arquivo_origem=f"igr_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  igr: {total} registros")


async def seed_nip() -> None:
    total = 0
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            beneficiarios = r_int(1_000, 800_000)
            demandas = r_int(5, 2_000)
            resolvidas = r_int(1, demandas)
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "modalidade": modal,
                "demandas_nip": demandas,
                "demandas_resolvidas": resolvidas,
                "beneficiarios": beneficiarios,
                "taxa_intermediacao_resolvida": round(resolvidas / demandas, 4),
                "taxa_resolutividade": r_float(0.3, 1.0, 4),
                "fonte_publicacao": "ANS/painel_nip",
            })
        meta = _layout("nip")
        await carregar_nip_bruto(
            registros,
            arquivo_origem=f"nip_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  nip: {total} registros")


async def seed_rn623() -> None:
    total = 0
    elegíveis = [op[0] for op in RNG.sample(OPERADORAS, 40)]
    for tri in TRIMESTRES[-4:]:
        registros = []
        for reg_ans in elegíveis:
            op = next(o for o in OPERADORAS if o[0] == reg_ans)
            modal = op[3]
            igr_val = r_float(0.1, 2.0, 3)
            tipo_lista = RNG.choice(["excelencia", "reducao"])
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "modalidade": modal,
                "tipo_lista": tipo_lista,
                "total_nip": r_int(1, 500),
                "beneficiarios": r_int(5_000, 800_000),
                "igr": igr_val,
                "meta_igr": r_float(0.5, 2.5, 3),
                "elegivel": True,
                "observacao": f"Lista {tipo_lista} - {tri}",
                "fonte_publicacao": "ANS/rn623",
            })
        meta = _layout("rn623")
        await carregar_rn623_lista_bruto(
            registros,
            arquivo_origem=f"rn623_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  rn623: {total} registros")


async def seed_idss() -> None:
    total = 0
    for ano in ANOS_IDSS:
        registros = []
        for reg_ans, _, _, _, _, _, _ in OPERADORAS:
            idqs = r_float(0.0, 1.0, 4)
            idga = r_float(0.0, 1.0, 4)
            idsm = r_float(0.0, 1.0, 4)
            idgr = r_float(0.0, 1.0, 4)
            total_score = round((idqs + idga + idsm + idgr) / 4, 4)
            faixa = "A" if total_score >= 0.75 else "B" if total_score >= 0.6 else "C" if total_score >= 0.45 else "D" if total_score >= 0.3 else "E"
            registros.append({
                "ano_base": ano,
                "registro_ans": reg_ans,
                "idss_total": total_score,
                "idqs": idqs,
                "idga": idga,
                "idsm": idsm,
                "idgr": idgr,
                "faixa_idss": faixa,
                "fonte_publicacao": f"ANS/idss_{ano}",
            })
        meta = _layout("idss")
        await carregar_idss_bruto(
            registros,
            arquivo_origem=f"idss_{ano}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  idss: {total} registros")


def _cnpj_digits(cnpj: str) -> str:
    return "".join(c for c in cnpj if c.isdigit())


async def seed_diops() -> None:
    total = 0
    ops_financeiras = [op for op in OPERADORAS if "odonto" not in op[3] and "administradora" not in op[3]]
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, modal, cnpj, _, _ in ops_financeiras:
            ativo = r_float(10_000_000, 5_000_000_000, 2)
            passivo = round(ativo * r_float(0.4, 0.8, 4), 2)
            pl = round(ativo - passivo, 2)
            receita = r_float(5_000_000, 3_000_000_000, 2)
            despesa = round(receita * r_float(0.7, 1.05, 4), 2)
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "cnpj": _cnpj_digits(cnpj),
                "ativo_total": ativo,
                "passivo_total": passivo,
                "patrimonio_liquido": pl,
                "receita_total": receita,
                "despesa_total": despesa,
                "resultado_periodo": round(receita - despesa, 2),
                "provisao_tecnica": r_float(1_000_000, 500_000_000, 2),
                "margem_solvencia_calculada": r_float(0.08, 0.35, 4),
                "fonte_publicacao": "ANS/diops",
            })
        meta = _layout("diops")
        await carregar_diops_bruto(
            registros,
            arquivo_origem=f"diops_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  diops: {total} registros")


async def seed_fip() -> None:
    total = 0
    ops_financeiras = [op for op in OPERADORAS if "odonto" not in op[3] and "administradora" not in op[3]]
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in ops_financeiras:
            for tipo in ["coletivo_empresarial", "coletivo_por_adesao"]:
                contraprestacao = r_float(1_000_000, 2_000_000_000, 2)
                sinistro = round(contraprestacao * r_float(0.55, 0.95, 4), 2)
                registros.append({
                    "trimestre": tri,
                    "registro_ans": reg_ans,
                    "modalidade": modal,
                    "tipo_contratacao": tipo,
                    "sinistro_total": sinistro,
                    "contraprestacao_total": contraprestacao,
                    "sinistralidade_bruta": round(sinistro / contraprestacao, 4),
                    "ressarcimento_sus": r_float(0, contraprestacao * 0.05, 2),
                    "evento_indenizavel": sinistro,
                    "fonte_publicacao": "ANS/fip",
                })
        meta = _layout("fip")
        await carregar_fip_bruto(
            registros,
            arquivo_origem=f"fip_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  fip: {total} registros")


async def seed_vda() -> None:
    ops_vda = [op[0] for op in RNG.sample(OPERADORAS, 25)]
    total = 0
    for mes in MESES_RECENTES:
        registros = []
        for reg_ans in ops_vda:
            valor_devido = r_float(10_000, 5_000_000, 2)
            valor_pago = round(valor_devido * r_float(0.0, 1.1, 4), 2)
            registros.append({
                "competencia": mes,
                "registro_ans": reg_ans,
                "valor_devido": valor_devido,
                "valor_pago": min(valor_pago, valor_devido),
                "saldo_devedor": max(0.0, round(valor_devido - valor_pago, 2)),
                "situacao_cobranca": RNG.choice(SITUACOES_VDA),
                "data_vencimento": date(int(mes[:4]), int(mes[4:]), 15),
                "fonte_publicacao": "ANS/vda",
            })
        meta = _layout("vda")
        await carregar_vda_bruto(
            registros,
            arquivo_origem=f"vda_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  vda: {total} registros")


async def seed_glosa() -> None:
    total = 0
    for mes in MESES_RECENTES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            if "odonto" in modal:
                continue
            for tipo in RNG.sample(TIPOS_GLOSA, 3):
                qt = r_int(1, 500)
                valor_fat = r_float(qt * 100, qt * 5_000, 2)
                registros.append({
                    "competencia": mes,
                    "registro_ans": reg_ans,
                    "tipo_glosa": tipo,
                    "qt_glosa": qt,
                    "valor_glosa": round(valor_fat * r_float(0.05, 0.30, 4), 2),
                    "valor_faturado": valor_fat,
                    "fonte_publicacao": "ANS/glosa",
                })
        meta = _layout("glosa")
        await carregar_glosa_bruto(
            registros,
            arquivo_origem=f"glosa_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  glosa: {total} registros")


async def seed_portabilidade() -> None:
    total = 0
    for mes in MESES_RECENTES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            for tipo in ["coletivo_empresarial", "individual_ou_familiar"]:
                registros.append({
                    "competencia": mes,
                    "registro_ans": reg_ans,
                    "modalidade": modal,
                    "tipo_contratacao": tipo,
                    "qt_portabilidade_entrada": r_int(0, 500),
                    "qt_portabilidade_saida": r_int(0, 500),
                    "fonte_publicacao": "ANS/portabilidade",
                })
        meta = _layout("portabilidade")
        await carregar_portabilidade_bruto(
            registros,
            arquivo_origem=f"portabilidade_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  portabilidade: {total} registros")


async def seed_regime_especial() -> None:
    ops_re = [op[0] for op in RNG.sample(OPERADORAS, 8)]
    registros = []
    for reg_ans in ops_re:
        tipo = RNG.choice(TIPOS_REGIME)
        ano_inicio = RNG.randint(2023, 2025)
        mes_inicio = RNG.randint(1, 12)
        data_inicio = date(ano_inicio, mes_inicio, 1)
        data_fim = date(ano_inicio + 1, mes_inicio, 1) if tipo != "liquidacao_extrajudicial" else None
        registros.append({
            "trimestre": f"{ano_inicio}T{(mes_inicio - 1) // 3 + 1}",
            "registro_ans": reg_ans,
            "tipo_regime": tipo,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "descricao": f"Regime especial tipo {tipo} instaurado em {data_inicio}",
            "fonte_publicacao": "ANS/regime_especial",
        })
    meta = _layout("regime_especial")
    await carregar_regime_especial_bruto(
        registros,
        arquivo_origem="regime_especial_historico.csv",
        **meta,
    )
    print(f"  regime_especial: {len(registros)} registros")


async def seed_prudencial() -> None:
    total = 0
    ops_prud = [op for op in OPERADORAS if "odonto" not in op[3] and "administradora" not in op[3]]
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, _, _, _, _ in ops_prud:
            capital_req = r_float(1_000_000, 100_000_000, 2)
            capital_disp = round(capital_req * r_float(0.8, 2.5, 4), 2)
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "margem_solvencia": round(capital_disp / capital_req, 4),
                "capital_minimo_requerido": capital_req,
                "capital_disponivel": capital_disp,
                "indice_liquidez": r_float(0.5, 3.0, 4),
                "situacao_prudencial": RNG.choice(SITUACOES_PRUDENCIAL),
                "fonte_publicacao": "ANS/prudencial",
            })
        meta = _layout("prudencial")
        await carregar_prudencial_bruto(
            registros,
            arquivo_origem=f"prudencial_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  prudencial: {total} registros")


async def seed_taxa_resolutividade() -> None:
    total = 0
    for tri in TRIMESTRES:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in OPERADORAS:
            n_total = r_int(10, 2_000)
            n_res = r_int(1, n_total)
            registros.append({
                "trimestre": tri,
                "registro_ans": reg_ans,
                "modalidade": modal,
                "taxa_resolutividade": round(n_res / n_total, 4),
                "n_reclamacao_resolvida": n_res,
                "n_reclamacao_total": n_total,
                "fonte_publicacao": "ANS/taxa_resolutividade",
            })
        meta = _layout("taxa_resolutividade")
        await carregar_taxa_resolutividade_bruto(
            registros,
            arquivo_origem=f"taxa_resolutividade_{tri.replace('T', 't')}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  taxa_resolutividade: {total} registros")


async def seed_rede_assistencial() -> None:
    total = 0
    ops_rede = OPERADORAS[:60]
    municipios_rede = MUNICIPIOS[:15]
    for mes in MESES_3:
        registros = []
        for reg_ans, _, _, modal, _, _, _ in ops_rede:
            for cd_mun, nm_mun, uf in municipios_rede:
                for seg in ["medico_hospitalar", "odontologico"] if "odonto" in modal else ["medico_hospitalar"]:
                    for tipo in RNG.sample(TIPOS_PRESTADOR, 3):
                        registros.append({
                            "competencia": mes,
                            "registro_ans": reg_ans,
                            "cd_municipio": cd_mun,
                            "nm_municipio": nm_mun,
                            "sg_uf": uf,
                            "segmento": seg,
                            "tipo_prestador": tipo,
                            "qt_prestador": r_int(1, 200),
                            "qt_especialidade_disponivel": r_int(1, 50),
                            "fonte_publicacao": "ANS/rede_assistencial",
                        })
        meta = _layout("rede_assistencial")
        await carregar_rede_assistencial_bruto(
            registros,
            arquivo_origem=f"rede_assistencial_{mes}.csv",
            **meta,
        )
        total += len(registros)
    print(f"  rede_assistencial: {total} registros")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    print("Iniciando seed completo...")
    await seed_cadop()
    await seed_sib_operadora()
    await seed_sib_municipio()
    await seed_igr()
    await seed_nip()
    await seed_rn623()
    await seed_idss()
    await seed_diops()
    await seed_fip()
    await seed_vda()
    await seed_glosa()
    await seed_portabilidade()
    await seed_regime_especial()
    await seed_prudencial()
    await seed_taxa_resolutividade()
    await seed_rede_assistencial()
    print("Seed completo finalizado.")


if __name__ == "__main__":
    asyncio.run(main())
