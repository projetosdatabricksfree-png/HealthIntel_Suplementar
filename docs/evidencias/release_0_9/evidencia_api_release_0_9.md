# Evidencia — Auditoria API Release 0.9

- Gerado em: 2026-05-15T22:28:27.007982+00:00
- Repo: `/opt/healthintel`
- Routers analisados: 19
- Endpoints totais: 93
- Decisao **publicar**: 42
- Decisao **publicar_parcial**: 44
- Decisao **ocultar**: 7

## Resumo por router

| router | n_endpoints | decisao | tabelas referenciadas |
|---|---:|---|---|
| `admin_billing` | 4 | **publicar_router_inteiro** | — |
| `admin_debug` | 1 | **publicar_router_inteiro** | — |
| `admin_layout` | 9 | **publicar_router_inteiro** | — |
| `bronze` | 11 | **publicar_router_inteiro** | `api_ans.api_bronze_cadop` (?), `api_ans.api_bronze_diops` (?), `api_ans.api_bronze_fip` (?), `api_ans.api_bronze_glosa` (?), `api_ans.api_bronze_idss` (?), `api_ans.api_bronze_igr` (?), `api_ans.api_bronze_nip` (?), `api_ans.api_bronze_rede_assistencial` (?), `api_ans.api_bronze_sib_municipio` (?), `api_ans.api_bronze_sib_operadora` (?), `api_ans.api_bronze_vda` (?) |
| `cnes` | 2 | **ocultar_router_inteiro** | `api_ans.api_cnes_municipio` (0) |
| `financeiro` | 2 | **filtrar_por_endpoint** | `api_ans.api_score_v2_operadora_mensal` (757), `consumo_ans.consumo_financeiro_operadora_trimestre` (0) |
| `mercado` | 2 | **filtrar_por_endpoint** | `api_ans.api_market_share_mensal` (59197), `api_ans.api_vazio_assistencial` (0) |
| `meta` | 7 | **filtrar_por_endpoint** | `api_ans.api_bronze_cadop` (?), `api_ans.api_bronze_diops` (?), `api_ans.api_bronze_fip` (?), `api_ans.api_bronze_glosa` (?), `api_ans.api_bronze_idss` (?), `api_ans.api_bronze_igr` (?), `api_ans.api_bronze_nip` (?), `api_ans.api_bronze_rede_assistencial` (?), `api_ans.api_bronze_sib_municipio` (?), `api_ans.api_bronze_sib_operadora` (?), `api_ans.api_bronze_vda` (?), `api_ans.api_cnes_municipio` (0), `api_ans.api_cnes_rede_gap` (0), `api_ans.api_financeiro_operadora_mensal` (0), `api_ans.api_market_share_mensal` (59197), `api_ans.api_operadora` (1107), `api_ans.api_oportunidade_v2_municipio_mensal` (646), `api_ans.api_portabilidade_operadora_mensal` (0), `api_ans.api_prata_cadop` (1107), `api_ans.api_prata_diops` (0), `api_ans.api_prata_financeiro_periodo` (0), `api_ans.api_prata_fip` (0), `api_ans.api_prata_glosa` (0), `api_ans.api_prata_idss` (0), `api_ans.api_prata_igr` (0), `api_ans.api_prata_municipio_metrica` (59197), `api_ans.api_prata_nip` (0), `api_ans.api_prata_operadora_enriquecida` (757), `api_ans.api_prata_rede_assistencial` (0), `api_ans.api_prata_sib_municipio` (59892), `api_ans.api_prata_sib_operadora` (803), `api_ans.api_prata_vda` (0), `api_ans.api_premium_cnes_estabelecimento_validado` (0), `api_ans.api_premium_operadora_360_validado` (757), `api_ans.api_premium_quality_dataset` (2), `api_ans.api_ranking_composto_mensal` (757), `api_ans.api_ranking_crescimento` (757), `api_ans.api_ranking_oportunidade` (646), `api_ans.api_ranking_score` (757), `api_ans.api_rede_assistencial` (0), `api_ans.api_regime_especial_operadora` (0), `api_ans.api_score_operadora_mensal` (757), `api_ans.api_score_regulatorio_operadora_mensal` (0), `api_ans.api_score_v2_operadora_mensal` (757), `api_ans.api_score_v3_operadora_mensal` (757), `api_ans.api_sinistralidade_procedimento` (0), `api_ans.api_tiss_operadora_trimestral` (0), `api_ans.api_vazio_assistencial` (0) |
| `operadora` | 7 | **publicar_router_inteiro** | `api_ans.api_operadora` (1107), `api_ans.api_score_operadora_mensal` (757), `consumo_ans.consumo_beneficiarios_operadora_mes` (757) |
| `prata` | 19 | **filtrar_por_endpoint** | `api_ans.api_prata_cadop` (1107), `api_ans.api_prata_cnes_municipio` (0), `api_ans.api_prata_cnes_rede_gap` (0), `api_ans.api_prata_diops` (0), `api_ans.api_prata_financeiro_periodo` (0), `api_ans.api_prata_fip` (0), `api_ans.api_prata_glosa` (0), `api_ans.api_prata_idss` (0), `api_ans.api_prata_igr` (0), `api_ans.api_prata_municipio_metrica` (59197), `api_ans.api_prata_nip` (0), `api_ans.api_prata_operadora_enriquecida` (757), `api_ans.api_prata_rede_assistencial` (0), `api_ans.api_prata_sib_municipio` (59892), `api_ans.api_prata_sib_operadora` (803), `api_ans.api_prata_tiss_procedimento` (0), `api_ans.api_prata_vda` (0) |
| `premium` | 9 | **filtrar_por_endpoint** | `api_ans.api_premium_cnes_estabelecimento_validado` (0), `api_ans.api_premium_contrato_validado` (0), `api_ans.api_premium_mdm_operadora` (1107), `api_ans.api_premium_mdm_prestador` (0), `api_ans.api_premium_operadora_360_validado` (757), `api_ans.api_premium_quality_dataset` (2), `api_ans.api_premium_subfatura_validada` (0), `api_ans.api_premium_tiss_procedimento_tuss_validado` (0), `api_ans.api_premium_tuss_procedimento` (3500) |
| `produto` | 3 | **publicar_router_inteiro** | `api_ans.api_historico_plano` (163567), `api_ans.api_produto_plano` (163661) |
| `public_checkout` | 1 | **publicar_router_inteiro** | — |
| `ranking` | 5 | **publicar_router_inteiro** | `api_ans.api_oportunidade_v2_municipio_mensal` (646), `api_ans.api_ranking_composto_mensal` (757), `api_ans.api_ranking_crescimento` (757), `api_ans.api_ranking_oportunidade` (646), `api_ans.api_ranking_score` (757) |
| `rede` | 1 | **ocultar_router_inteiro** | `api_ans.api_rede_assistencial` (0) |
| `regulatorio` | 1 | **ocultar_router_inteiro** | `api_ans.api_portabilidade_operadora_mensal` (0), `api_ans.api_regime_especial_operadora_trimestral` (?), `api_ans.api_regulatorio_operadora_trimestral` (0), `api_ans.api_rn623_lista_trimestral` (0), `api_ans.api_score_regulatorio_operadora_mensal` (0) |
| `regulatorio_v2` | 3 | **ocultar_router_inteiro** | `api_ans.api_portabilidade_operadora_mensal` (0), `api_ans.api_regime_especial_operadora_trimestral` (?), `api_ans.api_score_regulatorio_operadora_mensal` (0) |
| `status_page` | 1 | **publicar_router_inteiro** | — |
| `tiss` | 5 | **filtrar_por_endpoint** | `api_ans.api_cnes_rede_gap` (0), `api_ans.api_sinistralidade_procedimento` (0), `api_ans.api_tiss_operadora_trimestral` (0), `api_ans.api_tuss_procedimento_vigente` (64654) |

