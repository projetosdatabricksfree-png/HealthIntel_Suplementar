select
    operadora.operadora_id,
    idss.registro_ans,
    idss.ano_base,
    idss.idss_total,
    idss.idqs,
    idss.idga,
    idss.idsm,
    idss.idgr,
    idss.faixa_idss,
    idss.versao_metodologia,
    greatest(0, least(1, idss.idss_total))::numeric(6,4) as idss_total_normalizado,
    greatest(0, least(1, idss.idqs))::numeric(6,4) as idqs_normalizado,
    greatest(0, least(1, idss.idga))::numeric(6,4) as idga_normalizado,
    greatest(0, least(1, idss.idsm))::numeric(6,4) as idsm_normalizado,
    greatest(0, least(1, idss.idgr))::numeric(6,4) as idgr_normalizado
from {{ ref('stg_idss') }} as idss
inner join {{ ref('dim_operadora_atual') }} as operadora
    on idss.registro_ans = operadora.registro_ans
