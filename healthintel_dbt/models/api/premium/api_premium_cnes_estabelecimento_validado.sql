{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'competencia') }}",
            "{{ criar_indice_api(this, 'cnes_normalizado') }}",
            "{{ criar_indice_api(this, 'cd_municipio') }}",
            "{{ criar_indice_api(this, 'sg_uf') }}"
        ]
    )
}}

with validado as (
    select
        competencia,
        cnes,
        cnes_normalizado,
        cnpj_normalizado,
        razao_social,
        nome_fantasia,
        sg_uf,
        cd_municipio,
        nm_municipio,
        tipo_unidade,
        tipo_unidade_desc,
        cnes_formato_valido,
        cnpj_digito_valido,
        documento_quality_status,
        motivo_invalidade_documento,
        row_number() over (
            partition by competencia, cnes_normalizado
            order by _carregado_em desc nulls last, _lote_id desc nulls last
        ) as rn
    from {{ ref('dq_cnes_documento') }}
    where documento_quality_status = 'VALIDO'
      and cnes_formato_valido
      and cnpj_digito_valido
)

select
    competencia,
    cnes,
    cnes_normalizado,
    cnpj_normalizado,
    razao_social,
    nome_fantasia,
    sg_uf,
    cd_municipio,
    nm_municipio,
    tipo_unidade,
    tipo_unidade_desc,
    cnes_formato_valido,
    cnpj_digito_valido,
    documento_quality_status,
    motivo_invalidade_documento,
    100::numeric(5, 2) as quality_score_cnes
from validado
where rn = 1
