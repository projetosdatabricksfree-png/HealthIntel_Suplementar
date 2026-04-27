{{ config(tags=['api', 'premium', 'documento']) }}

select *
from {{ ref('api_premium_quality_dataset') }}
where quality_score_documental < 0
   or quality_score_documental > 100
   or taxa_valido < 0
   or taxa_valido > 1
