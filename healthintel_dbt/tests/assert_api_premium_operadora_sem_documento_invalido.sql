{{ config(tags=['api', 'premium', 'documento']) }}

select *
from {{ ref('api_premium_operadora_360_validado') }}
where documento_quality_status <> 'VALIDO'
   or not registro_ans_formato_valido
   or not cnpj_digito_valido
   or quality_score_documental < 0
   or quality_score_documental > 100
