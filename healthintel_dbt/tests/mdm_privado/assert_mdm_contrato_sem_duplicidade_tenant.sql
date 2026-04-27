{{ config(tags=['mdm_privado'], severity='error') }}

-- Chave canônica do master deve ser única: (tenant_id, numero_contrato_normalizado).

select tenant_id, numero_contrato_normalizado, count(*) as qtd
from {{ ref('mdm_contrato_master') }}
group by tenant_id, numero_contrato_normalizado
having count(*) > 1
