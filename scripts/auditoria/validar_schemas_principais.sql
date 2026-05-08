drop table if exists auditoria_validacao_schemas;

create temp table auditoria_validacao_schemas as
with required_schemas(schema_name) as (
    values
        ('bruto_ans'),
        ('stg_ans'),
        ('int_ans'),
        ('nucleo_ans'),
        ('api_ans'),
        ('consumo_ans'),
        ('consumo_premium_ans'),
        ('ref_ans'),
        ('plataforma')
)
select
    case when n.oid is null then 'FAIL' else 'PASS' end as severity,
    'schema_exists' as check_type,
    r.schema_name,
    (n.oid is not null) as exists,
    case
        when n.oid is null then 'schema obrigatorio ausente'
        else 'schema obrigatorio existe'
    end as message
from required_schemas as r
left join pg_catalog.pg_namespace as n
    on n.nspname = r.schema_name;

\o :output_file
copy (
    select *
    from auditoria_validacao_schemas
    order by schema_name
) to stdout with (format csv, header true);
\o
