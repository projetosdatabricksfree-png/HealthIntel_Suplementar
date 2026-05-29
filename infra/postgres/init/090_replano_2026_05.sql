-- Replano 2026-05 — Nova tabela de cotas + ciclo anual + enterprise pay-as-you-go
-- Aditivo: adiciona colunas em plataforma.plano, cria plataforma.trial_pro, UPDATE valores.
-- Decisões: cotas drásticamente reduzidas, FREE com cap mensal, trial PRO 14 dias,
-- ciclo anual com "2 meses grátis" (16,7% off), ENTERPRISE pay-as-you-go com mínimo R$5.000.

-- -----------------------------------------------------------------------
-- 1. Novas colunas em plataforma.plano
-- -----------------------------------------------------------------------
alter table if exists plataforma.plano
    add column if not exists preco_anual_centavos integer not null default 0,
    add column if not exists stripe_price_id_mensal text,
    add column if not exists stripe_price_id_anual text,
    add column if not exists limite_req_mes integer not null default 0,
    add column if not exists minimo_mensal_centavos integer not null default 0,
    add column if not exists modelo_cobranca text not null default 'flat';

-- CHECK constraint para modelo_cobranca (idempotente)
do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'plano_modelo_cobranca_check'
    ) then
        alter table plataforma.plano
            add constraint plano_modelo_cobranca_check
            check (modelo_cobranca in ('flat', 'franquia_overage', 'pay_as_you_go'));
    end if;
end$$;

-- -----------------------------------------------------------------------
-- 2. plataforma.trial_pro — 1 trial PRO de 14 dias por cliente (PK previne 2º trial)
-- -----------------------------------------------------------------------
create table if not exists plataforma.trial_pro (
    cliente_id uuid primary key references plataforma.cliente(id) on delete cascade,
    inicio_em timestamptz not null default now(),
    expira_em timestamptz not null,
    consumido boolean not null default false,
    motivo_consumo text,
    criado_em timestamptz not null default now()
);

create index if not exists ix_trial_pro_expira
    on plataforma.trial_pro (expira_em) where consumido = false;

comment on table plataforma.trial_pro is
    'Trial PRO de 14 dias auto-provisionado ao cadastro FREE. Quando ativo (now() < expira_em AND consumido=false), middleware aplica limites do plano PRO em vez do FREE.';

-- -----------------------------------------------------------------------
-- 3. UPDATE de planos canônicos com a nova tabela
--    FREE:       100/mês (sem cap diário), 0 reais
--    STARTER:    500/dia, R$ 99,99/mês ou R$ 999,90/ano (2 meses grátis)
--    PRO:        2.500/dia, R$ 499/mês ou R$ 4.990/ano
--    MAX:        25.000/dia, R$ 1.499/mês ou R$ 14.990/ano
--    ENTERPRISE: pay-as-you-go, mínimo R$ 5.000/mês + R$ 50/mil req
-- -----------------------------------------------------------------------

-- FREE: cap mensal 100, sem cap diário
update plataforma.plano set
    limite_req_dia = 0,
    limite_req_mes = 100,
    preco_base_centavos = 0,
    preco_anual_centavos = 0,
    franquia_requisicoes_mes = 100,
    preco_excedente_mil_requisicoes_centavos = 0,
    modelo_cobranca = 'flat',
    descricao = 'Plano gratuito para avaliação. 100 requisições/mês após 14 dias de trial PRO.'
where nome = 'free';

-- STARTER: 500 req/dia + ciclo anual
update plataforma.plano set
    limite_req_dia = 500,
    limite_req_mes = 0,
    preco_base_centavos = 9999,
    preco_anual_centavos = 99990,
    franquia_requisicoes_mes = 15000,
    preco_excedente_mil_requisicoes_centavos = 3500,
    modelo_cobranca = 'flat',
    descricao = 'Validação técnica e integração inicial — 500 req/dia.'
where nome = 'starter';

-- PRO: 2.500 req/dia + ciclo anual
update plataforma.plano set
    limite_req_dia = 2500,
    limite_req_mes = 0,
    preco_base_centavos = 49900,
    preco_anual_centavos = 499000,
    franquia_requisicoes_mes = 75000,
    preco_excedente_mil_requisicoes_centavos = 3000,
    modelo_cobranca = 'flat',
    descricao = 'Produção padrão para BI e produtos digitais — 2.500 req/dia.'
where nome = 'pro';

-- MAX: 25.000 req/dia + ciclo anual
update plataforma.plano set
    limite_req_dia = 25000,
    limite_req_mes = 0,
    preco_base_centavos = 149900,
    preco_anual_centavos = 1499000,
    franquia_requisicoes_mes = 750000,
    preco_excedente_mil_requisicoes_centavos = 2500,
    modelo_cobranca = 'flat',
    descricao = 'Alto volume self-service para healthtechs e operadoras — 25.000 req/dia.'
where nome = 'max';

-- ENTERPRISE: pay-as-you-go, sem cap diário
update plataforma.plano set
    limite_req_dia = 0,
    limite_req_mes = 0,
    preco_base_centavos = 0,
    preco_anual_centavos = 0,
    minimo_mensal_centavos = 500000,
    franquia_requisicoes_mes = 500000,
    preco_excedente_mil_requisicoes_centavos = 5000,
    modelo_cobranca = 'pay_as_you_go',
    descricao = 'Plano enterprise pay-as-you-go — mínimo R$5.000/mês + R$50 por mil req acima.'
where nome = 'enterprise';

-- -----------------------------------------------------------------------
-- 4. Auditoria do replano (idempotente — só insere se ainda não existe)
-- -----------------------------------------------------------------------
insert into plataforma.auditoria_cobranca (id, evento, ator, origem, payload, criado_em)
select
    gen_random_uuid(),
    'replano_2026_05',
    'sistema',
    'bootstrap_090',
    jsonb_build_object(
        'sprint', 'replano_2026_05',
        'descricao', 'Nova tabela de cotas + ciclo anual + enterprise pay-as-you-go',
        'planos_alterados', array['free','starter','pro','max','enterprise']
    ),
    now()
where not exists (
    select 1 from plataforma.auditoria_cobranca
    where evento = 'replano_2026_05'
);
