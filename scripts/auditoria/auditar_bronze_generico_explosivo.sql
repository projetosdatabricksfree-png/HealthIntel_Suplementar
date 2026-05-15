-- Audita risco de explosao em bruto_ans.ans_linha_generica.
-- Uso:
-- docker compose -f infra/docker-compose.yml exec -T postgres \
--   psql -U healthintel -d healthintel \
--   -f scripts/auditoria/auditar_bronze_generico_explosivo.sql

\pset pager off

select
    now() as auditado_em,
    pg_size_pretty(pg_database_size(current_database())) as tamanho_database,
    pg_size_pretty(pg_total_relation_size('bruto_ans.ans_linha_generica'::regclass)) as tamanho_ans_linha_generica,
    coalesce(s.n_live_tup, 0) as linhas_estimadas,
    case
        when pg_total_relation_size('bruto_ans.ans_linha_generica'::regclass) > 100 * 1024 * 1024
          or coalesce(s.n_live_tup, 0) > 1000000
        then 'TRUNCATE_RECOMENDADO_APOS_CONFIRMAR_DEPENDENCIAS'
        else 'OK'
    end as recomendacao
from pg_stat_user_tables s
where s.relid = 'bruto_ans.ans_linha_generica'::regclass;

select
    dataset_codigo,
    familia,
    count(*) as linhas_estimadas_por_dataset
from bruto_ans.ans_linha_generica
group by dataset_codigo, familia
order by linhas_estimadas_por_dataset desc
limit 20;

select
    dataset_codigo,
    familia,
    arquivo_origem,
    hash_arquivo,
    max(data_ingestao) as ultima_ingestao,
    count(*) as linhas
from bruto_ans.ans_linha_generica
group by dataset_codigo, familia, arquivo_origem, hash_arquivo
order by ultima_ingestao desc nulls last, linhas desc
limit 30;

select
    familia,
    dataset_codigo,
    nome_arquivo,
    status,
    pg_size_pretty(coalesce(tamanho_bytes, 0)) as tamanho_origem,
    baixado_em,
    updated_at,
    left(coalesce(erro_mensagem, ''), 240) as erro_mensagem
from plataforma.arquivo_fonte_ans
where dataset_codigo in (
    select distinct dataset_codigo
    from bruto_ans.ans_linha_generica
)
   or familia in ('rede_prestadores', 'rede_assistencial', 'cnes', 'tiss', 'diops', 'fip', 'precificacao_ntrp', 'sip', 'sib')
order by coalesce(tamanho_bytes, 0) desc, updated_at desc
limit 30;

select
    dataset_codigo,
    status,
    tabela_destino,
    sum(coalesce(linhas_lidas, 0)) as linhas_lidas,
    sum(coalesce(linhas_inseridas, 0)) as linhas_inseridas,
    count(*) as eventos,
    max(iniciado_em) as ultimo_evento,
    left(string_agg(distinct coalesce(motivo, erro_mensagem, ''), ' | '), 300) as motivos
from plataforma.tentativa_carga_ans
where tabela_destino = 'bruto_ans.ans_linha_generica'
   or status in ('LAYOUT_NAO_MAPEADO', 'ERRO_VALIDACAO')
   or dataset_codigo in (
        select distinct dataset_codigo
        from bruto_ans.ans_linha_generica
   )
group by dataset_codigo, status, tabela_destino
order by ultimo_evento desc nulls last
limit 30;
