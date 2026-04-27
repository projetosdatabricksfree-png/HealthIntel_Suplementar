# Catálogo de Endpoints

| Endpoint | Auth | Plano mínimo | Dataset de origem | Versão |
| --- | --- | --- | --- | --- |
| `GET /saude` | não | público | — | v1 |
| `GET /prontidao` | não | público | — | v1 |
| `GET /v1/meta/dataset` | não | público | `plataforma.versao_dataset` | v1 |
| `GET /v1/meta/versao` | não | público | `plataforma.versao_dataset` | v1 |
| `GET /v1/meta/pipeline` | não | público | `plataforma.job` | v1 |
| `GET /v1/meta/endpoints` | não | público | catálogo interno | v1 |
| `GET /v1/operadoras` | sim | starter | `api_ans.api_operadora` | v1 |
| `GET /v1/operadoras/{registro_ans}` | sim | starter | `api_ans.api_operadora` | v1 |
| `GET /v1/operadoras/{registro_ans}/score` | sim | starter | `api_ans.api_score_operadora_mensal` | v1 |
| `GET /v1/operadoras/{registro_ans}/score-regulatorio` | sim | growth | `api_ans.api_score_regulatorio_operadora_mensal` | v2 |
| `GET /v1/operadoras/{registro_ans}/regime-especial` | sim | growth | `api_ans.api_regime_especial_operadora` | v1 |
| `GET /v1/operadoras/{registro_ans}/portabilidade` | sim | growth | `api_ans.api_portabilidade_operadora_mensal` | v1 |
| `GET /v1/operadoras/{registro_ans}/financeiro` | sim | pro | `api_ans.api_financeiro_operadora_mensal` | v2 |
| `GET /v1/operadoras/{registro_ans}/score-v2` | sim | pro | `api_ans.api_score_v2_operadora_mensal` | v2 |
| `GET /v1/operadoras/{registro_ans}/rede` | sim | growth | `api_ans.api_rede_assistencial` | v1 |
| `GET /v1/mercado/municipio` | sim | starter | `api_ans.api_market_share_mensal` | v1 |
| `GET /v1/mercado/vazio-assistencial` | sim | growth | `api_ans.api_vazio_assistencial` | v1 |
| `GET /v1/rede/municipio/{cd_municipio}` | sim | growth | `api_ans.api_rede_assistencial` | v1 |
| `GET /v1/rankings/operadora/score` | sim | starter | `api_ans.api_ranking_score` | v1 |
| `GET /v1/rankings/operadora/crescimento` | sim | starter | `api_ans.api_ranking_crescimento` | v1 |
| `GET /v1/rankings/municipio/oportunidade` | sim | starter | `api_ans.api_ranking_oportunidade` | v1 |
| `GET /v1/rankings/municipio/oportunidade-v2` | sim | growth | `api_ans.api_oportunidade_v2_municipio_mensal` | v2 |
| `GET /v1/cnes/municipio/{cd_municipio}` | sim | growth | `api_ans.api_cnes_municipio` | v1 |
| `GET /v1/cnes/uf/{sg_uf}` | sim | growth | `api_ans.api_cnes_municipio` | v1 |
| `GET /v1/tiss/{registro_ans}/procedimentos` | sim | growth | `api_ans.api_tiss_operadora_trimestral` | v1 |
| `GET /v1/tiss/{registro_ans}/sinistralidade` | sim | growth | `api_ans.api_sinistralidade_procedimento` | v1 |
| `GET /v1/rede/gap/{cd_municipio}` | sim | growth | `api_ans.api_cnes_rede_gap` | v1 |

## Fase 3

| Endpoint | Auth | Plano mínimo | Dataset de origem | Versão |
| --- | --- | --- | --- | --- |
| `GET /v1/bronze/*` | sim | enterprise_tecnico | `api_ans.api_bronze_*` | v1 |
| `GET /v1/prata/*` | sim | analitico | `api_ans.api_prata_*` | v1 |
| `GET /v1/operadoras/{registro_ans}/score-v3` | sim | essencial | `api_ans.api_score_v3_operadora_mensal` | v1 |
| `GET /v1/operadoras/{registro_ans}/score-v3/historico` | sim | essencial | `api_ans.api_score_v3_operadora_mensal` | v1 |
| `GET /v1/rankings/composto` | sim | essencial | `api_ans.api_ranking_composto_mensal` | v1 |

## Fase 5

| Endpoint | Auth | Plano mínimo | Dataset de origem | Versão |
| --- | --- | --- | --- | --- |
| `GET /v1/premium/operadoras` | sim | premium | `api_ans.api_premium_operadora_360_validado` | v1 |
| `GET /v1/premium/cnes/estabelecimentos` | sim | premium | `api_ans.api_premium_cnes_estabelecimento_validado` | v1 |
| `GET /v1/premium/quality/datasets` | sim | premium | `api_ans.api_premium_quality_dataset` | v1 |

## Observação

O catálogo acima deve ser mantido alinhado ao `GET /v1/meta/endpoints`.
