# Baseline Hardgate Fase 4 — v3.0.0

## Referência de Congelamento

- Tag git: `v3.0.0`
- Commit resolvido localmente: `fe7b839c2f9c72e4cbab89c117d6dd692e8b0994`
- Comando de validação: `git rev-parse v3.0.0^{}`
- Release documentada: `docs/releases/v3.0.0.md`
- Regra: todo artefato listado neste documento é baseline aprovado e deve permanecer imutável durante a Fase 5.

## Comandos de Inventário

Inventário extraído com:

```bash
git ls-tree -r --name-only v3.0.0 -- healthintel_dbt/models
git ls-tree -r --name-only v3.0.0 -- api
git ls-tree -r --name-only v3.0.0 -- docs/releases
rg "v3.0.0|hardgate|consumo_|api_" docs healthintel_dbt api
```

## Modelos Staging

| Modelo | Arquivo |
|--------|---------|
| `stg_cadop` | `healthintel_dbt/models/staging/stg_cadop.sql` |
| `stg_cnes_estabelecimento` | `healthintel_dbt/models/staging/stg_cnes_estabelecimento.sql` |
| `stg_diops` | `healthintel_dbt/models/staging/stg_diops.sql` |
| `stg_fip` | `healthintel_dbt/models/staging/stg_fip.sql` |
| `stg_glosa` | `healthintel_dbt/models/staging/stg_glosa.sql` |
| `stg_idss` | `healthintel_dbt/models/staging/stg_idss.sql` |
| `stg_igr` | `healthintel_dbt/models/staging/stg_igr.sql` |
| `stg_nip` | `healthintel_dbt/models/staging/stg_nip.sql` |
| `stg_portabilidade` | `healthintel_dbt/models/staging/stg_portabilidade.sql` |
| `stg_prudencial` | `healthintel_dbt/models/staging/stg_prudencial.sql` |
| `stg_rede_assistencial` | `healthintel_dbt/models/staging/stg_rede_assistencial.sql` |
| `stg_regime_especial` | `healthintel_dbt/models/staging/stg_regime_especial.sql` |
| `stg_rn623_lista` | `healthintel_dbt/models/staging/stg_rn623_lista.sql` |
| `stg_sib_municipio` | `healthintel_dbt/models/staging/stg_sib_municipio.sql` |
| `stg_sib_operadora` | `healthintel_dbt/models/staging/stg_sib_operadora.sql` |
| `stg_taxa_resolutividade` | `healthintel_dbt/models/staging/stg_taxa_resolutividade.sql` |
| `stg_tiss_procedimento` | `healthintel_dbt/models/staging/stg_tiss_procedimento.sql` |
| `stg_vda` | `healthintel_dbt/models/staging/stg_vda.sql` |

## Modelos Intermediate

| Modelo | Arquivo |
|--------|---------|
| `int_beneficiario_localidade_enriquecido` | `healthintel_dbt/models/intermediate/int_beneficiario_localidade_enriquecido.sql` |
| `int_beneficiario_operadora_enriquecido` | `healthintel_dbt/models/intermediate/int_beneficiario_operadora_enriquecido.sql` |
| `int_cnes_municipio_resumo` | `healthintel_dbt/models/intermediate/int_cnes_municipio_resumo.sql` |
| `int_cnes_x_rede_municipio` | `healthintel_dbt/models/intermediate/int_cnes_x_rede_municipio.sql` |
| `int_crescimento_operadora_12m` | `healthintel_dbt/models/intermediate/int_crescimento_operadora_12m.sql` |
| `int_financeiro_operadora_periodo` | `healthintel_dbt/models/intermediate/int_financeiro_operadora_periodo.sql` |
| `int_idss_normalizado` | `healthintel_dbt/models/intermediate/int_idss_normalizado.sql` |
| `int_metrica_municipio` | `healthintel_dbt/models/intermediate/int_metrica_municipio.sql` |
| `int_operadora_canonica` | `healthintel_dbt/models/intermediate/int_operadora_canonica.sql` |
| `int_operadora_competencia` | `healthintel_dbt/models/intermediate/int_operadora_competencia.sql` |
| `int_oportunidade_v2_municipio` | `healthintel_dbt/models/intermediate/int_oportunidade_v2_municipio.sql` |
| `int_rede_assistencial_municipio` | `healthintel_dbt/models/intermediate/int_rede_assistencial_municipio.sql` |
| `int_regulatorio_operadora_trimestre` | `healthintel_dbt/models/intermediate/int_regulatorio_operadora_trimestre.sql` |
| `int_regulatorio_v2_operadora_trimestre` | `healthintel_dbt/models/intermediate/int_regulatorio_v2_operadora_trimestre.sql` |
| `int_score_insumo` | `healthintel_dbt/models/intermediate/int_score_insumo.sql` |
| `int_score_v2_componentes` | `healthintel_dbt/models/intermediate/int_score_v2_componentes.sql` |
| `int_score_v3_componentes` | `healthintel_dbt/models/intermediate/int_score_v3_componentes.sql` |
| `int_sinistralidade_procedimento` | `healthintel_dbt/models/intermediate/int_sinistralidade_procedimento.sql` |
| `int_tiss_operadora_trimestre` | `healthintel_dbt/models/intermediate/int_tiss_operadora_trimestre.sql` |
| `int_volatilidade_operadora_24m` | `healthintel_dbt/models/intermediate/int_volatilidade_operadora_24m.sql` |

