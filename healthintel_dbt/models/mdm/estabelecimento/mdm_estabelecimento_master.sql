{{
    config(
        tags=['mdm', 'estabelecimento', 'master']
    )
}}

with validacao as (
    select
        cnes_normalizado,
        cnpj_normalizado,
        cnes_formato_valido,
        documento_quality_status,
        row_number() over (partition by cnes_normalizado order by competencia desc) as rn_val
    from {{ ref('dq_cnes_documento') }}
    where cnes_normalizado is not null
),

cnes as (
    select
        lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0') as cnes_join,
        razao_social,
        nome_fantasia,
        cd_municipio,
        sg_uf,
        situacao,
        row_number() over (partition by lpad(regexp_replace(cast(cnes as text), '[^0-9]', '', 'g'), 7, '0') order by competencia desc) as rn_cnes
    from {{ ref('stg_cnes_estabelecimento') }}
),

unificada as (
    select
        v.cnes_normalizado as cnes_canonico,
        v.cnpj_normalizado as cnpj_canonico,
        c.razao_social as razao_social_canonica,
        c.nome_fantasia as nome_fantasia_canonico,
        c.cd_municipio as cd_municipio_canonico,
        c.sg_uf as uf_canonica,
        c.situacao as situacao_cnes_canonica,
        coalesce(v.documento_quality_status, 'NULO') as documento_quality_status,
        case
            when v.cnes_formato_valido = true and coalesce(v.documento_quality_status, 'NULO') in ('VALIDO', 'SEQUENCIA_INVALIDA', 'INVALIDO_FORMATO', 'INVALIDO_DIGITO') then 'ATIVO'
            else 'QUARANTENA'
        end as status_mdm,
        case
            when v.cnes_formato_valido = true and v.documento_quality_status = 'VALIDO' then 100
            when v.cnes_formato_valido = true then 50
            else 20
        end as confidence_score
    from cnes as c
    inner join validacao as v on c.cnes_join = v.cnes_normalizado and v.rn_val = 1
    where c.rn_cnes = 1
)

select
    md5(concat_ws('|', 'estabelecimento', cnes_canonico, coalesce(cnpj_canonico, ''))) as estabelecimento_master_id,
    cnes_canonico,
    cnpj_canonico,
    razao_social_canonica,
    nome_fantasia_canonico,
    cd_municipio_canonico,
    uf_canonica,
    situacao_cnes_canonica,
    documento_quality_status,
    status_mdm,
    confidence_score,
    current_timestamp as mdm_created_at,
    current_timestamp as mdm_updated_at
from unificada
