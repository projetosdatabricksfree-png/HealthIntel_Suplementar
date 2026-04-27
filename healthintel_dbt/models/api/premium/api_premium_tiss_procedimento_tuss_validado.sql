{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'trimestre') }}",
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'cd_procedimento_tuss') }}"
        ]
    )
}}

select
    trimestre,
    registro_ans,
    operadora_master_id,
    razao_social,
    cd_procedimento_tuss,
    grupo_desc,
    subgrupo_procedimento,
    qt_procedimentos,
    vl_total,
    custo_medio_procedimento,
    sinistralidade_pct,
    rank_por_valor,
    status_mdm,
    mdm_confidence_score,
    procedimento_quality_status,
    quality_score_procedimento
from {{ ref('consumo_premium_tiss_procedimento_tuss_validado') }}
