with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(modalidade)) as modalidade,
        coalesce(demandas_nip, 0) as demandas_nip,
        coalesce(demandas_resolvidas, 0) as demandas_resolvidas,
        coalesce(beneficiarios, 0) as beneficiarios,
        cast(taxa_intermediacao_resolvida as numeric(8,4)) as taxa_intermediacao_resolvida,
        cast(taxa_resolutividade as numeric(8,4)) as taxa_resolutividade,
        fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'nip_operadora_trimestral') }}
)

select
    trimestre,
    registro_ans,
    modalidade,
    demandas_nip,
    demandas_resolvidas,
    beneficiarios,
    taxa_intermediacao_resolvida,
    taxa_resolutividade,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