## Endpoints detalhados

### `admin_billing.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/resumo` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/fechar-ciclo` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/upgrade` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/clientes/{cliente_id}/chaves` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |

### `admin_debug.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| POST | `/_debug/raise` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |

### `admin_layout.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| POST | `/{layout_id}/versoes` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/{layout_id}/aliases` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| GET | `/incompativeis` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| GET | `/{layout_id}` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/validar-arquivo` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/{layout_id}/aprovar` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/{layout_id}/desativar` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/{layout_id}/reativar` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |
| POST | `/reprocessar` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |

### `bronze.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/cadop` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/sib/operadora` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/sib/municipio` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/igr` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/nip` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/idss` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/diops` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/fip` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/vda` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/glosa` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |
| GET | `/rede-assistencial` | **publicar** | tabelas nao mapeadas no inventario: api_ans.api_bronze_cadop, api_ans.api_bronze_diops, api_ans.api_bronze_fip, api_ans.api_bronze_glosa, api_ans.api_bronze_idss, api_ans.api_bronze_igr, api_ans.api_bronze_nip, api_ans.api_bronze_rede_assistencial, api_ans.api_bronze_sib_municipio, api_ans.api_bronze_sib_operadora, api_ans.api_bronze_vda (presumir publicar; revisar manualmente) |

