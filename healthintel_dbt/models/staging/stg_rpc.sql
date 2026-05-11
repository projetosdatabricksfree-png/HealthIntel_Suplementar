{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        lpad(regexp_replace(cast(coalesce(cd_municipio, '') as text), '[^0-9]', '', 'g'), 7, '0')
                                                        as cd_municipio,
        upper(trim(coalesce(sg_uf, '')))                as sg_uf,
        upper(trim(coalesce(tipo_reclamacao, '')))      as tipo_reclamacao,
        coalesce(cast(nullif(trim(cast(qt_reclamacoes as text)), '') as integer), 0)
                                                        as qt_reclamacoes,
        coalesce(cast(nullif(trim(cast(qt_resolvidas as text)), '') as integer), 0)
                                                        as qt_resolvidas,
        cast(nullif(trim(cast(coalesce(indice_resolucao, '0') as text)), '') as numeric(10, 4))
                                                        as indice_resolucao,
        cast(nullif(trim(cast(coalesce(nota_rpc, '0') as text)), '') as numeric(5, 2))
                                                        as nota_rpc,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'rpc') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
