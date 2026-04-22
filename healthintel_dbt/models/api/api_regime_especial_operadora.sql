{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'operadora_id') }}",
            "{{ criar_indice_api(this, 'ativo') }}"
        ],
        tags=['regulatorio_v2']
    )
}}

select
    f.operadora_id,
    f.registro_ans,
    f.nome,
    f.nome_fantasia,
    f.modalidade,
    f.uf_sede,
    f.trimestre_inicio as trimestre,
    f.trimestre_fim,
    f.tipo_regime,
    f.ativo,
    f.duracao_trimestres,
    f.data_inicio,
    f.data_fim,
    f.versao_dataset
from {{ ref('fat_regime_especial_historico') }} as f