### `cnes.py` — ocultar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/municipio/{cd_municipio}` | **ocultar** | todas tabelas zeradas: api_ans.api_cnes_municipio |
| GET | `/uf/{sg_uf}` | **ocultar** | todas tabelas zeradas: api_ans.api_cnes_municipio |

### `financeiro.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/{registro_ans}/financeiro` | **publicar_parcial** | populadas: api_ans.api_score_v2_operadora_mensal; zeradas: consumo_ans.consumo_financeiro_operadora_trimestre |
| GET | `/{registro_ans}/score-v2` | **publicar_parcial** | populadas: api_ans.api_score_v2_operadora_mensal; zeradas: consumo_ans.consumo_financeiro_operadora_trimestre |

### `mercado.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/municipio` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal; zeradas: api_ans.api_vazio_assistencial |
| GET | `/vazio-assistencial` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal; zeradas: api_ans.api_vazio_assistencial |

### `meta.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/datasets` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/dataset` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/atualizacao` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/qualidade` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/versao` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/pipeline` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |
| GET | `/endpoints` | **publicar_parcial** | populadas: api_ans.api_market_share_mensal, api_ans.api_operadora, api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score, api_ans.api_score_operadora_mensal, api_ans.api_score_v2_operadora_mensal, api_ans.api_score_v3_operadora_mensal; zeradas: api_ans.api_cnes_municipio, api_ans.api_cnes_rede_gap, api_ans.api_financeiro_operadora_mensal, api_ans.api_portabilidade_operadora_mensal, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_vda, api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_rede_assistencial, api_ans.api_regime_especial_operadora, api_ans.api_score_regulatorio_operadora_mensal, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral, api_ans.api_vazio_assistencial |

### `operadora.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/{registro_ans}` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/score` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/beneficiarios` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/regulatorio` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/rede` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/score-v3` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |
| GET | `/{registro_ans}/score-v3/historico` | **publicar** | todas tabelas populadas: api_ans.api_operadora, api_ans.api_score_operadora_mensal, consumo_ans.consumo_beneficiarios_operadora_mes |

### `prata.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/cadop` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/sib/operadora` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/sib/municipio` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/igr` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/nip` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/idss` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/diops` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/fip` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/vda` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/glosa` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/rede-assistencial` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/operadora/enriquecida` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/municipio/metrica` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/financeiro/periodo` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/cnes/municipio` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/cnes/rede-gap` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/tiss/procedimento` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/quarentena/resumo` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |
| GET | `/quarentena/{dataset}` | **publicar_parcial** | populadas: api_ans.api_prata_cadop, api_ans.api_prata_municipio_metrica, api_ans.api_prata_operadora_enriquecida, api_ans.api_prata_sib_municipio, api_ans.api_prata_sib_operadora; zeradas: api_ans.api_prata_cnes_municipio, api_ans.api_prata_cnes_rede_gap, api_ans.api_prata_diops, api_ans.api_prata_financeiro_periodo, api_ans.api_prata_fip, api_ans.api_prata_glosa, api_ans.api_prata_idss, api_ans.api_prata_igr, api_ans.api_prata_nip, api_ans.api_prata_rede_assistencial, api_ans.api_prata_tiss_procedimento, api_ans.api_prata_vda |

### `premium.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/operadoras` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/cnes/estabelecimentos` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/tiss/procedimentos` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/tuss/procedimentos` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/mdm/operadoras` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/mdm/prestadores` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/contratos` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/subfaturas` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |
| GET | `/quality/datasets` | **publicar_parcial** | populadas: api_ans.api_premium_mdm_operadora, api_ans.api_premium_operadora_360_validado, api_ans.api_premium_quality_dataset, api_ans.api_premium_tuss_procedimento; zeradas: api_ans.api_premium_cnes_estabelecimento_validado, api_ans.api_premium_contrato_validado, api_ans.api_premium_mdm_prestador, api_ans.api_premium_subfatura_validada, api_ans.api_premium_tiss_procedimento_tuss_validado |

