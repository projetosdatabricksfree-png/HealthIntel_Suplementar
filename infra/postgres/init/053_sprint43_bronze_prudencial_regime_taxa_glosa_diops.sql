-- Sprint 43: compatibility guard for existing bronze delta ANS tables.
--
-- The canonical tables are created by earlier migrations:
-- - bruto_ans.prudencial_operadora_trimestral
-- - bruto_ans.regime_especial_operadora_trimestral
-- - bruto_ans.taxa_resolutividade_operadora_trimestral
-- - bruto_ans.glosa_operadora_mensal
-- - bruto_ans.diops_operadora_trimestral
--
-- Keep this migration intentionally non-duplicative. Creating alternate table
-- names here would desynchronize dbt sources, ingestion DATASET_CONFIG and API
-- models.

create index if not exists ix_prudencial_operadora_trimestral_registro_s43
    on bruto_ans.prudencial_operadora_trimestral (registro_ans, trimestre desc);

create index if not exists ix_regime_especial_operadora_trimestral_registro_s43
    on bruto_ans.regime_especial_operadora_trimestral (registro_ans, trimestre desc);

create index if not exists ix_taxa_resolutividade_operadora_trimestral_registro_s43
    on bruto_ans.taxa_resolutividade_operadora_trimestral (registro_ans, trimestre desc);

create index if not exists ix_glosa_operadora_mensal_registro_s43
    on bruto_ans.glosa_operadora_mensal (registro_ans, competencia desc);

create index if not exists ix_diops_operadora_trimestral_registro_s43
    on bruto_ans.diops_operadora_trimestral (registro_ans, trimestre desc);

do $$
begin
    if exists (select 1 from pg_roles where rolname = 'healthintel_api') then
        grant select on
            bruto_ans.prudencial_operadora_trimestral,
            bruto_ans.regime_especial_operadora_trimestral,
            bruto_ans.taxa_resolutividade_operadora_trimestral,
            bruto_ans.glosa_operadora_mensal,
            bruto_ans.diops_operadora_trimestral
        to healthintel_api;
    end if;
end
$$;
