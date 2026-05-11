{{
    config(
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio']) }}",
            "{{ criar_indices(this, ['sg_uf']) }}",
            "{{ criar_indices(this, ['competencia']) }}",
            "{{ criar_indices(this, ['ranking_posicao']) }}"
        ],
        tags=['oportunidade_v2']
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
    ranking_posicao,
    sinal_vazio,
    versao_algoritmo
from {{ ref('fat_oportunidade_v2_municipio_mensal') }}
order by ranking_posicao asc, nm_municipio asc
