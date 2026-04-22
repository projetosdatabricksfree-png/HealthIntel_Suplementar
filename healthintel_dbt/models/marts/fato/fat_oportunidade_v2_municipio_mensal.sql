{{
    config(
        materialized='table',
        tags=['oportunidade_v2'],
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia', 'sg_uf']) }}"
        ]
    )
}}

with base as (
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
        oportunidade_score_v1,
        qt_operadoras_cobertura,
        qt_segmentos_cobertos,
        qt_segmentos_vazios,
        qt_segmentos_parciais,
        pct_operadoras_com_cobertura,
        pct_operadoras_sem_cobertura,
        vazio_assistencial_presente,
        operadora_melhor_score_v2,
        score_v2_maximo,
        score_oportunidade_rede,
        score_sip,
        oportunidade_v2_score,
        sinal_vazio,
        versao_algoritmo
    from {{ ref('int_oportunidade_v2_municipio') }}
)

select
    base.*,
    row_number() over (
        partition by competencia
        order by oportunidade_v2_score desc nulls last, total_beneficiarios desc nulls last, nm_municipio
    ) as ranking_posicao
from base
