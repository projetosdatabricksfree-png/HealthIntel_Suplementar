{{ config(tags=['quality', 'documento', 'cnpj'], severity='error') }}

-- Hard gate: CNPJ com tamanho diferente de 14 digitos ou sequencia repetida
-- invalida. Ignora CNPJ nulo (classificado como NULO pela macro), que nao
-- quebra o CI nesta sprint.
with documento as (
    select
'dq_cadop_documento' as modelo_nome,
registro_ans as chave,
cnpj_normalizado,
cnpj_tamanho_valido,
cnpj_is_sequencia_invalida
    from {{ ref('dq_cadop_documento') }}

    union all

    select
'dq_operadora_documento' as modelo_nome,
registro_ans as chave,
cnpj_normalizado,
cnpj_tamanho_valido,
cnpj_is_sequencia_invalida
    from {{ ref('dq_operadora_documento') }}

    union all

    select
'dq_cnes_documento' as modelo_nome,
cnes as chave,
cnpj_normalizado,
cnpj_tamanho_valido,
cnpj_is_sequencia_invalida
    from {{ ref('dq_cnes_documento') }}
)

select
    modelo_nome,
    chave,
    cnpj_normalizado
from documento
where cnpj_normalizado is not null
  and (not cnpj_tamanho_valido or cnpj_is_sequencia_invalida)
