{{
    config(
        materialized='ephemeral',
        tags=['oportunidade_v2']
    )
}}

with oportunidade_v1 as (
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
        oportunidade_score
    from {{ ref('fat_oportunidade_municipio_mensal') }}
),
cobertura_municipal as (
    select
        cd_municipio,
        competencia,
        max(nm_municipio) as nm_municipio,
        max(sg_uf) as sg_uf,
        max(nm_regiao) as nm_regiao,
        count(distinct case when tem_cobertura then operadora_id end) as qt_operadoras_cobertura,
        count(distinct case when tem_cobertura then segmento end) as qt_segmentos_cobertos,
        count(distinct case when not tem_cobertura then segmento end) as qt_segmentos_vazios,
        count(
            distinct case
                when tem_cobertura and not cobertura_minima_atendida then segmento
            end
        ) as qt_segmentos_parciais,
        round(
            coalesce(
                (
                    count(distinct case when tem_cobertura then operadora_id end)::numeric
                    / nullif(count(distinct operadora_id), 0)
                ) * 100,
                0
            ),
            2
        ) as pct_operadoras_com_cobertura,
        round(
            coalesce(
                (
                    count(distinct case when not tem_cobertura then operadora_id end)::numeric
                    / nullif(count(distinct operadora_id), 0)
                ) * 100,
                0
            ),
            2
        ) as pct_operadoras_sem_cobertura
    from {{ ref('fat_cobertura_rede_municipio') }}
    group by 1, 2
),
vazio_presenca as (
    select
        cd_municipio,
        competencia,
        bool_or(vazio_total or vazio_parcial) as vazio_assistencial_presente
    from {{ ref('fat_vazio_assistencial_municipio') }}
    group by 1, 2
),
operadora_relevante as (
    select
        cobertura.cd_municipio,
        cobertura.competencia,
        score_v2.operadora_id,
        score_v2.registro_ans,
        score_v2.score_v2,
        row_number() over (
            partition by cobertura.cd_municipio, cobertura.competencia
            order by score_v2.score_v2 desc nulls last, score_v2.operadora_id
        ) as linha
    from (
        select distinct
            cd_municipio,
            competencia,
            operadora_id
        from {{ ref('fat_cobertura_rede_municipio') }}
    ) as cobertura
    inner join {{ ref('fat_score_v2_operadora_mensal') }} as score_v2
        on score_v2.operadora_id = cobertura.operadora_id
        and score_v2.competencia = cobertura.competencia
),
score_v2_municipio as (
    select
        cd_municipio,
        competencia,
        registro_ans as operadora_melhor_score_v2,
        score_v2 as score_v2_maximo
    from operadora_relevante
    where linha = 1
)

select
    v1.cd_municipio,
    v1.nm_municipio,
    v1.sg_uf,
    v1.nm_regiao,
    v1.competencia,
    v1.total_beneficiarios,
    v1.hhi_municipio,
    v1.cobertura_media_pct,
    v1.cobertura_rede,
    v1.oportunidade_score as oportunidade_score_v1,
    coalesce(cobertura_municipal.qt_operadoras_cobertura, 0) as qt_operadoras_cobertura,
    coalesce(cobertura_municipal.qt_segmentos_cobertos, 0) as qt_segmentos_cobertos,
    coalesce(cobertura_municipal.qt_segmentos_vazios, 0) as qt_segmentos_vazios,
    coalesce(cobertura_municipal.qt_segmentos_parciais, 0) as qt_segmentos_parciais,
    coalesce(cobertura_municipal.pct_operadoras_com_cobertura, 0) as pct_operadoras_com_cobertura,
    coalesce(cobertura_municipal.pct_operadoras_sem_cobertura, 0) as pct_operadoras_sem_cobertura,
    coalesce(vazio_presenca.vazio_assistencial_presente, false) as vazio_assistencial_presente,
    score_v2_municipio.operadora_melhor_score_v2,
    coalesce(score_v2_municipio.score_v2_maximo, 0) as score_v2_maximo,
    round(
        least(
            100,
            greatest(
                0,
                100
                - coalesce(cobertura_municipal.pct_operadoras_com_cobertura, 0)
                + case when coalesce(vazio_presenca.vazio_assistencial_presente, false) then 10 else 0 end
            )
        ),
        2
    ) as score_oportunidade_rede,
    round(
        least(
            100,
            greatest(
                0,
                coalesce(v1.oportunidade_score, 0) * 0.40
                + (
                    100
                    - coalesce(cobertura_municipal.pct_operadoras_com_cobertura, 0)
                    + case when coalesce(vazio_presenca.vazio_assistencial_presente, false) then 10 else 0 end
                ) * 0.35
                + coalesce(score_v2_municipio.score_v2_maximo, 0) * 0.25
            )
        ),
        2
    ) as oportunidade_v2_score,
    case
        when coalesce(vazio_presenca.vazio_assistencial_presente, false) then 'vazio_detectado'
        else 'sem_vazio'
    end as sinal_vazio,
    null::numeric as score_sip,
    'v2.0' as versao_algoritmo
from oportunidade_v1 as v1
left join cobertura_municipal
    on cobertura_municipal.cd_municipio = v1.cd_municipio
    and cobertura_municipal.competencia = v1.competencia
left join vazio_presenca
    on vazio_presenca.cd_municipio = v1.cd_municipio
    and vazio_presenca.competencia = v1.competencia
left join score_v2_municipio
    on score_v2_municipio.cd_municipio = v1.cd_municipio
    and score_v2_municipio.competencia = v1.competencia