## Modelos Marts

### Dimensões

| Modelo | Arquivo |
|--------|---------|
| `dim_competencia` | `healthintel_dbt/models/marts/dimensao/dim_competencia.sql` |
| `dim_localidade` | `healthintel_dbt/models/marts/dimensao/dim_localidade.sql` |
| `dim_modalidade` | `healthintel_dbt/models/marts/dimensao/dim_modalidade.sql` |
| `dim_operadora_atual` | `healthintel_dbt/models/marts/dimensao/dim_operadora_atual.sql` |
| `dim_segmentacao` | `healthintel_dbt/models/marts/dimensao/dim_segmentacao.sql` |
| `dim_tipo_contratacao` | `healthintel_dbt/models/marts/dimensao/dim_tipo_contratacao.sql` |

### Fatos `fat_*`

| Modelo | Arquivo |
|--------|---------|
| `fat_beneficiario_localidade` | `healthintel_dbt/models/marts/fato/fat_beneficiario_localidade.sql` |
| `fat_beneficiario_operadora` | `healthintel_dbt/models/marts/fato/fat_beneficiario_operadora.sql` |
| `fat_cnes_estabelecimento_municipio` | `healthintel_dbt/models/marts/fato/fat_cnes_estabelecimento_municipio.sql` |
| `fat_cnes_rede_gap_municipio` | `healthintel_dbt/models/marts/fato/fat_cnes_rede_gap_municipio.sql` |
| `fat_cobertura_rede_municipio` | `healthintel_dbt/models/marts/fato/fat_cobertura_rede_municipio.sql` |
| `fat_densidade_rede_operadora` | `healthintel_dbt/models/marts/fato/fat_densidade_rede_operadora.sql` |
| `fat_financeiro_operadora_trimestral` | `healthintel_dbt/models/marts/fato/fat_financeiro_operadora_trimestral.sql` |
| `fat_glosa_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_glosa_operadora_mensal.sql` |
| `fat_idss_operadora` | `healthintel_dbt/models/marts/fato/fat_idss_operadora.sql` |
| `fat_market_share_mensal` | `healthintel_dbt/models/marts/fato/fat_market_share_mensal.sql` |
| `fat_monitoramento_regulatorio_trimestral` | `healthintel_dbt/models/marts/fato/fat_monitoramento_regulatorio_trimestral.sql` |
| `fat_oportunidade_municipio_mensal` | `healthintel_dbt/models/marts/fato/fat_oportunidade_municipio_mensal.sql` |
| `fat_oportunidade_v2_municipio_mensal` | `healthintel_dbt/models/marts/fato/fat_oportunidade_v2_municipio_mensal.sql` |
| `fat_ranking_composto_mensal` | `healthintel_dbt/models/marts/fato/fat_ranking_composto_mensal.sql` |
| `fat_reclamacao_operadora` | `healthintel_dbt/models/marts/fato/fat_reclamacao_operadora.sql` |
| `fat_regime_especial_historico` | `healthintel_dbt/models/marts/fato/fat_regime_especial_historico.sql` |
| `fat_score_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_score_operadora_mensal.sql` |
| `fat_score_regulatorio_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_score_regulatorio_operadora_mensal.sql` |
| `fat_score_v2_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_score_v2_operadora_mensal.sql` |
| `fat_score_v3_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_score_v3_operadora_mensal.sql` |
| `fat_sinistralidade_procedimento` | `healthintel_dbt/models/marts/fato/fat_sinistralidade_procedimento.sql` |
| `fat_tiss_procedimento_operadora` | `healthintel_dbt/models/marts/fato/fat_tiss_procedimento_operadora.sql` |
| `fat_vazio_assistencial_municipio` | `healthintel_dbt/models/marts/fato/fat_vazio_assistencial_municipio.sql` |
| `fat_vda_operadora_mensal` | `healthintel_dbt/models/marts/fato/fat_vda_operadora_mensal.sql` |

