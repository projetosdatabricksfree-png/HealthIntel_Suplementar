# Sprint 23 — Gold Curado: Data Products ANS

**Status:** Pendente
**Objetivo:** criar os marts Gold em `nucleo_ans` com fatos, dimensões, marts e métricas de negócio, prontos para API e consumo externo; introduzir dimensões adicionais; documentar grão e chaves de cada mart.
**Critério de saída:** 6 marts em `nucleo_ans` compilando sem erro; `dbt test --select tag:mart` zero falhas; grão documentado para cada mart em `_marts_gold.yml`.

## Histórias

### HIS-23.0 — Auditoria de Dependências Gold

- [ ] Antes de criar SQL dos marts, confirmar todos os modelos `fat_*`, `dim_*` e `int_*` citados como dependência.
- [ ] Para cada mart, registrar em `_marts_gold.yml` a origem efetiva das dependências e o fallback arquitetural quando o modelo necessário ainda não existir.
- [ ] Bloquear implementação de mart que dependa de modelo inexistente sem decisão explícita de criar a dependência nesta sprint.

### HIS-23.1 — Dimensões Adicionais

- [x] Criar `healthintel_dbt/models/marts/dimensao/dim_modalidade.sql`:
  - Source: `bruto_ans.cadop` via `stg_cadop`
  - Colunas: `modalidade_id` (surrogate), `codigo_modalidade`, `descricao_modalidade`, `ativa`
  - Materialização: `table`, schema: `nucleo_ans`, tag: `dimensao`
- [x] Criar `healthintel_dbt/models/marts/dimensao/dim_segmentacao.sql`:
  - Segmentações assistenciais ANS (ambulatorial, hospitalar, odontológico, etc.)
  - Source: tabela de referência (`seeds/ref_segmentacao.csv`) ou CADOP campo `segmentacao`
- [x] Criar `healthintel_dbt/models/marts/dimensao/dim_tipo_contratacao.sql`:
  - Tipos: coletivo empresarial, coletivo por adesão, individual/familiar
  - Source: CADOP ou seed de referência
- [ ] Documentar as 3 novas dimensões em `healthintel_dbt/models/marts/dimensao/_dimensao.yml`:
  - Grão: uma linha por modalidade/segmentação/tipo
  - Testes: `unique` em `_id`, `not_null` em `codigo_*`

### HIS-23.2 — mart_operadora_360

- [x] Criar `healthintel_dbt/models/marts/fato/mart_operadora_360.sql`:
  - **Grão**: uma linha por `(registro_ans, competencia)` — visão 360° da operadora no mês
  - Joins:
    - `fat_beneficiario_operadora` — `qt_beneficiarios`, `variacao_mensal_pct`
    - `fat_financeiro_operadora_trimestral` — `receita_total`, `sinistralidade_pct` (último trimestre do mês)
    - `fat_score_v3_operadora_mensal` — `score_total`, `componente_core`, ..., `versao_metodologia`
    - `fat_monitoramento_regulatorio_trimestral` — `qtd_processos_ativos`, `multas_total`
    - `fat_market_share_mensal` — `market_share_pct`, `rank_porte`
    - `dim_operadora_atual` — `razao_social`, `modalidade`, `uf_sede`, `ativo`
  - Materialização: `incremental`, `unique_key: [registro_ans, competencia]`, schema: `nucleo_ans`, tag: `mart`
  - Reprocessa últimas 4 competências por run
- [x] Documentar em `_marts_gold.yml`: grão, chaves, métricas disponíveis, fonte de cada coluna.

### HIS-23.3 — mart_mercado_municipio

- [x] Criar `healthintel_dbt/models/marts/fato/mart_mercado_municipio.sql`:
  - **Grão**: uma linha por `(cd_municipio, competencia)` — visão de mercado territorial
  - Joins:
    - `fat_beneficiario_localidade` — `qt_beneficiarios_total`, `qt_operadoras_ativas`
    - `fat_market_share_mensal` agregado por município — HHI, operadora dominante
    - `fat_oportunidade_v2_municipio_mensal` — `score_oportunidade`, `populacao_alvo`, `penetracao_pct`
    - `fat_cnes_rede_gap_municipio` — `gap_leitos`, `gap_especialistas`
    - `dim_localidade` — `nome_municipio`, `uf`, `codigo_ibge`
  - Materialização: `incremental`, `unique_key: [cd_municipio, competencia]`, schema: `nucleo_ans`, tag: `mart`
- [x] Documentar em `_marts_gold.yml`.

### HIS-23.4 — mart_regulatorio_operadora

- [x] Criar `healthintel_dbt/models/marts/fato/mart_regulatorio_operadora.sql`:
  - **Grão**: uma linha por `(registro_ans, trimestre)` — situação regulatória trimestral
  - Joins:
    - `fat_monitoramento_regulatorio_trimestral` — processos, multas, regime especial
    - `fat_regime_especial_historico` — `ativo`, `data_inicio_regime`
    - `fat_reclamacao_operadora` — `qtd_reclamacoes`, `indice_reclamacao` (IGR)
    - `fat_idss_operadora` — `idss_score`, `idss_classificacao` (ano_base)
    - `dim_operadora_atual` — dados cadastrais
  - Colunas derivadas: `tendencia_regulatoria` (piora/estável/melhora vs. trimestre anterior), `nivel_alerta` (verde/amarelo/vermelho)
  - Materialização: `incremental`, `unique_key: [registro_ans, trimestre]`, schema: `nucleo_ans`, tag: `mart`
