-- Sprint 41: Delta ANS 100% — Grants de acesso para roles de serviço
-- Usa GRANT ON ALL TABLES (seguro mesmo com schemas vazios) +
-- ALTER DEFAULT PRIVILEGES (cobre tabelas criadas pelo dbt após este script).

-- api_ans: lido pela API FastAPI
GRANT USAGE ON SCHEMA api_ans TO healthintel_api_user;
GRANT SELECT ON ALL TABLES IN SCHEMA api_ans TO healthintel_api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA api_ans
    GRANT SELECT ON TABLES TO healthintel_api_user;

-- consumo_ans: lido por clientes BI
GRANT USAGE ON SCHEMA consumo_ans TO healthintel_consumo_user;
GRANT SELECT ON ALL TABLES IN SCHEMA consumo_ans TO healthintel_consumo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA consumo_ans
    GRANT SELECT ON TABLES TO healthintel_consumo_user;

-- consumo_ans: acesso premium
GRANT USAGE ON SCHEMA consumo_ans TO healthintel_premium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA consumo_ans TO healthintel_premium_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA consumo_ans
    GRANT SELECT ON TABLES TO healthintel_premium_user;
