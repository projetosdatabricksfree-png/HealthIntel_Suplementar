{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia', 'segmento']) }}"
        ],
        tags=['vazio']
    )
}}

select
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    competencia,
    segmento,
    qt_operadora_presente,
    qt_operadora_sem_cobertura,
    qt_operadora_total,
    pct_operadoras_com_cobertura,
    pct_operadoras_sem_cobertura,
    vazio_total,
    vazio_parcial,
    versao_dataset
from {{ ref('fat_vazio_assistencial_municipio') }}
order by competencia desc, vazio_total desc, pct_operadoras_sem_cobertura desc, nm_municipio asc
