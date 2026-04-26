{{ config(tags=['quality', 'documento', 'cnes']) }}

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