### Marts `mart_*`

| Modelo | Arquivo |
|--------|---------|
| `mart_mercado_municipio` | `healthintel_dbt/models/marts/fato/mart_mercado_municipio.sql` |
| `mart_operadora_360` | `healthintel_dbt/models/marts/fato/mart_operadora_360.sql` |
| `mart_rede_assistencial` | `healthintel_dbt/models/marts/fato/mart_rede_assistencial.sql` |
| `mart_regulatorio_operadora` | `healthintel_dbt/models/marts/fato/mart_regulatorio_operadora.sql` |
| `mart_score_operadora` | `healthintel_dbt/models/marts/fato/mart_score_operadora.sql` |
| `mart_tiss_procedimento` | `healthintel_dbt/models/marts/fato/mart_tiss_procedimento.sql` |

## Modelos API

### API Serviço

| Modelo | Arquivo |
|--------|---------|
| `api_cnes_municipio` | `healthintel_dbt/models/api/api_cnes_municipio.sql` |
| `api_cnes_rede_gap` | `healthintel_dbt/models/api/api_cnes_rede_gap.sql` |
| `api_financeiro_operadora_mensal` | `healthintel_dbt/models/api/api_financeiro_operadora_mensal.sql` |
| `api_market_share_mensal` | `healthintel_dbt/models/api/api_market_share_mensal.sql` |
| `api_operadora` | `healthintel_dbt/models/api/api_operadora.sql` |
| `api_oportunidade_municipio_mensal` | `healthintel_dbt/models/api/api_oportunidade_municipio_mensal.sql` |
| `api_oportunidade_v2_municipio_mensal` | `healthintel_dbt/models/api/api_oportunidade_v2_municipio_mensal.sql` |
| `api_portabilidade_operadora_mensal` | `healthintel_dbt/models/api/api_portabilidade_operadora_mensal.sql` |
| `api_ranking_composto_mensal` | `healthintel_dbt/models/api/api_ranking_composto_mensal.sql` |
| `api_ranking_crescimento` | `healthintel_dbt/models/api/api_ranking_crescimento.sql` |
| `api_ranking_oportunidade` | `healthintel_dbt/models/api/api_ranking_oportunidade.sql` |
| `api_ranking_score` | `healthintel_dbt/models/api/api_ranking_score.sql` |
| `api_rede_assistencial` | `healthintel_dbt/models/api/api_rede_assistencial.sql` |
| `api_regime_especial_operadora` | `healthintel_dbt/models/api/api_regime_especial_operadora.sql` |
| `api_regulatorio_operadora_trimestral` | `healthintel_dbt/models/api/api_regulatorio_operadora_trimestral.sql` |
| `api_rn623_lista_trimestral` | `healthintel_dbt/models/api/api_rn623_lista_trimestral.sql` |
| `api_score_operadora_mensal` | `healthintel_dbt/models/api/api_score_operadora_mensal.sql` |
| `api_score_regulatorio_operadora_mensal` | `healthintel_dbt/models/api/api_score_regulatorio_operadora_mensal.sql` |
| `api_score_v2_operadora_mensal` | `healthintel_dbt/models/api/api_score_v2_operadora_mensal.sql` |
| `api_score_v3_operadora_mensal` | `healthintel_dbt/models/api/api_score_v3_operadora_mensal.sql` |
| `api_sinistralidade_procedimento` | `healthintel_dbt/models/api/api_sinistralidade_procedimento.sql` |
| `api_tiss_operadora_trimestral` | `healthintel_dbt/models/api/api_tiss_operadora_trimestral.sql` |
| `api_vazio_assistencial` | `healthintel_dbt/models/api/api_vazio_assistencial.sql` |

