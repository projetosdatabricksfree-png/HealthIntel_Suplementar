{{
    config(
        tags=['tiss']
    )
}}

with base as (
    select
        upper(trim(regexp_replace(cast(trimestre as text), '\s+', '', 'g'))) as trimestre,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(coalesce(sg_uf, 'na'))) as sg_uf,
        lpad(regexp_replace(cast(grupo_procedimento as text), '[^0-9]', '', 'g'), 6, '0') as grupo_procedimento,
        upper(trim(coalesce(grupo_desc, 'nao informado'))) as grupo_desc,
        upper(trim(coalesce(subgrupo_procedimento, 'nao informado'))) as subgrupo_procedimento,
        coalesce(qt_procedimentos, 0) as qt_procedimentos,
        coalesce(qt_beneficiarios_distintos, 0) as qt_beneficiarios_distintos,
        cast(coalesce(valor_total, 0) as numeric(18, 2)) as valor_total,
        upper(trim(coalesce(modalidade, 'nao informado'))) as modalidade,
        upper(trim(coalesce(tipo_contratacao, 'nao informado'))) as tipo_contratacao,
        coalesce(fonte_publicacao, 'tiss_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        _layout_id,
        _layout_versao_id,
        _hash_arquivo,
        _hash_estrutura,
        _status_parse,
        row_number() over (
            partition by
                upper(trim(regexp_replace(cast(trimestre as text), '\s+', '', 'g'))),
                {{ normalizar_registro_ans('registro_ans') }},
                lpad(regexp_replace(cast(grupo_procedimento as text), '[^0-9]', '', 'g'), 6, '0'),
                upper(trim(coalesce(sg_uf, 'na')))
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'tiss_procedimento_trimestral') }}
)

select
    trimestre,
    registro_ans,
    sg_uf,
    grupo_procedimento,
    grupo_desc,
    subgrupo_procedimento,
    qt_procedimentos,
    qt_beneficiarios_distintos,
    valor_total,
    modalidade,
    tipo_contratacao,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id,
    _layout_id,
    _layout_versao_id,
    _hash_arquivo,
    _hash_estrutura,
    _status_parse
from base
where base.rn = 1
