{{ config(tags=['consumo_premium', 'premium', 'tiss']) }}

select *
from {{ ref('consumo_premium_tiss_procedimento_tuss_validado') }}
where cd_procedimento_tuss is null
   or operadora_master_id is null
   or procedimento_quality_status <> 'VALIDO'
   or quality_score_procedimento < 0
   or quality_score_procedimento > 100
