{{ config(tags=['api', 'premium']) }}

-- Teste documental em dbt: modelos api_premium materializados devem existir apenas
-- como superficie api_ans. Leitura direta pela FastAPI e validada em testes Python.
select
table_schema,
table_name
from information_schema.tables
where table_name like 'api_premium_%'
  and table_schema <> 'api_ans'
