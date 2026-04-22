{{
    config(tags=['regulatorio_v2'])
}}

with base as (
    select
        upper(trim(trimestre)) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(coalesce(base.modalidade, ref_modalidade.modalidade))) as modalidade,
        coalesce(ref_modalidade.descricao, upper(trim(coalesce(base.modalidade, 'NAO_INFORMADA')))) as modalidade_descricao,
        cast(taxa_resolutividade as numeric(12,4)) as taxa_resolutividade,
        coalesce(n_reclamacao_resolvida, 0) as n_reclamacao_resolvida,
        coalesce(n_reclamacao_total, 0) as n_reclamacao_total,
        coalesce(fonte_publicacao, 'taxa_resolutividade_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by upper(trim(trimestre)), {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'taxa_resolutividade_operadora_trimestral') }} as base
    left join {{ ref('ref_modalidade') }} as ref_modalidade
        on upper(trim(coalesce(base.modalidade, 'NAO_INFORMADA'))) = ref_modalidade.modalidade
)

select
    trimestre,
    registro_ans,
    modalidade,
    modalidade_descricao,
    taxa_resolutividade,
    n_reclamacao_resolvida,
    n_reclamacao_total,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