### API Bronze

| Modelo | Arquivo |
|--------|---------|
| `api_bronze_cadop` | `healthintel_dbt/models/api/bronze/api_bronze_cadop.sql` |
| `api_bronze_diops` | `healthintel_dbt/models/api/bronze/api_bronze_diops.sql` |
| `api_bronze_fip` | `healthintel_dbt/models/api/bronze/api_bronze_fip.sql` |
| `api_bronze_glosa` | `healthintel_dbt/models/api/bronze/api_bronze_glosa.sql` |
| `api_bronze_idss` | `healthintel_dbt/models/api/bronze/api_bronze_idss.sql` |
| `api_bronze_igr` | `healthintel_dbt/models/api/bronze/api_bronze_igr.sql` |
| `api_bronze_nip` | `healthintel_dbt/models/api/bronze/api_bronze_nip.sql` |
| `api_bronze_rede_assistencial` | `healthintel_dbt/models/api/bronze/api_bronze_rede_assistencial.sql` |
| `api_bronze_sib_municipio` | `healthintel_dbt/models/api/bronze/api_bronze_sib_municipio.sql` |
| `api_bronze_sib_operadora` | `healthintel_dbt/models/api/bronze/api_bronze_sib_operadora.sql` |
| `api_bronze_vda` | `healthintel_dbt/models/api/bronze/api_bronze_vda.sql` |

### API Prata

| Modelo | Arquivo |
|--------|---------|
| `api_prata_cadop` | `healthintel_dbt/models/api/prata/api_prata_cadop.sql` |
| `api_prata_cnes_municipio` | `healthintel_dbt/models/api/prata/api_prata_cnes_municipio.sql` |
| `api_prata_cnes_rede_gap` | `healthintel_dbt/models/api/prata/api_prata_cnes_rede_gap.sql` |
| `api_prata_diops` | `healthintel_dbt/models/api/prata/api_prata_diops.sql` |
| `api_prata_financeiro_periodo` | `healthintel_dbt/models/api/prata/api_prata_financeiro_periodo.sql` |
| `api_prata_fip` | `healthintel_dbt/models/api/prata/api_prata_fip.sql` |
| `api_prata_glosa` | `healthintel_dbt/models/api/prata/api_prata_glosa.sql` |
| `api_prata_idss` | `healthintel_dbt/models/api/prata/api_prata_idss.sql` |
| `api_prata_igr` | `healthintel_dbt/models/api/prata/api_prata_igr.sql` |
| `api_prata_municipio_metrica` | `healthintel_dbt/models/api/prata/api_prata_municipio_metrica.sql` |
| `api_prata_nip` | `healthintel_dbt/models/api/prata/api_prata_nip.sql` |
| `api_prata_operadora_enriquecida` | `healthintel_dbt/models/api/prata/api_prata_operadora_enriquecida.sql` |
| `api_prata_rede_assistencial` | `healthintel_dbt/models/api/prata/api_prata_rede_assistencial.sql` |
| `api_prata_sib_municipio` | `healthintel_dbt/models/api/prata/api_prata_sib_municipio.sql` |
| `api_prata_sib_operadora` | `healthintel_dbt/models/api/prata/api_prata_sib_operadora.sql` |
| `api_prata_tiss_procedimento` | `healthintel_dbt/models/api/prata/api_prata_tiss_procedimento.sql` |
| `api_prata_vda` | `healthintel_dbt/models/api/prata/api_prata_vda.sql` |

## Modelos Consumo

Os 8 modelos abaixo são modelos `consumo_*` existentes no baseline `v3.0.0` do repositório:

