{{
    config(
        materialized='table',
        schema='quality_ans',
        tags=['quality', 'audit', 'documento', 'operadora', 'cadop']
    )
}}

-- Auditoria de razao social divergente entre a dimensao de operadora e a
-- fonte CADOP/ANS, quando o CNPJ e identico e valido em ambas as fontes.
-- Este modelo NAO e um hard gate — existe apenas para inspecao humana.
-- Divergencias podem ser causadas por: acentuacao, abreviacao (LTDA/SA/S.A.),
-- nome fantasia vs razao social, ou variacao textual inofensiva.
-- Nao ha teste dbt vinculado a este modelo.
with operadora_valida as (
    select
        registro_ans_normalizado,
        cnpj_normalizado,
        nome as nome_operadora
    from {{ ref('dq_operadora_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnpj_normalizado is not null
),

cadop_valido as (
    select
        registro_ans_normalizado,
        cnpj_normalizado,
        nome as nome_cadop
    from {{ ref('dq_cadop_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnpj_normalizado is not null
)

select
    op.registro_ans_normalizado,
    op.cnpj_normalizado,
    op.nome_operadora,
    cp.nome_cadop,
    case
        when lower(trim(op.nome_operadora)) = lower(trim(cp.nome_cadop)) then 'IDENTICO'
        else 'DIVERGENTE'
    end as status_comparacao,
    current_timestamp as _auditado_em
from operadora_valida op
inner join cadop_valido cp
    on op.registro_ans_normalizado = cp.registro_ans_normalizado
   and op.cnpj_normalizado = cp.cnpj_normalizado
where lower(trim(op.nome_operadora)) <> lower(trim(cp.nome_cadop))