{{
    config(
        materialized='table',
        schema='consumo_ans',
        tags=['delta_ans_100', 'sip', 'consumo'],
        post_hook="{{ grant_select_to_cliente_reader() }}"
    )
}}

select
    competencia,
    registro_ans,
    cd_municipio,
    nm_municipio,
    sg_uf,
    nm_regiao,
    tipo_assistencial,
    qt_beneficiarios,
    qt_eventos,
    indicador_cobertura_medio
from {{ ref('api_sip_assistencial_operadora') }}
