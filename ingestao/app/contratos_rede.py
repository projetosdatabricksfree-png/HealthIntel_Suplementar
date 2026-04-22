from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContratoFonteRede:
    dataset_codigo: str
    nome: str
    descricao: str
    tabela_raw_destino: str
    cadencia: str
    formato_publicacao: str
    url_publicacao: str
    atualizado_em_oficial: str
    observacao: str


CONTRATO_REDE_ASSISTENCIAL = ContratoFonteRede(
    dataset_codigo="rede_assistencial",
    nome="Rede assistencial ANS",
    descricao=(
        "Conjunto de prestadores e especialidades por operadora, municipio, segmento e "
        "competencia, para inteligencia de cobertura territorial."
    ),
    tabela_raw_destino="bruto_ans.rede_prestador_municipio",
    cadencia="mensal",
    formato_publicacao="csv_zip",
    url_publicacao=(
        "https://www.gov.br/ans/pt-br/assuntos/noticias/beneficiario/"
        "ans-lanca-painel-de-rede-e-vazios-assistenciais-na-saude-suplementar"
    ),
    atualizado_em_oficial="2026-04-22",
    observacao=(
        "Contrato focado em rede credenciada com compatibilidade manual por layout e "
        "respeitando cobertura geográfica por municipio e UF."
    ),
)
