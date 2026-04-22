{% macro criar_indices(relacao, colunas) -%}
    {% if colunas is string %}
        {% set colunas = [colunas] %}
    {% endif %}
    {% for coluna in colunas %}
        create index if not exists ix_{{ relacao.identifier }}_{{ coluna | replace(', ', '_') | replace(',', '_') | replace(' ', '_') }}
        on {{ relacao }} ({{ coluna }});
    {% endfor %}
{%- endmacro %}
