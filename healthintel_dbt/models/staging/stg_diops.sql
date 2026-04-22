{{
    config(tags=['financeiro'])
}}

with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        trim(cnpj) as cnpj,
        cast(ativo_total as numeric(18,4)) as ativo_total,
        cast(passivo_total as numeric(18,4)) as passivo_total,
        cast(patrimonio_liquido as numeric(18,4)) as patrimonio_liquido,
        cast(receita_total as numeric(18,4)) as receita_total,
        cast(despesa_total as numeric(18,4)) as despesa_total,
        cast(resultado_periodo as numeric(18,4)) as resultado_periodo,
        cast(provisao_tecnica as numeric(18,4)) as provisao_tecnica,
        cast(margem_solvencia_calculada as numeric(18,4)) as margem_solvencia_calculada,
        coalesce(fonte_publicacao, 'diops_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        case
            when coalesce(receita_total, 0) - coalesce(despesa_total, 0) >= 0 then 'superavit'
            else 'deficit'
        end as situacao_resultado,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'diops_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    cnpj,
    ativo_total,
    passivo_total,
    patrimonio_liquido,
    receita_total,
    despesa_total,
    resultado_periodo,
    receita_total - despesa_total as resultado_operacional,
    provisao_tecnica,
    margem_solvencia_calculada,
    situacao_resultado,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
