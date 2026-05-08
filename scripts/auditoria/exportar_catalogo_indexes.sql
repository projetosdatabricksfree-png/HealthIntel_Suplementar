\copy (
    with scoped_schemas(schema_name) as (
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
        tn.nspname as table_schema,
        tbl.relname as table_name,
        in_nsp.nspname as index_schema,
        idx.relname as index_name,
        i.indisunique as is_unique,
        i.indisprimary as is_primary,
        i.indisvalid as is_valid,
        pg_catalog.pg_get_indexdef(idx.oid) as index_definition
    from pg_catalog.pg_index as i
    inner join pg_catalog.pg_class as idx
        on idx.oid = i.indexrelid
    inner join pg_catalog.pg_namespace as in_nsp
        on in_nsp.oid = idx.relnamespace
    inner join pg_catalog.pg_class as tbl
        on tbl.oid = i.indrelid
    inner join pg_catalog.pg_namespace as tn
        on tn.oid = tbl.relnamespace
    inner join scoped_schemas as s
        on s.schema_name = tn.nspname
    order by
        table_schema,
        table_name,
        index_name
) to :'output_file' with (format csv, header true)