| Modelo | Arquivo |
|--------|---------|
| `consumo_beneficiarios_municipio_mes` | `healthintel_dbt/models/consumo/consumo_beneficiarios_municipio_mes.sql` |
| `consumo_beneficiarios_operadora_mes` | `healthintel_dbt/models/consumo/consumo_beneficiarios_operadora_mes.sql` |
| `consumo_financeiro_operadora_trimestre` | `healthintel_dbt/models/consumo/consumo_financeiro_operadora_trimestre.sql` |
| `consumo_operadora_360` | `healthintel_dbt/models/consumo/consumo_operadora_360.sql` |
| `consumo_oportunidade_municipio` | `healthintel_dbt/models/consumo/consumo_oportunidade_municipio.sql` |
| `consumo_rede_assistencial_municipio` | `healthintel_dbt/models/consumo/consumo_rede_assistencial_municipio.sql` |
| `consumo_regulatorio_operadora_trimestre` | `healthintel_dbt/models/consumo/consumo_regulatorio_operadora_trimestre.sql` |
| `consumo_score_operadora_mes` | `healthintel_dbt/models/consumo/consumo_score_operadora_mes.sql` |

## Arquivos Relevantes da API

| Grupo | Arquivos no baseline `v3.0.0` |
|-------|-------------------------------|
| Entrada da aplicação | `api/app/main.py` |
| Core | `api/app/core/config.py`, `api/app/core/database.py`, `api/app/core/errors.py`, `api/app/core/redis_client.py`, `api/app/core/security.py` |
| Middleware | `api/app/middleware/autenticacao.py`, `api/app/middleware/hardening.py`, `api/app/middleware/log_requisicao.py`, `api/app/middleware/rate_limit.py` |
| Routers | `admin_billing.py`, `admin_layout.py`, `bronze.py`, `cnes.py`, `financeiro.py`, `mercado.py`, `meta.py`, `operadora.py`, `prata.py`, `ranking.py`, `rede.py`, `regulatorio.py`, `regulatorio_v2.py`, `tiss.py` |
| Services | `billing.py`, `bronze.py`, `cnes.py`, `financeiro_v2.py`, `health.py`, `layout_admin.py`, `mercado.py`, `meta.py`, `operadora.py`, `prata.py`, `ranking.py`, `rede.py`, `regulatorio.py`, `regulatorio_v2.py`, `score_v3.py`, `tiss.py`, `uso.py` |
| Schemas | `billing.py`, `bronze.py`, `cnes.py`, `financeiro_v2.py`, `layout_admin.py`, `mercado.py`, `meta.py`, `municipio.py`, `operadora.py`, `prata.py`, `ranking.py`, `rede.py`, `regulatorio.py`, `regulatorio_v2.py`, `score_v3.py`, `tiss.py` |

## Releases e Hardgates Conhecidos

| Fonte | Evidência |
|-------|-----------|
| `docs/releases/v3.0.0.md` | Release `3.0.0`, datada de 2026-04-24, fecha a Fase 4 com modelagem Consumo, segurança, limites de API, streaming ingestion e resiliência. |
| Ruff | Release registra `ruff check api ingestao scripts testes` aprovado localmente. |
| Pytest | Release registra `pytest -v` parcialmente aprovado localmente; falhas remanescentes associadas à indisponibilidade de PostgreSQL/Redis locais. |
| dbt | Release registra tentativa de `dbt compile --select tag:prata tag:mart tag:consumo`; validação final dependente de CI por ausência de binário/infra local. |
| Fase 4 README | Hardgates de Fase 4 documentam `smoke-prata`, `smoke-sib`, `smoke-cadop`, `smoke-consumo`, `dbt build --select tag:prata tag:mart tag:consumo`, `dbt test`, `dbt docs generate` e regressão `test_endpoints_fase4.py`. |

## Regra de Não Regressão

- A Fase 5 pode usar os artefatos acima como upstream.
- A Fase 5 não pode editar, substituir ou alterar a semântica dos artefatos acima.
- A FastAPI permanece limitada à camada `api_ans`.
- A entrega SQL direta legada permanece em `consumo_ans`.
- Produtos premium novos devem ser publicados em `consumo_premium_ans` e, quando expostos por API, mediados por `api_ans.api_premium_*`.
