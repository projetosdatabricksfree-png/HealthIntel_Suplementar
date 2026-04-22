{% macro criar_indice_api(relacao, coluna) -%}
    {% set sufixo = coluna | replace(', ', '_') | replace(',', '_') | replace(' ', '_') %}
    create index if not exists ix_{{ relacao.identifier }}_{{ sufixo }} on {{ relacao }} ({{ coluna }});
{%- endmacro %}
