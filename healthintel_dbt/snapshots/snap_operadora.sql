{% snapshot snap_operadora %}
{{
    config(
        target_schema='nucleo_ans',
        unique_key='registro_ans',
        strategy='check',
        check_cols=['nome', 'nome_fantasia', 'modalidade', 'uf_sede', 'municipio_sede', 'cnpj']
    )
}}

select * from {{ ref('stg_cadop') }}

{% endsnapshot %}
