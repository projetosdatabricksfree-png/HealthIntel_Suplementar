{% macro trimestre_para_competencia(campo) -%}
    case right({{ campo }}, 1)
        when '1' then substr({{ campo }}, 1, 4) || '03'
        when '2' then substr({{ campo }}, 1, 4) || '06'
        when '3' then substr({{ campo }}, 1, 4) || '09'
        when '4' then substr({{ campo }}, 1, 4) || '12'
        else null
    end
{%- endmacro %}
