{{
    config(materialized='table', tags=['dimensao', 'mart'])
}}

select
    1 as segmentacao_id,
    'NAO_INFORMADA' as codigo_segmentacao,
    'NAO INFORMADA' as descricao_segmentacao,
    true as ativa
union all
select
    2 as segmentacao_id,
    'AMBULATORIAL' as codigo_segmentacao,
    'AMBULATORIAL' as descricao_segmentacao,
    true as ativa
union all
select
    3 as segmentacao_id,
    'HOSPITALAR' as codigo_segmentacao,
    'HOSPITALAR' as descricao_segmentacao,
    true as ativa
union all
select
    4 as segmentacao_id,
    'ODONTOLOGICO' as codigo_segmentacao,
    'ODONTOLOGICO' as descricao_segmentacao,
    true as ativa
