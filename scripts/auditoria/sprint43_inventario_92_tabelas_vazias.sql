-- Sprint 43 — inventário das tabelas em api_ans / consumo_ans / nucleo_ans
-- Saída: schema|tabela|n_live_tup_estimado|tamanho_bytes
-- Usar como base; count(*) real é feito pelo orquestrador Python.

\pset format unaligned
\pset fieldsep '|'
\pset tuples_only on

select
    schemaname                                                  as schema,
    relname                                                     as tabela,
    n_live_tup                                                  as n_live_tup_estimado,
    pg_total_relation_size(format('%I.%I', schemaname, relname)) as tamanho_bytes
from pg_stat_user_tables
where schemaname in ('api_ans', 'consumo_ans', 'nucleo_ans')
order by schemaname, relname;
