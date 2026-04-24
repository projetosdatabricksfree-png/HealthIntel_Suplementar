{{
    config(
        materialized='table',
        tags=['tiss'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'trimestre') }}",
            "{{ criar_indice_api(this, 'grupo_procedimento') }}"
        ]
    )
}}

select
    tiss.trimestre,
    tiss.operadora_id,
    tiss.registro_ans,
    tiss.nome,
    tiss.nome_fantasia,
    tiss.modalidade as modalidade_operadora,
    tiss.uf_sede,
    tiss.grupo_procedimento,
    tiss.grupo_desc,
    tiss.subgrupo_procedimento,
    tiss.qt_procedimentos,
    tiss.qt_beneficiarios_distintos,
    tiss.valor_total,
    tiss.valor_medio,
    tiss.pct_do_total_operadora,
    tiss.rank_por_valor,
    tiss.versao_dataset
from {{ ref('fat_tiss_procedimento_operadora') }} as tiss
