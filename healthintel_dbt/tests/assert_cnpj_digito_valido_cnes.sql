{{ config(tags=['quality', 'documento', 'cnes'], severity='warn') }}

-- Sinal de qualidade: contagem de CNPJ com 14 digitos e nao-sequencial cujo DV
-- nao bate. A tabela `dq_cnes_documento` ja classifica esses casos como
-- INVALIDO_DIGITO, entao este teste e severity=warn para evitar bloquear o
-- pipeline quando o snapshot CNES/DATASUS traz CNPJs ficticios (demo) ou
-- corrompidos. Em producao com snapshot CNES real a contagem deve tender a
-- zero.
select
    competencia,
    cnes,
    cnpj_normalizado,
    documento_quality_status,
    motivo_invalidade_documento
from {{ ref('dq_cnes_documento') }}
where cnpj_normalizado is not null
  and cnpj_tamanho_valido
  and not cnpj_is_sequencia_invalida
  and not cnpj_digito_valido