- [x] Documentar em `_marts_gold.yml`.

### HIS-23.5 — mart_rede_assistencial

- [x] Criar `healthintel_dbt/models/marts/fato/mart_rede_assistencial.sql`:
  - **Grão**: uma linha por `(registro_ans, cd_municipio, competencia)` — presença da operadora no município
  - Joins:
    - `fat_cobertura_rede_municipio` — `qt_prestadores`, `qt_especialidades`
    - `fat_densidade_rede_operadora` — `densidade_prestadores_por_10k_beneficiarios`
    - `fat_cnes_rede_gap_municipio` — `gap_leitos_cnes`, `gap_especialistas_cnes`
    - `fat_vazio_assistencial_municipio` — `classificacao_vazio`
    - `dim_localidade` — `nome_municipio`, `uf`
    - `dim_operadora_atual` — `razao_social`
  - Materialização: `incremental`, `unique_key: [registro_ans, cd_municipio, competencia]`, schema: `nucleo_ans`, tag: `mart`
- [x] Documentar em `_marts_gold.yml`.

### HIS-23.6 — mart_score_operadora

- [x] Criar `healthintel_dbt/models/marts/fato/mart_score_operadora.sql`:
  - **Grão**: uma linha por `(registro_ans, competencia)` — painel de score e ranking
  - Joins:
    - `fat_score_v3_operadora_mensal` — todos os 5 componentes + score_total
    - `fat_ranking_composto_mensal` — `posicao_geral`, `posicao_por_modalidade`
    - `fat_oportunidade_v2_municipio_mensal` agregado por operadora — `municipios_com_oportunidade`
    - `int_crescimento_operadora_12m` — `crescimento_12m_pct`, `tendencia_crescimento`
    - `dim_operadora_atual` — `razao_social`, `modalidade`
  - Colunas derivadas: `faixa_score` (Excelente/Bom/Regular/Atenção), `variacao_score_mom` (vs. mês anterior)
  - Materialização: `incremental`, `unique_key: [registro_ans, competencia]`, schema: `nucleo_ans`, tag: `mart`
- [x] Documentar em `_marts_gold.yml`.

### HIS-23.7 — mart_tiss_procedimento

- [x] Criar `healthintel_dbt/models/marts/fato/mart_tiss_procedimento.sql`:
  - **Grão**: uma linha por `(registro_ans, cd_procedimento_tuss, trimestre)` — utilização e custo por procedimento
  - Joins:
    - `fat_tiss_procedimento_operadora` — `qt_procedimentos`, `vl_total`
    - `fat_sinistralidade_procedimento` — `sinistralidade_pct`
    - `fat_glosa_operadora_mensal` — `taxa_glosa_pct` (agregado por trimestre)
    - `dim_operadora_atual` — cadastrais
  - Colunas derivadas: `custo_medio_procedimento`, `variacao_trimestral_pct`
  - Materialização: `incremental`, `unique_key: [registro_ans, cd_procedimento_tuss, trimestre]`, schema: `nucleo_ans`, tag: `mart`
- [x] Documentar em `_marts_gold.yml`.

### HIS-23.8 — Documentação e Testes dos Marts

- [x] Criar `healthintel_dbt/models/marts/fato/_marts_gold.yml`:
  - Para cada mart: `name`, `description`, `config`, `columns` (chaves + métricas principais com `description` e `tests`)
  - Testes genéricos por mart: `unique` na `unique_key`, `not_null` em chaves e métricas críticas, `dbt_utils.expression_is_true` para invariantes de negócio (ex: `score_total between 0 and 100`)
- [x] Criar testes singulares:
  - `healthintel_dbt/tests/assert_mart_operadora_360_grao_unico.sql` — sem duplicatas por (registro_ans, competencia)
  - `healthintel_dbt/tests/assert_mart_score_faixa_valida.sql` — `score_total between 0 and 100`
  - `healthintel_dbt/tests/assert_mart_mercado_hhi_valido.sql` — `hhi between 0 and 10000`

## Entregas esperadas

- [x] `models/marts/dimensao/dim_modalidade.sql`
- [x] `models/marts/dimensao/dim_segmentacao.sql`
- [x] `models/marts/dimensao/dim_tipo_contratacao.sql`
- [x] `models/marts/fato/mart_operadora_360.sql`
- [x] `models/marts/fato/mart_mercado_municipio.sql`
- [x] `models/marts/fato/mart_regulatorio_operadora.sql`
- [x] `models/marts/fato/mart_rede_assistencial.sql`
- [x] `models/marts/fato/mart_score_operadora.sql`
- [x] `models/marts/fato/mart_tiss_procedimento.sql`
- [x] `models/marts/fato/_marts_gold.yml` com column-level docs e testes
- [ ] `models/marts/dimensao/_dimensao.yml` atualizado com novas dimensões
- [x] Testes singulares `assert_mart_*.sql`

## Validação esperada

- [x] `dbt compile --select tag:mart`
- [x] `dbt build --select tag:mart` — sem falhas em dados demo
- [x] `dbt test --select tag:mart` — zero falhas
- [x] `mart_operadora_360` materializado em `nucleo_ans` com dados para `competencia=202501`
- [ ] `mart_score_operadora` com `score_total between 0 and 100` para todos os registros
- [ ] `assert_mart_operadora_360_grao_unico` passando (zero duplicatas)
