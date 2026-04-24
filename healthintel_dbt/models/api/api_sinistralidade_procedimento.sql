{{
    config(
        materialized='table',
        tags=['tiss', 'financeiro'],
        post_hook=[
            "{{ criar_indice_api(this, 'registro_ans') }}",
            "{{ criar_indice_api(this, 'trimestre') }}"
        ]
    )
}}

select
    sinistro.trimestre,
    sinistro.operadora_id,
    sinistro.registro_ans,
    sinistro.nome,
    sinistro.nome_fantasia,
    sinistro.modalidade as modalidade_operadora,
    sinistro.uf_sede,
    sinistro.grupo_procedimento,
    sinistro.grupo_desc,
    sinistro.subgrupo_procedimento,
    sinistro.qt_procedimentos,
    sinistro.qt_beneficiarios_distintos,
    sinistro.valor_tiss,
    sinistro.receita_total,
    sinistro.sinistralidade_grupo_pct,
    sinistro.desvio_padrao_sinistralidade,
    sinistro.flag_sinistralidade_alta,
    sinistro.rank_sinistralidade,
    sinistro.versao_dataset
from {{ ref('fat_sinistralidade_procedimento') }} as sinistro
