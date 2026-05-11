{{
    config(
        tags=['mdm', 'prestador', 'master']
    )
}}

with cnes as (
    select
        cnes_canonico,
        cnpj_canonico,
        estabelecimento_master_id,
        razao_social_canonica,
        cd_municipio_canonico,
        uf_canonica,
        documento_quality_status,
        status_mdm,
        confidence_score
    from {{ ref('mdm_estabelecimento_master') }}
),

stg as (
    select
        lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0') as cnes_join,
        tipo_unidade_desc,
        row_number() over (partition by lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0') order by competencia desc) as rn_cnes
    from {{ ref('stg_cnes_estabelecimento') }}
),

unificada as (
    select
        coalesce(c.cnpj_canonico, c.cnes_canonico) as chave_publica_principal,
        c.estabelecimento_master_id,
        c.cnes_canonico,
        c.cnpj_canonico,
        c.razao_social_canonica as nome_prestador_canonico,
        s.tipo_unidade_desc as tipo_prestador_canonico,
        c.cd_municipio_canonico,
        c.uf_canonica,
        c.documento_quality_status,
        c.status_mdm,
        c.confidence_score
    from cnes as c
    left join stg as s on c.cnes_canonico = s.cnes_join and s.rn_cnes = 1
)

select
    md5(concat_ws('|', 'prestador', chave_publica_principal, coalesce(estabelecimento_master_id, ''))) as prestador_master_id,
    estabelecimento_master_id,
    null::text as operadora_master_id, -- Link com operadora será feito via rede credenciada futuramente
    cnes_canonico,
    cnpj_canonico,
    nome_prestador_canonico,
    tipo_prestador_canonico,
    cd_municipio_canonico,
    uf_canonica,
    documento_quality_status,
    status_mdm,
    confidence_score,
    current_timestamp as mdm_created_at,
    current_timestamp as mdm_updated_at
from unificada
