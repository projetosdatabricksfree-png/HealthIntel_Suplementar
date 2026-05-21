-- Sprint 45 — Fix: portal não conseguia criar chave (NotNullViolationError em chave_api.id)
-- Aditivo: só seta DEFAULT na PK; não toca colunas existentes nem dados.
-- gen_random_uuid() já é usada em 072_sprint44_portal_real.sql (assinatura.id).

alter table plataforma.chave_api
    alter column id set default gen_random_uuid();
