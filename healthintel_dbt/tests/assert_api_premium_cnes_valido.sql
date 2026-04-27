{{ config(tags=['api', 'premium', 'documento', 'cnes']) }}

select *
from {{ ref('api_premium_cnes_estabelecimento_validado') }}
where documento_quality_status <> 'VALIDO'
   or not cnes_formato_valido
   or not cnpj_digito_valido
   or quality_score_cnes < 0
   or quality_score_cnes > 100
