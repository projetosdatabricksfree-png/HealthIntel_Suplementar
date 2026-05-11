{{
    config(tags=['regulatorio_v2'])
}}

with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        cast(margem_solvencia as numeric(18,4)) as margem_solvencia,
        cast(capital_minimo_requerido as numeric(18,4)) as capital_minimo_requerido,
        cast(capital_disponivel as numeric(18,4)) as capital_disponivel,
        cast(indice_liquidez as numeric(18,4)) as indice_liquidez,
        lower(trim(coalesce(situacao_prudencial, 'adequada'))) as situacao_prudencial,
        coalesce(fonte_publicacao, 'prudencial_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        coalesce(lower(trim(coalesce(situacao_prudencial, ''))) in ('inadequada', 'critica', 'risco'), false) as situacao_inadequada,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'prudencial_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    margem_solvencia,
    capital_minimo_requerido,
    capital_disponivel,
    indice_liquidez,
    situacao_prudencial,
    situacao_inadequada,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
