select *
from {{ ref('fat_beneficiario_operadora') }}
where coalesce(qt_beneficiario_ativo, 0) < 0
