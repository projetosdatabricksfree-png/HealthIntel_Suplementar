with contagens as (
    select 'api_operadora' as modelo, count(*) as total from {{ ref('api_operadora') }}
    union all select 'api_produto_plano', count(*) from {{ ref('api_produto_plano') }}
    union all select 'api_historico_plano', count(*) from {{ ref('api_historico_plano') }}
    union all select 'api_tuss_procedimento_vigente', count(*) from {{ ref('api_tuss_procedimento_vigente') }}
    union all select 'api_prata_idss', count(*) from {{ ref('api_prata_idss') }}
    union all select 'api_prata_igr', count(*) from {{ ref('api_prata_igr') }}
    union all select 'api_prata_nip', count(*) from {{ ref('api_prata_nip') }}
    union all select 'api_prata_diops', count(*) from {{ ref('api_prata_diops') }}
    union all select 'api_prata_financeiro_periodo', count(*) from {{ ref('api_prata_financeiro_periodo') }}
    union all select 'api_glosa_operadora_mensal', count(*) from {{ ref('api_glosa_operadora_mensal') }}
    union all select 'api_prudencial_operadora_trimestral', count(*) from {{ ref('api_prudencial_operadora_trimestral') }}
    union all select 'api_regime_especial_operadora_trimestral', count(*) from {{ ref('api_regime_especial_operadora_trimestral') }}
    union all select 'api_taxa_resolutividade_operadora_trimestral', count(*) from {{ ref('api_taxa_resolutividade_operadora_trimestral') }}
)

select *
from contagens
where total = 0
