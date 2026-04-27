with total_dim as (
    select count(*) as total from {{ ref('dim_operadora_atual') }}
),

total_mdm as (
    select count(*) as total from {{ ref('mdm_operadora_master') }}
)

select
    t_dim.total as total_operadoras_dim,
    t_mdm.total as total_operadoras_mdm,
    cast(t_mdm.total as float) / nullif(t_dim.total, 0) as taxa_cobertura
from total_dim t_dim
cross join total_mdm t_mdm
where (cast(t_mdm.total as float) / nullif(t_dim.total, 0)) < 0.95
