{% macro classificar_rating_regulatorio(expressao_score) -%}
    case
        when {{ expressao_score }} >= 90 then 'A'
        when {{ expressao_score }} >= 80 then 'B'
        when {{ expressao_score }} >= 65 then 'C'
        when {{ expressao_score }} >= 40 then 'D'
        else 'E'
    end
{%- endmacro %}
