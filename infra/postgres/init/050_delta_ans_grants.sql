-- Sprint 41: Delta ANS 100% — Grants de acesso para roles de serviço
-- Roles existentes no projeto:
--   healthintel_cliente_reader  → consumo_ans  (criada em 022_consumo_ans.sql)
--   healthintel_premium_reader  → consumo_premium_ans (criada em 027_fase5_premium_roles.sql)
-- api_ans não tem role separada — a API FastAPI acessa pelo usuário principal.

-- consumo_ans: clientes BI
GRANT USAGE ON SCHEMA consumo_ans TO healthintel_cliente_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA consumo_ans TO healthintel_cliente_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA consumo_ans
    GRANT SELECT ON TABLES TO healthintel_cliente_reader;

-- consumo_premium_ans: clientes premium
GRANT USAGE ON SCHEMA consumo_premium_ans TO healthintel_premium_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA consumo_premium_ans TO healthintel_premium_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA consumo_premium_ans
    GRANT SELECT ON TABLES TO healthintel_premium_reader;
