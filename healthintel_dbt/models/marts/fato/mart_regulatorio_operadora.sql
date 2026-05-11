{{
    config(materialized='table', tags=['mart'])
}}

select
    reg.registro_ans,
    reg.trimestre,
    op.nome as razao_social,
    op.modalidade,
    reg.total_reclamacoes as qtd_reclamacoes,
    reg.igr as indice_reclamacao,
    reg.demandas_nip,
    reg.taxa_resolutividade,
    reg.faixa_risco_regulatorio as nivel_alerta,
    case
        when reg.faixa_risco_regulatorio = 'alto' then 'piora'
        when reg.faixa_risco_regulatorio = 'baixo' then 'melhora'
        else 'estavel'
    end as tendencia_regulatoria
from {{ ref('fat_monitoramento_regulatorio_trimestral') }} as reg
left join {{ ref('dim_operadora_atual') }} as op
    on reg.registro_ans = op.registro_ans
