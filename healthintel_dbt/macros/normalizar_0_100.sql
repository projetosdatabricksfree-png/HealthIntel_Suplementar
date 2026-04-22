{% macro normalizar_0_100(expressao, minimo=0, maximo=100) -%}
    case
        when {{ expressao }} is null then null
        when {{ maximo }} = {{ minimo }} then 0
        else least(
            greatest(
                round(
                    ((({{ expressao }} - {{ minimo }}) / nullif(({{ maximo }} - {{ minimo }}), 0)) * 100)::numeric,
                    2
                ),
                0
            ),
            100
        )
    end
{%- endmacro %}
