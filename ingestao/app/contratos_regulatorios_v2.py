from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContratoFonteRegulatoriaV2:
    dataset_codigo: str
    nome: str
    descricao: str
    tabela_raw_destino: str
    cadencia: str
    formato_publicacao: str
    url_publicacao: str
    atualizado_em_oficial: str
    observacao: str


CONTRATOS_FONTES_REGULATORIAS_V2: dict[str, ContratoFonteRegulatoriaV2] = {
    "regime_especial": ContratoFonteRegulatoriaV2(
        dataset_codigo="regime_especial",
        nome="Regime Especial de Direcao Fiscal e Tecnica",
        descricao=(
            "Publicacoes e certidoes da ANS sobre operadoras em regime especial, "
            "com vigencia temporal rastreavel por trimestre."
        ),
        tabela_raw_destino="bruto_ans.regime_especial_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="página institucional + certidão",
        url_publicacao=(
            "https://www.gov.br/pt-br/servicos/obter-certidao-de-regime-especial-de-direcao-tecnica"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "A ANS publica a certidao e comunica a instauracao/encerramento do regime especial "
            "em páginas e atos específicos; o contrato trata a vigencia por trimestre."
        ),
    ),
    "prudencial": ContratoFonteRegulatoriaV2(
        dataset_codigo="prudencial",
        nome="Capital Regulatório e acompanhamento prudencial",
        descricao=(
            "Bases e publicacoes da regulação prudencial usadas para compor margem, "
            "capital mínimo, capital disponível e índice de liquidez."
        ),
        tabela_raw_destino="bruto_ans.prudencial_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="página institucional + dados abertos",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/operadoras/regulacao-prudencial-"
            "acompanhamento-assistencial-e-economico-financeiro/regulacao-prudencial-1/"
            "capital-regulatorio"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "O contrato concentra o núcleo de capital regulatório e acompanhamento prudencial "
            "divulgado pela ANS em páginas institucionais e artefatos de apoio ao mercado."
        ),
    ),
    "portabilidade": ContratoFonteRegulatoriaV2(
        dataset_codigo="portabilidade",
        nome="Portabilidade de carências e movimentação assistida",
        descricao=(
            "Movimentação de beneficiários por operadora, modalidade e tipo de contratação "
            "para compor análise regulatória de portabilidade."
        ),
        tabela_raw_destino="bruto_ans.portabilidade_operadora_mensal",
        cadencia="mensal",
        formato_publicacao="página institucional + guia",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/contratacao-e-troca-de-plano/portabilidade-de-carencias"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "A fonte oficial da portabilidade é um conjunto de instrucoes, guias e consultas "
            "ao Guia ANS, tratado aqui como uma serie mensal operacional."
        ),
    ),
    "taxa_resolutividade": ContratoFonteRegulatoriaV2(
        dataset_codigo="taxa_resolutividade",
        nome="Taxa de Resolutividade de Notificação de Intermediação Preliminar",
        descricao=(
            "Painel e publicacoes oficiais com a taxa de resolutividade, usados como componente "
            "do score regulatório composto."
        ),
        tabela_raw_destino="bruto_ans.taxa_resolutividade_operadora_trimestral",
        cadencia="trimestral",
        formato_publicacao="painel + noticia institucional",
        url_publicacao=(
            "https://www.gov.br/ans/pt-br/assuntos/noticias/numeros-do-setor/"
            "ans-amplia-transparencia-sobre-indices-de-reclamacoes"
        ),
        atualizado_em_oficial="2026-04-22",
        observacao=(
            "A taxa de resolutividade é divulgada no painel de reclamacoes e comparativos "
            "por operadora, estado, regiao e cobertura contratada."
        ),
    ),
}
