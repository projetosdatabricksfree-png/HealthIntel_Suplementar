with totalizacao as (
    select
        cd_municipio,
        competencia,
        round(sum(market_share_pct), 2) as soma_market_share
    from {{ ref('fat_market_share_mensal') }}
    group by cd_municipio, competencia
)

select *
from totalizacao
where abs(soma_market_share - 100) > 0.5
