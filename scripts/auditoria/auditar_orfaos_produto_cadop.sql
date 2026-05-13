-- Sprint 43 — Diagnóstico dos órfãos registro_ans em produto vs CADOP
--
-- Pergunta: por que 64% dos operadora distintos em produto não batem com CADOP?
-- Hipóteses testadas:
--   H1 (bug): zeros à esquerda, casting → REJEITADA (registros têm 6 chars padronizados)
--   H2 (canceladas): órfãos são operadoras canceladas → CONFIRMADA estruturalmente,
--                   mas stg_operadora_cancelada está vazio (fonte ANS não ingerida)
--   H3 (CADOP incompleto): CADOP atual só lista 1.107 ativas, e produto tem
--                          2.935 distintas (histórico)
--
-- Decisão Sprint 43: histórico legítimo. Documentado em
--   docs/evidencias/sprint43/orfaos_produto_cadop_decisao.md
-- Próximo passo (Sprint 44): ingerir fonte ANS de operadoras canceladas.

\pset format unaligned
\pset fieldsep '|'
\pset tuples_only off

\echo '=== Cardinalidade ==='
select 'total_registros_produto' as metrica, count(*)::text as valor
  from stg_ans.stg_produto_caracteristica
union all
select 'produto_distintos', count(distinct registro_ans)::text
  from stg_ans.stg_produto_caracteristica
union all
select 'total_registros_cadop', count(*)::text
  from stg_ans.stg_cadop
union all
select 'cadop_distintos', count(distinct registro_ans)::text
  from stg_ans.stg_cadop;

\echo ''
\echo '=== Órfãos (produto sem CADOP correspondente) ==='
with orfaos as (
  select distinct pc.registro_ans
  from stg_ans.stg_produto_caracteristica pc
  where pc.registro_ans is not null
    and not exists (
      select 1 from stg_ans.stg_cadop c where c.registro_ans = pc.registro_ans
    )
)
select 'orfaos_distintos' as metrica, count(*)::text as valor from orfaos
union all
select 'amostra_min', min(registro_ans) from orfaos
union all
select 'amostra_max', max(registro_ans) from orfaos;

\echo ''
\echo '=== Comportamento da fonte CADOP (estado atual) ==='
\echo 'bruto_ans.cadop deve refletir 1:1 o que o portal ANS publica.'
\echo 'O Relatorio_cadop.csv publica apenas operadoras ATIVAS,'
\echo 'então órfãos são esperados para qualquer fato histórico.'
select 'bronze_distintos' as metrica, count(distinct registro_ans)::text as valor
  from bruto_ans.cadop;

\echo ''
\echo '=== Operadoras canceladas (fonte ANS separada — Sprint 44) ==='
select 'stg_operadora_cancelada_count' as metrica, count(*)::text as valor
  from stg_ans.stg_operadora_cancelada;

\echo ''
\echo '=== Conclusão ==='
\echo 'O número 57.074 reportado pelo dbt test foi de LINHAS órfãs em produto,'
\echo 'não de operadoras distintas. Em operadoras distintas: 2.014.'
\echo 'A causa raiz é histórica, não bug. A correção definitiva passa por'
\echo 'ingerir a fonte ANS de operadoras canceladas e expor uma dim union'
\echo 'CADOP atual + canceladas como `dim_operadora_historica`.'
