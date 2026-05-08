\copy (
    select
        c.table_schema,
        c.table_name,
        c.column_name,
        c.data_type,
        c.udt_name,
        c.is_nullable,
        c.column_default,
        c.ordinal_position
    from information_schema.columns as c
    where c.table_schema in (
        'bruto_ans',
        'stg_ans',
        'int_ans',
        'nucleo_ans',
        'api_ans',
        'consumo_ans',
        'consumo_premium_ans',
        'ref_ans',
        'plataforma'
    )
    order by
        c.table_schema,
        c.table_name,
        c.ordinal_position
) to :'output_file' with (format csv, header true)
