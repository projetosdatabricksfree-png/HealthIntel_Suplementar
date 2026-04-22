{% macro calcular_hhi(expressao_participacao, particionamento) -%}
    round(
        sum(power(coalesce({{ expressao_participacao }}, 0), 2))
        over (partition by {{ particionamento }}) * 10000,
        2
    )
{%- endmacro %}
