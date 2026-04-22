with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(modalidade)) as modalidade,
        lower(trim(tipo_lista)) as tipo_lista,
        coalesce(total_nip, 0) as total_nip,
        coalesce(beneficiarios, 0) as beneficiarios,
        cast(igr as numeric(12,4)) as igr,
        cast(meta_igr as numeric(12,4)) as meta_igr,
        coalesce(elegivel, true) as elegivel,
        observacao,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by
                upper(trim(trimestre)),
                {{ normalizar_registro_ans('registro_ans') }},
                lower(trim(tipo_lista))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'rn623_lista_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    modalidade,
    tipo_lista,
    total_nip,
    beneficiarios,
    igr,
    meta_igr,
    elegivel,
    observacao,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
