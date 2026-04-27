{{
    config(
        tags=['mdm', 'operadora', 'master']
    )
}}

with validacao as (
    select
        registro_ans,
        registro_ans_normalizado,
        cnpj_normalizado,
        documento_quality_status
    from {{ ref('dq_cadop_documento') }}
    where registro_ans_formato_valido = true
),

operadora as (
    select
        registro_ans,
        nome,
        nome_fantasia,
        modalidade,
        uf_sede,
        municipio_sede,
        cnpj as cnpj_original
    from {{ ref('dim_operadora_atual') }}
),

unificada as (
    select
        o.registro_ans as registro_ans_canonico,
        v.cnpj_normalizado as cnpj_canonico,
        o.nome as razao_social_canonica,
        o.nome_fantasia as nome_fantasia_canonico,
        o.modalidade as modalidade_canonica,
        o.uf_sede as uf_canonica,
        o.municipio_sede as municipio_sede_canonico,
        coalesce(v.documento_quality_status, 'NULO') as documento_quality_status,
        case
            when v.documento_quality_status = 'VALIDO' then 'ATIVO'
            else 'QUARANTENA'
        end as status_mdm,
        case
            when v.documento_quality_status = 'VALIDO' then 100
            when v.cnpj_normalizado is null then 50
            else 20
        end as confidence_score
    from operadora o
    left join validacao v on o.registro_ans = v.registro_ans
)

select
    md5(concat_ws('|', 'operadora', registro_ans_canonico, coalesce(cnpj_canonico, ''))) as operadora_master_id,
    registro_ans_canonico,
    cnpj_canonico,
    razao_social_canonica,
    nome_fantasia_canonico,
    modalidade_canonica,
    uf_canonica,
    municipio_sede_canonico,
    documento_quality_status,
    status_mdm,
    confidence_score,
    current_timestamp as mdm_created_at,
    current_timestamp as mdm_updated_at
from unificada
