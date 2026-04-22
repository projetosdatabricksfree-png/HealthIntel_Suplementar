{{
    config(tags=['regulatorio_v2'])
}}

with base as (
    select
        cast(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g') as integer) as competencia,
        {{ competencia_para_data("lpad(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), 6, '0')") }} as competencia_data,
        {{ normalizar_registro_ans('registro_ans') }} as registro_ans,
        upper(trim(coalesce(base.modalidade, 'NAO_INFORMADA'))) as modalidade,
        coalesce(
            ref_modalidade.descricao,
            upper(trim(coalesce(base.modalidade, 'NAO_INFORMADA')))
        ) as modalidade_descricao,
        upper(trim(coalesce(tipo_contratacao, 'NAO_INFORMADO'))) as tipo_contratacao,
        coalesce(qt_portabilidade_entrada, 0) as qt_portabilidade_entrada,
        coalesce(qt_portabilidade_saida, 0) as qt_portabilidade_saida,
        coalesce(qt_portabilidade_entrada, 0) - coalesce(qt_portabilidade_saida, 0) as saldo_portabilidade,
        coalesce(fonte_publicacao, 'portabilidade_ans') as fonte_publicacao,
        _carregado_em,
        _arquivo_origem,
        _lote_id,
        row_number() over (
            partition by
                cast(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g') as integer),
                {{ normalizar_registro_ans('registro_ans') }}
            order by _carregado_em desc, _lote_id desc
        ) as rn
    from {{ source('bruto_ans', 'portabilidade_operadora_mensal') }} as base
    left join {{ ref('ref_modalidade') }} as ref_modalidade
        on upper(trim(coalesce(base.modalidade, 'NAO_INFORMADA'))) = ref_modalidade.modalidade
)

select
    competencia,
    competencia_data,
    registro_ans,
    modalidade,
    modalidade_descricao,
    tipo_contratacao,
    qt_portabilidade_entrada,
    qt_portabilidade_saida,
    saldo_portabilidade,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id
from base
where rn = 1
