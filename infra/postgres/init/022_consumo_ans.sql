create schema if not exists consumo_ans;

do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'healthintel_cliente_reader') then
        create role healthintel_cliente_reader nologin;
    end if;
end
$$;

grant usage on schema consumo_ans to healthintel_cliente_reader;
grant select on all tables in schema consumo_ans to healthintel_cliente_reader;
alter default privileges in schema consumo_ans
    grant select on tables to healthintel_cliente_reader;

revoke all on schema bruto_ans from healthintel_cliente_reader;
revoke all on schema stg_ans from healthintel_cliente_reader;
revoke all on schema int_ans from healthintel_cliente_reader;
revoke all on schema nucleo_ans from healthintel_cliente_reader;
revoke all on schema plataforma from healthintel_cliente_reader;

revoke all on all tables in schema bruto_ans from healthintel_cliente_reader;
revoke all on all tables in schema stg_ans from healthintel_cliente_reader;
revoke all on all tables in schema int_ans from healthintel_cliente_reader;
revoke all on all tables in schema nucleo_ans from healthintel_cliente_reader;
revoke all on all tables in schema plataforma from healthintel_cliente_reader;

revoke all on all sequences in schema bruto_ans from healthintel_cliente_reader;
revoke all on all sequences in schema stg_ans from healthintel_cliente_reader;
revoke all on all sequences in schema int_ans from healthintel_cliente_reader;
revoke all on all sequences in schema nucleo_ans from healthintel_cliente_reader;
revoke all on all sequences in schema plataforma from healthintel_cliente_reader;
