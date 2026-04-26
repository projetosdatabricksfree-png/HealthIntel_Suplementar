{{ config(tags=['quality', 'documento', 'cadop']) }}

select
    registro_ans,
    cnpj_normalizado,
    documento_quality_status,
    motivo_invalidade_documento
from {{ ref('dq_cadop_documento') }}
where cnpj_normalizado is not null
  and cnpj_tamanho_valido
  and not cnpj_is_sequencia_invalida
  and not cnpj_digito_valido

