{{
    config(
        unique_key=['operadora_id', 'competencia'],
        incremental_strategy='delete+insert',
        on_schema_change='sync_all_columns'
    )
}}

with pesos_base as (
    select
        versao_score,
        componente,
        cast(peso as numeric(10,4)) as peso,
        cast(cast(vigente_inicio as text) as date) as vigente_inicio,
        cast(nullif(cast(vigente_fim as text), '') as date) as vigente_fim,
        cast(cast(ativo as text) as boolean) as ativo
    from {{ ref('score_pesos') }}
    where cast(cast(ativo as text) as boolean) is true
),
pesos_ativos as (
    select
        versao_score,
        max(case when componente = 'crescimento' then peso end) as peso_crescimento,
        max(case when componente = 'qualidade' then peso end) as peso_qualidade,
        max(case when componente = 'estabilidade' then peso end) as peso_estabilidade,
        max(case when componente = 'presenca' then peso end) as peso_presenca,
        row_number() over (
            order by max(vigente_inicio) desc, versao_score desc
        ) as rn
    from pesos_base
    where vigente_inicio <= current_date
        and (vigente_fim is null or vigente_fim >= current_date)
    group by versao_score
),
pesos as (
    select
        versao_score,
        peso_crescimento,
        peso_qualidade,
        peso_estabilidade,
        peso_presenca
    from pesos_ativos
    where rn = 1
),
base as (
    select *
    from {{ ref('int_score_insumo') }}
)

select
    base.operadora_id,
    base.registro_ans,
    competencia,
    round(
        (
            (base.score_crescimento * pesos.peso_crescimento)
            + (base.score_qualidade * pesos.peso_qualidade)
            + (base.score_estabilidade * pesos.peso_estabilidade)
            + (base.score_presenca * pesos.peso_presenca)
        ),
        2
    )::numeric(10,2) as score_final,
    base.score_crescimento::numeric(10,2) as score_crescimento,
    base.score_qualidade::numeric(10,2) as score_qualidade,
    base.score_estabilidade::numeric(10,2) as score_estabilidade,
    base.score_presenca::numeric(10,2) as score_presenca,
    case
        when (
            (base.score_crescimento * pesos.peso_crescimento)
            + (base.score_qualidade * pesos.peso_qualidade)
            + (base.score_estabilidade * pesos.peso_estabilidade)
            + (base.score_presenca * pesos.peso_presenca)
        ) >= 85 then 'A'
        when (
            (base.score_crescimento * pesos.peso_crescimento)
            + (base.score_qualidade * pesos.peso_qualidade)
            + (base.score_estabilidade * pesos.peso_estabilidade)
            + (base.score_presenca * pesos.peso_presenca)
        ) >= 75 then 'B'
        when (
            (base.score_crescimento * pesos.peso_crescimento)
            + (base.score_qualidade * pesos.peso_qualidade)
            + (base.score_estabilidade * pesos.peso_estabilidade)
            + (base.score_presenca * pesos.peso_presenca)
        ) >= 65 then 'C'
        when (
            (base.score_crescimento * pesos.peso_crescimento)
            + (base.score_qualidade * pesos.peso_qualidade)
            + (base.score_estabilidade * pesos.peso_estabilidade)
            + (base.score_presenca * pesos.peso_presenca)
        ) >= 50 then 'D'
        else 'E'
    end::text as rating,
    pesos.versao_score
from base
cross join pesos
