from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContratoFonteFinanceira:
    dataset_codigo: str
    nome: str
    descricao: str
    tabela_raw_destino: str
    cadencia: str
    formato_publicacao: str
    url_publicacao: str
    atualizado_em_oficial: str
    observacao: str


CONTRATOS_FONTES_FINANCEIRAS: dict[str, ContratoFonteFinanceira] = {
    "diops": ContratoFonteFinanceira(
        dataset_codigo="diops",
        nome="DIOPS Financeiro",
        descricao=(
            "Documento de Informacoes Periodicas das Operadoras com recorte financeiro, "
            "normalizado em serie trimestral para análise econômico-financeira."
        ),
        tabela_raw_destino="bruto_ans.diops_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="DIOPS-XML",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/operadoras/aplicativos-ans-2/"
            "aplicativos-diops/diops-financeiro"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "A ANS informa o envio trimestral das informacoes financeiras e disponibiliza "
            "versoes historicas do cliente DIOPS-XML."
        ),
    ),
    "fip": ContratoFonteFinanceira(
        dataset_codigo="fip",
        nome="FIP historico financeiro",
        descricao=(
            "Serie financeira historica derivada do legado FIP e harmonizada com o "
            "DIOPS para apoiar analise de sinistralidade e resultado."
        ),
        tabela_raw_destino="bruto_ans.fip_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="legado_historico",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/operadoras/aplicativos-ans-2/"
            "aplicativos-diops/diops-financeiro"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "O contrato trata FIP como recorte historico e de compatibilidade financeira, "
            "preservando a modelagem separada no bronze e a harmonizacao posterior no dbt."
        ),
    ),
    "vda": ContratoFonteFinanceira(
        dataset_codigo="vda",
        nome="VDA mensal",
        descricao=(
            "Valor Devido à ANS mensal por operadora, usado para medir adimplencia e "
            "sinalizar risco de cobrança."
        ),
        tabela_raw_destino="bruto_ans.vda_operadora_mensal",
        cadencia="mensal",
        formato_publicacao="csv",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/arquivos/assuntos/consumidor/"
            "reajustes-de-mensalidade/reajuste-anual-de-planos-individuais-familiares/"
            "metodologia-de-calculo/2023/Nota_da_VDA.pdf"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "A VDA entra na camada financeira v2 como fonte mensal para penalizacao de "
            "inadimplencia, preservando o histórico por competencia."
        ),
    ),
    "glosa": ContratoFonteFinanceira(
        dataset_codigo="glosa",
        nome="Glosa mensal",
        descricao=(
            "Glosa mensal por operadora e tipo de glosa, consolidada para apoiar o "
            "score financeiro v2."
        ),
        tabela_raw_destino="bruto_ans.glosa_operadora_mensal",
        cadencia="mensal",
        formato_publicacao="painel_ans",
        url_publicacao="https://www.gov.br/ans/pt-br",
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "O contrato assume publicacao oficial/portal institucional como origem e "
            "mantem granularidade por tipo de glosa para auditoria e score v2."
        ),
    ),
}