### `produto.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/planos` | **publicar** | todas tabelas populadas: api_ans.api_historico_plano, api_ans.api_produto_plano |
| GET | `/planos/{codigo_plano}` | **publicar** | todas tabelas populadas: api_ans.api_historico_plano, api_ans.api_produto_plano |
| GET | `/historico` | **publicar** | todas tabelas populadas: api_ans.api_historico_plano, api_ans.api_produto_plano |

### `public_checkout.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| POST | `/confirmar` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |

### `ranking.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/operadora/score` | **publicar** | todas tabelas populadas: api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score |
| GET | `/operadora/crescimento` | **publicar** | todas tabelas populadas: api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score |
| GET | `/municipio/oportunidade` | **publicar** | todas tabelas populadas: api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score |
| GET | `/municipio/oportunidade-v2` | **publicar** | todas tabelas populadas: api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score |
| GET | `/composto` | **publicar** | todas tabelas populadas: api_ans.api_oportunidade_v2_municipio_mensal, api_ans.api_ranking_composto_mensal, api_ans.api_ranking_crescimento, api_ans.api_ranking_oportunidade, api_ans.api_ranking_score |

### `rede.py` — ocultar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/municipio/{cd_municipio}` | **ocultar** | todas tabelas zeradas: api_ans.api_rede_assistencial |

### `regulatorio.py` — ocultar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/rn623` | **ocultar** | todas tabelas zeradas: api_ans.api_portabilidade_operadora_mensal, api_ans.api_regulatorio_operadora_trimestral, api_ans.api_rn623_lista_trimestral, api_ans.api_score_regulatorio_operadora_mensal |

### `regulatorio_v2.py` — ocultar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/{registro_ans}/score-regulatorio` | **ocultar** | todas tabelas zeradas: api_ans.api_portabilidade_operadora_mensal, api_ans.api_score_regulatorio_operadora_mensal |
| GET | `/{registro_ans}/regime-especial` | **ocultar** | todas tabelas zeradas: api_ans.api_portabilidade_operadora_mensal, api_ans.api_score_regulatorio_operadora_mensal |
| GET | `/{registro_ans}/portabilidade` | **ocultar** | todas tabelas zeradas: api_ans.api_portabilidade_operadora_mensal, api_ans.api_score_regulatorio_operadora_mensal |

### `status_page.py` — publicar_router_inteiro

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/status` | **publicar** | endpoint sem tabela de dados (utilitario/meta) |

### `tiss.py` — filtrar_por_endpoint

| method | path | decisao | motivo |
|---|---|---|---|
| GET | `/tiss/{registro_ans}/procedimentos` | **publicar_parcial** | populadas: api_ans.api_tuss_procedimento_vigente; zeradas: api_ans.api_cnes_rede_gap, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral |
| GET | `/tuss/procedimentos` | **publicar_parcial** | populadas: api_ans.api_tuss_procedimento_vigente; zeradas: api_ans.api_cnes_rede_gap, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral |
| GET | `/tuss/procedimentos/{codigo_tuss}` | **publicar_parcial** | populadas: api_ans.api_tuss_procedimento_vigente; zeradas: api_ans.api_cnes_rede_gap, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral |
| GET | `/tiss/{registro_ans}/sinistralidade` | **publicar_parcial** | populadas: api_ans.api_tuss_procedimento_vigente; zeradas: api_ans.api_cnes_rede_gap, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral |
| GET | `/rede/gap/{cd_municipio}` | **publicar_parcial** | populadas: api_ans.api_tuss_procedimento_vigente; zeradas: api_ans.api_cnes_rede_gap, api_ans.api_sinistralidade_procedimento, api_ans.api_tiss_operadora_trimestral |

## Acoes recomendadas

Routers a ocultar inteiramente do Swagger (include_in_schema=False no include_router):

- `app.include_router(cnes.router, ..., include_in_schema=False)`
- `app.include_router(rede.router, ..., include_in_schema=False)`
- `app.include_router(regulatorio.router, ..., include_in_schema=False)`
- `app.include_router(regulatorio_v2.router, ..., include_in_schema=False)`

Routers que precisam filtro por endpoint (alguns publicar, outros ocultar):

- `financeiro.py`:
- `mercado.py`:
- `meta.py`:
- `prata.py`:
- `premium.py`:
- `tiss.py`:
