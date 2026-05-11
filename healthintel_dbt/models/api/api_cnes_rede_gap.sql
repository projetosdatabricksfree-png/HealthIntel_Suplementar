{{
    config(
        materialized='table',
        tags=['cnes', 'rede'],
        post_hook=[
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'tipo_unidade') }}"
        ]
    )
}}

select
    gap.competencia,
    gap.cd_municipio,
    gap.nm_municipio,
    uf.nome as nm_uf,
    gap.sg_uf,
    gap.nm_regiao as regiao,
    gap.tipo_unidade,
    gap.tipo_unidade_desc,
    gap.estabelecimentos_cnes,
    gap.prestadores_credenciados,
    gap.gap_absoluto,
    gap.gap_pct,
    gap.severidade_gap,
    gap.flag_gap_critico,
    gap.versao_dataset
from {{ ref('fat_cnes_rede_gap_municipio') }} as gap
left join {{ ref('ref_uf') }} as uf
    on gap.sg_uf = uf.uf
