select vazios.cd_municipio
from {{ ref('fat_vazio_assistencial_municipio') }} as vazios
left join {{ ref('ref_municipio_ibge') }} as municipio
    on lpad(cast(municipio.codigo_ibge as text), 7, '0') = vazios.cd_municipio
where municipio.codigo_ibge is null
