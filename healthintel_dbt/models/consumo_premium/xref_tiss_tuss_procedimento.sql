{{
    config(
        materialized='table',
        schema='consumo_premium_ans',
        tags=['consumo_premium', 'tiss', 'tuss']
    )
}}

-- Crosswalk sintético TISS/TUSS — Sprint 31.
-- Modo CI não comercial: correspondência baseada em prefixo do código TUSS.
-- Substituir por tabela oficial de mapeamento TISS↔TUSS quando disponível.

with tuss as (
    select
        codigo_tuss,
        descricao_tuss,
        grupo,
        subgrupo,
        capitulo,
        versao_tuss,
        is_tuss_vigente,
        quality_score_tuss
    from {{ ref('dim_tuss_procedimento') }}
),

tiss as (
    select distinct
        cd_procedimento_tuss,
        grupo_desc,
        subgrupo_procedimento
    from {{ ref('mart_tiss_procedimento') }}
    where cd_procedimento_tuss is not null
)

select
    tuss.codigo_tuss,
    tuss.descricao_tuss,
    tuss.grupo as tuss_grupo,
    tuss.subgrupo as tuss_subgrupo,
    tuss.versao_tuss,
    tuss.is_tuss_vigente,
    tiss.cd_procedimento_tuss as tiss_codigo_procedimento,
    tiss.grupo_desc as tiss_grupo,
    tiss.subgrupo_procedimento as tiss_subgrupo,
    -- tiss_tuss_match_status: sempre UNMATCHED em modo sintético
    -- pois não há mapeamento real TISS↔TUSS disponível
    case
        when tiss.cd_procedimento_tuss is null then 'UNMATCHED'
        when tuss.codigo_tuss = tiss.cd_procedimento_tuss then 'MATCHED'
        else 'UNMATCHED'
    end as tiss_tuss_match_status,
    -- quality_score_tuss: herdado da dim_tuss_procedimento (0-100)
    least(100, greatest(0, tuss.quality_score_tuss))::numeric(5, 2) as quality_score_tuss,
    100::numeric(5, 2) as quality_score_publicacao,
    current_timestamp as dt_processamento
from tuss
left join tiss
    on tuss.codigo_tuss = tiss.cd_procedimento_tuss
