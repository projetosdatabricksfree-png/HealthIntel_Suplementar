{{
    config(
        post_hook=[
            "{{ criar_indice_api(this, 'fonte_documento') }}",
            "{{ criar_indice_api(this, 'documento_quality_status') }}"
        ]
    )
}}

select
    fonte_documento,
    documento_quality_status,
    total_registro,
    total_fonte,
    total_valido,
    total_invalido,
    taxa_valido,
    quality_score_documental
from {{ ref('consumo_premium_quality_dataset') }}
