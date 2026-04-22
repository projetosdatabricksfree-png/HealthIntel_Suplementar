{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'registro_ans, trimestre') }}"
        ]
    )
}}

select
    fat.registro_ans,
    fat.trimestre,
    dim.nome,
    dim.nome_fantasia,
    dim.modalidade,
    dim.uf_sede,
    fat.igr,
    fat.meta_igr,
    fat.atingiu_meta_excelencia,
    fat.demandas_nip,
    fat.demandas_resolvidas,
    fat.taxa_intermediacao_resolvida,
    fat.taxa_resolutividade,
    fat.rn623_excelencia,
    fat.rn623_reducao,
    fat.faixa_risco_regulatorio,
    case
        when fat.rn623_excelencia then 'excelencia'
        when fat.rn623_reducao then 'reducao'
        else 'fora_lista'
    end as status_rn623,
    'regulatorio_v1' as versao_regulatoria
from {{ ref('fat_monitoramento_regulatorio_trimestral') }} as fat
inner join {{ ref('dim_operadora_atual') }} as dim
    on fat.registro_ans = dim.registro_ans
