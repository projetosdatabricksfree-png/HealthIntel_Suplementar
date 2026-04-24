{{
    config(materialized='table', tags=['dimensao', 'mart'])
}}

select 1 as segmentacao_id, 'NAO_INFORMADA' as codigo_segmentacao, 'NAO INFORMADA' as descricao_segmentacao, true as ativa
union all
select 2, 'AMBULATORIAL', 'AMBULATORIAL', true
union all
select 3, 'HOSPITALAR', 'HOSPITALAR', true
union all
select 4, 'ODONTOLOGICO', 'ODONTOLOGICO', true
