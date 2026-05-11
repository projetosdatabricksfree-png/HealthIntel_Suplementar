{{ config(tags=['quality', 'documento', 'cnpj', 'cadop', 'operadora'], severity='error') }}

-- Hard gate: CNPJ divergente entre a dimensao de operadora e a fonte CADOP/ANS
-- pelo mesmo registro_ans. Quando ambos possuem CNPJ VALIDO, o numero deve ser
-- identico. Divergencia indica corrupcao, duplicata ou erro de carga.
with operadora_valida as (
    select
        registro_ans_normalizado,
        cnpj_normalizado as cnpj_operadora,
        nome as nome_operadora
    from {{ ref('dq_operadora_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnpj_normalizado is not null
),

cadop_valido as (
    select
        registro_ans_normalizado,
        cnpj_normalizado as cnpj_cadop,
        nome as nome_cadop
    from {{ ref('dq_cadop_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnpj_normalizado is not null
)

select
    op.registro_ans_normalizado,
    op.cnpj_operadora,
    cp.cnpj_cadop,
    op.nome_operadora,
    cp.nome_cadop
from operadora_valida as op
inner join cadop_valido as cp
    on op.registro_ans_normalizado = cp.registro_ans_normalizado
where op.cnpj_operadora <> cp.cnpj_cadop
