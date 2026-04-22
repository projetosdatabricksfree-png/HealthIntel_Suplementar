from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContratoFonteRegulatoria:
    dataset_codigo: str
    nome: str
    descricao: str
    tabela_raw_destino: str
    cadencia: str
    formato_publicacao: str
    url_publicacao: str
    atualizado_em_oficial: str
    observacao: str


CONTRATOS_FONTES_REGULATORIAS: dict[str, ContratoFonteRegulatoria] = {
    "igr": ContratoFonteRegulatoria(
        dataset_codigo="igr",
        nome="Indice Geral de Reclamacoes",
        descricao=(
            "Painel oficial da ANS com o historico do IGR por operadora e periodo, "
            "com base em beneficiarios e reclamacoes desde 2020."
        ),
        tabela_raw_destino="bruto_ans.igr_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="painel_powerbi",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/"
            "indice-de-reclamacoes-2"
        ),
        atualizado_em_oficial="2025-09-24",
        observacao=(
            "O painel oficial referencia o IGR como termometro do comportamento das "
            "operadoras no atendimento aos problemas apontados pelos beneficiarios."
        ),
    ),
    "nip": ContratoFonteRegulatoria(
        dataset_codigo="nip",
        nome="Demandas NIP e Taxas de Intermediacao",
        descricao=(
            "Painel oficial da ANS com demandas NIP por operadora e indicador de "
            "intermediacao/resolutividade publicado a partir de 2025."
        ),
        tabela_raw_destino="bruto_ans.nip_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="painel_powerbi",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/"
            "indice-de-reclamacoes-2"
        ),
        atualizado_em_oficial="2025-09-24",
        observacao=(
            "A ANS passou a divulgar o painel TIR em 05/03/2025, mantendo a rastreabilidade "
            "das demandas processadas via NIP."
        ),
    ),
    "rn623_lista": ContratoFonteRegulatoria(
        dataset_codigo="rn623_lista",
        nome="Listas RN 623/2024",
        descricao=(
            "Listas trimestrais de Excelencia e de Reducao das reclamacoes das operadoras, "
            "divulgadas no portal oficial da ANS."
        ),
        tabela_raw_destino="bruto_ans.rn623_lista_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="html_pdf_painel",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/"
            "lista-excelencia-e-reducao-das-reclamacoes-das-operadoras"
        ),
        atualizado_em_oficial="2026-03-13",
        observacao=(
            "A pagina oficial informa vigencia da RN 623 desde 01/07/2025, divulgacao da "
            "lista de Excelencia desde dezembro de 2025 e da lista de Reducao desde marco de 2026."
        ),
    ),
}
