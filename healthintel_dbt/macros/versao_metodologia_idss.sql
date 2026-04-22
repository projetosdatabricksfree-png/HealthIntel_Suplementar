{% macro versao_metodologia_idss(ano_base) -%}
    case
        when cast({{ ano_base }} as integer) <= 2014 then 'v1_faixas'
        when cast({{ ano_base }} as integer) <= 2019 then 'v2_notas'
        when cast({{ ano_base }} as integer) <= 2021 then 'v3_dimensoes'
        else 'v4_rn505'
    end
{%- endmacro %}
