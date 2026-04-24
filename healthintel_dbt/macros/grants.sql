{% macro grant_select_to_cliente_reader() %}
    {% if target.name == 'prod' %}
        grant select on {{ this }} to "healthintel_reader";
    {% endif %}
{% endmacro %}
