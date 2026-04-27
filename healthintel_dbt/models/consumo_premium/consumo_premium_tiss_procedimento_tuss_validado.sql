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
    tiss.trimestre,
    tiss.registro_ans,
    mdm.operadora_master_id,
    tiss.razao_social,
    tiss.cd_procedimento_tuss,
    tiss.grupo_desc,
    tiss.subgrupo_procedimento,
    tiss.qt_procedimentos,
    tiss.vl_total,
    tiss.custo_medio_procedimento,
    tiss.sinistralidade_pct,
    tiss.rank_por_valor,
    mdm.status_mdm,
    mdm.confidence_score as mdm_confidence_score,
    case
        when tiss.cd_procedimento_tuss is not null then 'VALIDO'
        else 'NULO'
    end as procedimento_quality_status,
    case
        when tiss.cd_procedimento_tuss is not null then 100::numeric(5, 2)
        else 0::numeric(5, 2)
    end as quality_score_procedimento
from {{ ref('mart_tiss_procedimento') }} as tiss
inner join {{ ref('mdm_operadora_master') }} as mdm
    on tiss.registro_ans = mdm.registro_ans_canonico
where mdm.status_mdm = 'ATIVO'
  and tiss.cd_procedimento_tuss is not null
