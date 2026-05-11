-- Sprint 42 — Validação Pós-Carga Real ANS
-- Executar via: psql -U healthintel -d healthintel -f smoke_delta_ans_100_sql.sql

-- ============================================================
-- H3: status plataforma.arquivo_fonte_ans
-- ============================================================

\echo '--- H3a: status por familia ---'
select
    familia,
    status,
    count(*) as total_arquivos
from plataforma.arquivo_fonte_ans
group by familia, status
order by familia, status;

\echo '--- H3b: status geral ---'
select
    status,
    count(*) as total_arquivos
from plataforma.arquivo_fonte_ans
group by status
order by status;

\echo '--- H3c: familias delta ANS ---'
select
    familia,
    count(*) filter (where status in ('carregado', 'bronze_generico', 'arquivado_r2')) as sucesso,
    count(*) filter (where status like 'erro%') as erro,
    count(*) filter (where status in ('baixado_sem_parser', 'pendente')) as pendente,
    count(*) as total
from plataforma.arquivo_fonte_ans
where familia in (
    'produtos_planos',
    'tuss',
    'tiss',
    'sip',
    'ressarcimento_sus',
    'precificacao_ntrp',
    'rede_prestadores',
    'regulatorios_complementares',
    'beneficiarios_cobertura'
)
group by familia
order by familia;

\echo '--- H3d: familias distintas (descoberta) ---'
select distinct familia
from plataforma.arquivo_fonte_ans
order by familia;

-- ============================================================
-- H4: contagens api_ans (20 tabelas)
-- ============================================================

\echo '--- H4: contagens api_ans ---'
select 'api_produto_plano' as tabela, count(*) as linhas from api_ans.api_produto_plano
union all
select 'api_historico_plano', count(*) from api_ans.api_historico_plano
union all
select 'api_plano_servico_opcional', count(*) from api_ans.api_plano_servico_opcional
union all
select 'api_quadro_auxiliar_corresponsabilidade', count(*) from api_ans.api_quadro_auxiliar_corresponsabilidade
union all
select 'api_tuss_procedimento_vigente', count(*) from api_ans.api_tuss_procedimento_vigente
union all
select 'api_tiss_ambulatorial_operadora_mes', count(*) from api_ans.api_tiss_ambulatorial_operadora_mes
union all
select 'api_tiss_hospitalar_operadora_mes', count(*) from api_ans.api_tiss_hospitalar_operadora_mes
union all
select 'api_tiss_plano_mes', count(*) from api_ans.api_tiss_plano_mes
union all
select 'api_sip_assistencial_operadora', count(*) from api_ans.api_sip_assistencial_operadora
union all
select 'api_ressarcimento_beneficiario_abi', count(*) from api_ans.api_ressarcimento_beneficiario_abi
union all
select 'api_ressarcimento_sus_operadora_plano', count(*) from api_ans.api_ressarcimento_sus_operadora_plano
union all
select 'api_ressarcimento_hc', count(*) from api_ans.api_ressarcimento_hc
union all
select 'api_ressarcimento_cobranca_arrecadacao', count(*) from api_ans.api_ressarcimento_cobranca_arrecadacao
union all
select 'api_ressarcimento_indice_pagamento', count(*) from api_ans.api_ressarcimento_indice_pagamento
union all
select 'api_painel_precificacao', count(*) from api_ans.api_painel_precificacao
union all
select 'api_valor_comercial_medio_municipio', count(*) from api_ans.api_valor_comercial_medio_municipio
union all
select 'api_prestador_acreditado', count(*) from api_ans.api_prestador_acreditado
union all
select 'api_alteracao_rede_hospitalar', count(*) from api_ans.api_alteracao_rede_hospitalar
union all
select 'api_penalidade_operadora', count(*) from api_ans.api_penalidade_operadora
union all
select 'api_rpc_operadora_mes', count(*) from api_ans.api_rpc_operadora_mes
order by tabela;

-- ============================================================
-- H5: contagens consumo_ans (11 tabelas)
-- ============================================================

