{{ config(
    severity='warn',
    tags=['quality', 'documento', 'cnpj', 'documento_warning']
) }}

-- Sinal de qualidade: CNPJ com 14 dígitos e não-sequencial cujo DV
-- não bate, unificado sobre os 3 modelos dq_*.
-- A tag `documento_warning` permite que o CI isole este teste
-- e NÃO aplique --warn-error sobre ele.

with documento as (
    select
        'dq_cadop_documento' as modelo,
        cast(registro_ans as text) as chave,
        cnpj_normalizado,
        cnpj_tamanho_valido,
        cnpj_is_sequencia_invalida,
        cnpj_digito_valido
    from {{ ref('dq_cadop_documento') }}

    union all

    select
        'dq_operadora_documento' as modelo,
        cast(registro_ans as text) as chave,
        cnpj_normalizado,
        cnpj_tamanho_valido,
        cnpj_is_sequencia_invalida,
        cnpj_digito_valido
    from {{ ref('dq_operadora_documento') }}

    union all

    select
        'dq_cnes_documento' as modelo,
        cast(cnes as text) as chave,
        cnpj_normalizado,
        cnpj_tamanho_valido,
        cnpj_is_sequencia_invalida,
        cnpj_digito_valido
    from {{ ref('dq_cnes_documento') }}
)

select
    modelo,
    chave,
    cnpj_normalizado
from documento
where cnpj_normalizado is not null
  and cnpj_tamanho_valido is true
  and cnpj_is_sequencia_invalida is false
  and cnpj_digito_valido is false
