{{ config(tags=['quality', 'documento', 'consumo_premium']) }}

/*
  Guarda antecipada da Sprint 27. A camada consumo_premium_ans ainda pertence
  a sprint futura; enquanto ela nao existir, este teste deve retornar zero linhas.
*/
select
    table_schema,
    table_name
from information_schema.tables
where table_schema = 'consumo_premium_ans'
  and table_name like 'consumo_premium_%'
  and false

