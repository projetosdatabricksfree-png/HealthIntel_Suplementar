{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    ben.competencia,
    ben.registro_ans,
    op.nome as razao_social,
    op.nome_fantasia,
    op.modalidade,
    op.uf_sede as uf,
    ben.qt_beneficiario_ativo as qt_beneficiarios,
    ben.qt_beneficiario_medico,
    ben.qt_beneficiario_odonto,
    ben.taxa_crescimento_12m,
    ben.volatilidade_24m
from {{ ref('fat_beneficiario_operadora') }} as ben
left join {{ ref('dim_operadora_atual') }} as op
    on op.registro_ans = ben.registro_ans
