# Auditoria de cobertura 3 anos - API Core ANS

- Gerado em: 2026-05-16T18:42:41.811755+00:00
- Endpoints auditados: 26

## Resumo

| status | endpoints |
|---|---:|
| ok_3_anos | 8 |
| parcial | 11 |
| snapshot_vigente | 1 |
| vazio | 6 |

## Cobertura por endpoint

| endpoint | fonte | granularidade | linhas | inicio | fim | periodos | status | acao |
|---|---|---|---:|---|---|---:|---|---|
| `/v1/operadoras` | `api_ans.api_operadora.competencia_referencia` | snapshot_vigente | 1107 | 202603 | 202603 | 1 | **snapshot_vigente** | nenhuma |
| `/v1/produtos-planos` | `consumo_ans.consumo_produto_plano.competencia` | mensal | 163661 | 202605 | 202605 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/historico-planos` | `consumo_ans.consumo_historico_plano.competencia` | mensal | 163567 | 202505 | 202505 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/regulatorio` | `consumo_ans.consumo_regulatorio_operadora_trimestre.trimestre` | trimestral | 161173 | 1T2011 | 2T2026 | 62 | **ok_3_anos** | nenhuma |
| `/v1/igr` | `consumo_ans.consumo_igr.trimestre` | trimestral | 136908 | 1T2015 | 2T2026 | 46 | **ok_3_anos** | nenhuma |
| `/v1/nip` | `consumo_ans.consumo_nip.trimestre` | trimestral | 53637 | 1T2011 | 4T2020 | 40 | **ok_3_anos** | nenhuma |
| `/v1/idss` | `consumo_ans.consumo_idss.ano_base` | anual | 13072 | 2012 | 2025 | 14 | **ok_3_anos** | nenhuma |
| `/v1/financeiro` | `consumo_ans.consumo_financeiro_operadora_trimestre.trimestre` | trimestral | 10978 | 4T2022 | 4T2025 | 13 | **ok_3_anos** | nenhuma |
| `/v1/prudencial` | `consumo_ans.consumo_prudencial_operadora_trimestral.trimestre` | trimestral | 11216 | 1T2024 | 2T2026 | 10 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/glosa` | `consumo_ans.consumo_glosa_operadora_mensal.competencia` | mensal | 844 | 202501 | 202501 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/regime-especial` | `consumo_ans.consumo_regime_especial_operadora_trimestral.trimestre` | trimestral | 117 | 1T2002 | 1T2025 | 20 | **ok_3_anos** | nenhuma |
| `/v1/mercado/municipio` | `api_ans.api_market_share_mensal.competencia` | mensal | 59197 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/mercado/vazio-assistencial` | `api_ans.api_vazio_assistencial.competencia` | mensal | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
| `/v1/rankings/operadora/score` | `api_ans.api_ranking_score.competencia` | mensal | 757 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/rankings/operadora/crescimento` | `api_ans.api_ranking_crescimento.competencia` | mensal | 757 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/rankings/municipio/oportunidade` | `api_ans.api_ranking_oportunidade.competencia` | mensal | 646 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/rankings/municipio/oportunidade-v2` | `api_ans.api_oportunidade_v2_municipio_mensal.competencia` | mensal | 646 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/rankings/composto` | `api_ans.api_ranking_composto_mensal.competencia_id` | mensal | 757 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/cnes/municipio/{cd_municipio}` | `api_ans.api_cnes_municipio.competencia` | mensal | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
| `/v1/cnes/uf/{sg_uf}` | `api_ans.api_cnes_municipio.competencia` | mensal | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
| `/v1/rede/municipio/{cd_municipio}` | `api_ans.api_rede_assistencial.competencia` | mensal | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
| `/v1/regulatorio/rn623` | `api_ans.api_rn623_lista_trimestral.trimestre` | trimestral | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
| `/v1/operadoras/{registro_ans}/financeiro` | `consumo_ans.consumo_financeiro_operadora_trimestre.trimestre` | trimestral | 10978 | 4T2022 | 4T2025 | 13 | **ok_3_anos** | nenhuma |
| `/v1/operadoras/{registro_ans}/regulatorio` | `consumo_ans.consumo_regulatorio_operadora_trimestre.trimestre` | trimestral | 161173 | 1T2011 | 2T2026 | 62 | **ok_3_anos** | nenhuma |
| `/v1/operadoras/{registro_ans}/score-v3/historico` | `api_ans.api_score_v3_operadora_mensal.competencia_id` | mensal | 757 | 202603 | 202603 | 1 | **parcial** | executar backfill real ou ocultar como disponivel no catalogo publico |
| `/v1/operadoras/{registro_ans}/portabilidade` | `api_ans.api_portabilidade_operadora_mensal.competencia` | mensal | 0 |  |  | 0 | **vazio** | manter roadmap/fora do catalogo disponivel ate carga real produzir linhas |
