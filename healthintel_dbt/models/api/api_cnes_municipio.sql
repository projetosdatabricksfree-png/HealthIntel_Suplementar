{{
    config(
        materialized='table',
        tags=['cnes'],
        post_hook=[
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'tipo_unidade') }}"
        ]
    )
}}

select
    cnes.competencia,
    cnes.cd_municipio,
    cnes.nm_municipio,
    uf.nome as nm_uf,
    cnes.sg_uf,
    cnes.nm_regiao as regiao,
    cnes.tipo_unidade,
    cnes.tipo_unidade_desc,
    cnes.total_estabelecimentos,
    cnes.total_estabelecimentos_vinculo_sus,
    cnes.total_leitos,
    cnes.total_leitos_sus,
    cnes.pct_leitos_sus,
    cnes.pct_vinculo_sus,
    cnes.pop_estimada_ibge,
    cnes.porte_municipio,
    cnes.versao_dataset
from {{ ref('fat_cnes_estabelecimento_municipio') }} as cnes
left join {{ ref('ref_uf') }} as uf
    on cnes.sg_uf = uf.uf
