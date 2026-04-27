{{ config(tags=['mdm_privado'], severity='error') }}

-- Chave canônica do master de subfatura deve ser única:
-- (tenant_id, numero_contrato_normalizado, codigo_subfatura_normalizado).
-- Duplicidade adicional por competência é tratada como WARNING via mdm_subfatura_exception.

select tenant_id, numero_contrato_normalizado, codigo_subfatura_normalizado, count(*) as qtd
from {{ ref('mdm_subfatura_master') }}
group by tenant_id, numero_contrato_normalizado, codigo_subfatura_normalizado
having count(*) > 1
