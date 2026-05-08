drop table if exists auditoria_objetos_dbt_faltantes;

create temp table auditoria_objetos_dbt_faltantes as
select
    case
        when e.schema_name not in (
            'bruto_ans',
            'stg_ans',
            'int_ans',
            'nucleo_ans',
            'api_ans',
            'consumo_ans',
            'consumo_premium_ans',
            'ref_ans',
            'plataforma'
        ) then 'WARN'
        else 'FAIL'
    end as severity,
    'missing_dbt_relation' as check_type,
    e.database_name,
    e.schema_name,
    e.object_name,
    e.resource_type,
    e.materialized,
    e.original_file_path,
    e.tags,
    e.unique_id,
    case
        when e.schema_name not in (
            'bruto_ans',
            'stg_ans',
            'int_ans',
            'nucleo_ans',
            'api_ans',
            'consumo_ans',
            'consumo_premium_ans',
            'ref_ans',
            'plataforma'
        ) then 'objeto dbt ausente em schema fora do escopo principal'
        else 'objeto dbt esperado ausente no banco'
    end as message
from auditoria_objetos_dbt_esperados as e
left join pg_catalog.pg_namespace as n
    on n.nspname = e.schema_name
left join pg_catalog.pg_class as c
    on c.relnamespace = n.oid
    and c.relname = e.object_name
    and c.relkind in ('r', 'p', 'v', 'm', 'f')
where c.oid is null;

\o :output_file
copy (
    select *
    from auditoria_objetos_dbt_faltantes
    order by
        severity,
        schema_name,
        object_name
) to stdout with (format csv, header true);
\o
