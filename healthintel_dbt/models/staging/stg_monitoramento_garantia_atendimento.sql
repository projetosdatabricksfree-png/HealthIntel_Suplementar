{{ config(tags=['delta_ans_100', 'regulatorios_complementares']) }}

with base as (
    select
        cast(
            nullif(regexp_replace(cast(competencia as text), '[^0-9]', '', 'g'), '')
            as integer
        )                                               as competencia,
        lpad(trim(coalesce(registro_ans, '')), 6, '0')  as registro_ans,
        upper(trim(coalesce(tipo_garantia, '')))        as tipo_garantia,
        coalesce(cast(nullif(trim(cast(qt_ocorrencias as text)), '') as integer), 0)
                                                        as qt_ocorrencias,
        coalesce(cast(nullif(trim(cast(qt_resolvidas as text)), '') as integer), 0)
                                                        as qt_resolvidas,
        coalesce(cast(nullif(trim(cast(qt_pendentes as text)), '') as integer), 0)
                                                        as qt_pendentes,
        cast(nullif(trim(cast(coalesce(prazo_medio_resolucao, '0') as text)), '') as numeric(10, 2))
                                                        as prazo_medio_resolucao,
        _carregado_em,
        _arquivo_origem,
        _lote_id
    from {{ source('bruto_ans', 'monitoramento_garantia_atendimento') }}
    where trim(coalesce(registro_ans, '')) != ''
)

select *
from base
where competencia is not null
