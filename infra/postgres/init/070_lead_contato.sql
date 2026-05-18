-- 070_lead_contato.sql
-- Cria tabela plataforma.lead_contato para persistir leads do formulário
-- público do site institucional. Idempotente.

CREATE SCHEMA IF NOT EXISTS plataforma;

CREATE TABLE IF NOT EXISTS plataforma.lead_contato (
    id          uuid PRIMARY KEY,
    criado_em   timestamptz NOT NULL DEFAULT NOW(),
    nome        text NOT NULL,
    email       text NOT NULL,
    empresa     text NOT NULL,
    perfil      text NOT NULL,
    plano       text,
    mensagem    text NOT NULL,
    origem      text,
    ip_origem   inet
);

CREATE INDEX IF NOT EXISTS idx_lead_contato_criado_em
    ON plataforma.lead_contato (criado_em DESC);

CREATE INDEX IF NOT EXISTS idx_lead_contato_email
    ON plataforma.lead_contato (lower(email));

COMMENT ON TABLE plataforma.lead_contato IS
    'Leads comerciais recebidos pelo formulário do site institucional HealthIntel.';
