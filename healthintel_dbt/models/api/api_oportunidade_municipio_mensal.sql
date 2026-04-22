{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia']) }}"
        ]
    )
}}

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    competencia,
    total_beneficiarios,
    hhi_municipio,
    cobertura_media_pct,
    cobertura_rede,
    oportunidade_score,
    'opportunity_v1' as versao_dataset
from {{ ref('fat_oportunidade_municipio_mensal') }}
