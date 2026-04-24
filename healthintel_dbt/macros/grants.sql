{% macro grant_select_to_cliente_reader() %}
    grant select on {{ this }} to healthintel_cliente_reader;
{% endmacro %}
