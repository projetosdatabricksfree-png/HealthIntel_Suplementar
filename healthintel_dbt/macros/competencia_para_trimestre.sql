{% macro competencia_para_trimestre(campo) -%}
    case substr({{ campo }}, 5, 2)
        when '01' then substr({{ campo }}, 1, 4) || 'T1'
        when '02' then substr({{ campo }}, 1, 4) || 'T1'
        when '03' then substr({{ campo }}, 1, 4) || 'T1'
        when '04' then substr({{ campo }}, 1, 4) || 'T2'
        when '05' then substr({{ campo }}, 1, 4) || 'T2'
        when '06' then substr({{ campo }}, 1, 4) || 'T2'
        when '07' then substr({{ campo }}, 1, 4) || 'T3'
        when '08' then substr({{ campo }}, 1, 4) || 'T3'
        when '09' then substr({{ campo }}, 1, 4) || 'T3'
        when '10' then substr({{ campo }}, 1, 4) || 'T4'
        when '11' then substr({{ campo }}, 1, 4) || 'T4'
        when '12' then substr({{ campo }}, 1, 4) || 'T4'
        else null
    end
{%- endmacro %}
