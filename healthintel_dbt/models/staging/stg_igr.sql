with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(modalidade)) as modalidade,
        upper(trim(coalesce(porte, 'NAO_INFORMADO'))) as porte,
        coalesce(total_reclamacoes, 0) as total_reclamacoes,
        coalesce(beneficiarios, 0) as beneficiarios,
        cast(igr as numeric(12,4)) as igr,
        cast(meta_igr as numeric(12,4)) as meta_igr,
        coalesce(atingiu_meta, false) as atingiu_meta,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'igr_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    modalidade,
    porte,
    total_reclamacoes,
    beneficiarios,
    igr,
    meta_igr,
    atingiu_meta,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
