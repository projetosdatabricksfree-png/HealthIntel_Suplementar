-- Sprint 45 — Alinhar plataforma.plano com o contrato comercial publicado
-- (frontend/healthintel_frontend_fase9/src/data/plans.ts e components/marketing/Pricing.tsx).
-- Aditivo: apenas UPDATEs em 5 linhas dos planos canônicos. Sem DDL, sem dados novos.

-- limite_req_dia: 0 desliga o check no middleware (api/app/middleware/rate_limit.py:21).
-- Valores espelham exatamente os exibidos na pricing pública.
update plataforma.plano set limite_req_dia = 100      where nome = 'free';
update plataforma.plano set limite_req_dia = 30000    where nome = 'starter';
update plataforma.plano set limite_req_dia = 150000   where nome = 'pro';
update plataforma.plano set limite_req_dia = 500000   where nome = 'max';
update plataforma.plano set limite_req_dia = 0        where nome = 'enterprise';  -- contratual, sem cap diário

-- limite_api_keys: cap por chaves ATIVAS, enforçado em api/app/routers/portal_api_keys.py
-- nos endpoints criar/habilitar. Alinhado com o pricing.
update plataforma.plano set limite_api_keys = 1  where nome = 'free';
update plataforma.plano set limite_api_keys = 1  where nome = 'starter';
update plataforma.plano set limite_api_keys = 3  where nome = 'pro';
update plataforma.plano set limite_api_keys = 5  where nome = 'max';
update plataforma.plano set limite_api_keys = -1 where nome = 'enterprise';  -- ilimitado