\echo '--- H5: contagens consumo_ans ---'
select 'consumo_produto_plano' as tabela, count(*) as linhas from consumo_ans.consumo_produto_plano
union all
select 'consumo_historico_plano', count(*) from consumo_ans.consumo_historico_plano
union all
select 'consumo_plano_servico_opcional', count(*) from consumo_ans.consumo_plano_servico_opcional
union all
select 'consumo_tuss_procedimento_vigente', count(*) from consumo_ans.consumo_tuss_procedimento_vigente
union all
select 'consumo_tiss_utilizacao_operadora_mes', count(*) from consumo_ans.consumo_tiss_utilizacao_operadora_mes
union all
select 'consumo_sip_assistencial_operadora', count(*) from consumo_ans.consumo_sip_assistencial_operadora
union all
select 'consumo_ressarcimento_sus_operadora', count(*) from consumo_ans.consumo_ressarcimento_sus_operadora
union all
select 'consumo_precificacao_plano', count(*) from consumo_ans.consumo_precificacao_plano
union all
select 'consumo_rede_acreditacao', count(*) from consumo_ans.consumo_rede_acreditacao
union all
select 'consumo_regulatorio_complementar_operadora', count(*) from consumo_ans.consumo_regulatorio_complementar_operadora
union all
select 'consumo_beneficiarios_cobertura_municipio', count(*) from consumo_ans.consumo_beneficiarios_cobertura_municipio
order by tabela;

-- ============================================================
-- H6: TISS / RPC — janela 24 meses
-- ============================================================

\echo '--- H6a: TISS e RPC api_ans ---'
select
    'api_tiss_ambulatorial_operadora_mes' as tabela,
    min(competencia) as competencia_min,
    max(competencia) as competencia_max,
    count(distinct competencia) as qtd_competencias,
    count(*) as linhas
from api_ans.api_tiss_ambulatorial_operadora_mes
union all
select
    'api_tiss_hospitalar_operadora_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_tiss_hospitalar_operadora_mes
union all
select
    'api_tiss_plano_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_tiss_plano_mes
union all
select
    'api_rpc_operadora_mes',
    min(competencia),
    max(competencia),
    count(distinct competencia),
    count(*)
from api_ans.api_rpc_operadora_mes;

\echo '--- H6b: TISS consumo_ans ---'
select
    'consumo_tiss_utilizacao_operadora_mes' as tabela,
    min(competencia) as competencia_min,
    max(competencia) as competencia_max,
    count(distinct competencia) as qtd_competencias,
    count(*) as linhas
from consumo_ans.consumo_tiss_utilizacao_operadora_mes;

-- ============================================================
-- H7: TUSS oficial
-- ============================================================

\echo '--- H7a: contagem TUSS vigente ---'
select
    count(*) as total_tuss_vigente
from api_ans.api_tuss_procedimento_vigente;

\echo '--- H7b: duplicidade por codigo_tuss + versao_tuss ---'
select
    codigo_tuss,
    versao_tuss,
    count(*) as total
from api_ans.api_tuss_procedimento_vigente
group by codigo_tuss, versao_tuss
having count(*) > 1
order by total desc
limit 20;

\echo '--- H7c: amostra por codigo ---'
select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    vigencia_fim,
    is_tuss_vigente
from api_ans.api_tuss_procedimento_vigente
where codigo_tuss is not null
limit 20;

\echo '--- H7d: busca por descricao (consulta) ---'
select
    codigo_tuss,
    descricao,
    versao_tuss,
    is_tuss_vigente
from api_ans.api_tuss_procedimento_vigente
where lower(descricao) like '%consulta%'
limit 20;

\echo '--- H7e: contagem TUSS consumo ---'
select
    count(*) as total_tuss_consumo
from consumo_ans.consumo_tuss_procedimento_vigente;

-- ============================================================
-- H8: grants finais
-- ============================================================

\echo '--- H8a: grants em camadas comerciais ---'
select
    grantee,
    table_schema,
    count(*) as total_privilegios
from information_schema.role_table_grants
where table_schema in ('api_ans', 'consumo_ans', 'consumo_premium_ans')
group by grantee, table_schema
order by grantee, table_schema;

\echo '--- H8b: grants indevidos em camadas internas ---'
select
    grantee,
    table_schema,
    count(*) as total_privilegios
from information_schema.role_table_grants
where table_schema in ('bruto_ans', 'stg_ans', 'int_ans', 'nucleo_ans')
  and grantee in ('healthintel_cliente_reader', 'healthintel_premium_reader')
group by grantee, table_schema
order by grantee, table_schema;
