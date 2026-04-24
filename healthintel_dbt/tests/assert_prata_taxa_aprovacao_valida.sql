{% set modelos_prata = [
    'api_prata_cadop',
    'api_prata_sib_operadora',
    'api_prata_sib_municipio',
    'api_prata_igr',
    'api_prata_nip',
    'api_prata_idss',
    'api_prata_diops',
    'api_prata_fip',
    'api_prata_vda',
    'api_prata_glosa',
    'api_prata_rede_assistencial',
    'api_prata_operadora_enriquecida',
    'api_prata_municipio_metrica',
    'api_prata_financeiro_periodo',
    'api_prata_cnes_municipio',
    'api_prata_cnes_rede_gap',
    'api_prata_tiss_procedimento'
] %}

{% for modelo in modelos_prata %}
select '{{ modelo }}' as modelo, taxa_aprovacao_lote
from {{ ref(modelo) }}
where taxa_aprovacao_lote is not null
  and (taxa_aprovacao_lote < 0 or taxa_aprovacao_lote > 1)
{% if not loop.last %}union all{% endif %}
{% endfor %}
