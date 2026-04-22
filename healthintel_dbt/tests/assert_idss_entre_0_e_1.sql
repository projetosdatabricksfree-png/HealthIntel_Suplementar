select *
from {{ ref('stg_idss') }}
where idss_total < 0
   or idss_total > 1
   or idqs < 0
   or idqs > 1
   or idga < 0
   or idga > 1
   or idsm < 0
   or idsm > 1
   or idgr < 0
   or idgr > 1
