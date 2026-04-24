{{ config(materialized='table', schema='consumo_ans', tags=['consumo']) }}

select
    loc.registro_ans,
    op.nome as razao_social,
    loc.cd_municipio,
    loc.nm_municipio as nome_municipio,
    loc.sg_uf as uf,
    loc.competencia,
    loc.qt_beneficiario_ativo as qt_beneficiarios
from {{ ref('fat_beneficiario_localidade') }} as loc
left join {{ ref('dim_operadora_atual') }} as op
    on op.registro_ans = loc.registro_ans
