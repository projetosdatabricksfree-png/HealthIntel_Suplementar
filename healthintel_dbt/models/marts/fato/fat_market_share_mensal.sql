{{
    config(
        materialized='table',
        post_hook=[
            "{{ criar_indices(this, ['cd_municipio', 'competencia']) }}",
            "{{ criar_indices(this, ['registro_ans']) }}"
        ]
    )
}}

select
    metrica.cd_municipio,
    metrica.nm_municipio,
    metrica.sg_uf,
    metrica.nm_regiao,
    metrica.competencia,
    metrica.operadora_id,
    metrica.registro_ans,
    dim.nome,
    dim.nome_fantasia,
    dim.modalidade,
    dim.uf_sede,
    metrica.municipio,
    metrica.uf,
    metrica.beneficiario_total,
    metrica.total_beneficiarios_municipio,
    metrica.market_share_pct,
    metrica.hhi_municipio,
    metrica.concentracao_mercado,
    upper(coalesce(dim.modalidade, 'NAO_INFORMADA')) as segmento
from {{ ref('int_metrica_municipio') }} as metrica
left join {{ ref('dim_operadora_atual') }} as dim
    on metrica.registro_ans = dim.registro_ans
