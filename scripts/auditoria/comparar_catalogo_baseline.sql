\copy (
    with baseline as (
        select
            table_schema,
            table_name,
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            ordinal_position::integer as ordinal_position
        from auditoria_baseline_schema
    ),
    current_catalog as (
        select
            table_schema,
            table_name,
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            ordinal_position::integer as ordinal_position
        from auditoria_catalogo_schema_atual
    ),
    joined as (
        select
            b.table_schema,
            b.table_name,
            b.column_name,
            b.data_type as expected_data_type,
            c.data_type as actual_data_type,
            b.udt_name as expected_udt_name,
            c.udt_name as actual_udt_name,
            b.is_nullable as expected_is_nullable,
            c.is_nullable as actual_is_nullable,
            b.column_default as expected_column_default,
            c.column_default as actual_column_default,
            b.ordinal_position as expected_ordinal_position,
            c.ordinal_position as actual_ordinal_position,
            c.column_name is not null as column_exists
        from baseline as b
        left join current_catalog as c
            on c.table_schema = b.table_schema
            and c.table_name = b.table_name
            and c.column_name = b.column_name
    )
    select
        'FAIL' as severity,
        'missing_column' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'coluna presente no baseline local e ausente no banco auditado' as message
    from joined
    where not column_exists

    union all

    select
        'FAIL' as severity,
        'data_type_mismatch' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'tipo logico da coluna diverge do baseline local' as message
    from joined
    where column_exists
        and expected_data_type is distinct from actual_data_type

    union all

    select
        'FAIL' as severity,
        'udt_name_mismatch' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'udt_name da coluna diverge do baseline local' as message
    from joined
    where column_exists
        and expected_udt_name is distinct from actual_udt_name

    union all

    select
        'FAIL' as severity,
        'is_nullable_mismatch' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'nulidade da coluna diverge do baseline local' as message
    from joined
    where column_exists
        and expected_is_nullable is distinct from actual_is_nullable

    union all

    select
        'FAIL' as severity,
        'column_default_mismatch' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'default da coluna diverge do baseline local' as message
    from joined
    where column_exists
        and expected_column_default is distinct from actual_column_default

    union all

    select
        'WARN' as severity,
        'ordinal_position_mismatch' as check_type,
        table_schema,
        table_name,
        column_name,
        expected_data_type,
        actual_data_type,
        expected_udt_name,
        actual_udt_name,
        expected_is_nullable,
        actual_is_nullable,
        expected_column_default,
        actual_column_default,
        expected_ordinal_position,
        actual_ordinal_position,
        'posicao ordinal da coluna diverge do baseline local' as message
    from joined
    where column_exists
        and expected_ordinal_position is distinct from actual_ordinal_position

    order by
        severity,
        check_type,
        table_schema,
        table_name,
        column_name
) to :'output_file' with (format csv, header true)
