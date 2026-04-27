-- Sprint 31 - superficie SQL direta premium.
-- Este bootstrap e aditivo: clientes legados continuam restritos a consumo_ans.

create schema if not exists consumo_premium_ans;

do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'healthintel_premium_reader') then
        create role healthintel_premium_reader;
    end if;
end
$$;

revoke all on schema consumo_premium_ans from public;
revoke all on schema consumo_premium_ans from healthintel_cliente_reader;

grant usage on schema consumo_premium_ans to healthintel_premium_reader;
grant select on all tables in schema consumo_premium_ans to healthintel_premium_reader;
alter default privileges in schema consumo_premium_ans
    grant select on tables to healthintel_premium_reader;

-- Superficies internas da Fase 5 nao sao produto SQL direto.
revoke all on schema quality_ans from healthintel_premium_reader;
revoke all on schema mdm_ans from healthintel_premium_reader;
revoke all on schema bruto_cliente from healthintel_premium_reader;
revoke all on schema stg_cliente from healthintel_premium_reader;
revoke all on schema mdm_privado from healthintel_premium_reader;
