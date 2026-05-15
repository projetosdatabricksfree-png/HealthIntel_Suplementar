# Evidencia - hard gate consumo_ans comercial

- Validado em: 2026-05-15T20:21:56.736027+00:00
- Schema: `consumo_ans`
- Banco consultado: sim
- Resultado: SUCESSO

## Resumo por status

| status | tabelas |
|---|---:|
| disponivel | 12 |
| fora_do_escopo | 1 |
| parcial | 5 |
| vazia_bloqueada | 8 |

## Status por dominio

| dominio | status | tabelas |
|---|---|---:|
| cnes_rede_assistencial | vazia_bloqueada | 2 |
| financeiro | disponivel | 1 |
| glosa | disponivel | 1 |
| ntrp | vazia_bloqueada | 1 |
| produto_plano | disponivel | 2 |
| produto_plano | vazia_bloqueada | 1 |
| prudencial | disponivel | 1 |
| regime_especial | disponivel | 1 |
| regulatorio | disponivel | 5 |
| regulatorio | vazia_bloqueada | 1 |
| ressarcimento | vazia_bloqueada | 1 |
| sib | parcial | 5 |
| sib | vazia_bloqueada | 1 |
| sip | vazia_bloqueada | 1 |
| tiss | fora_do_escopo | 1 |
| tuss | disponivel | 1 |

## Tabelas

| tabela | dominio | status | linhas |
|---|---|---|---:|
| `consumo_ans.consumo_produto_plano` | produto_plano | disponivel | 163661 |
| `consumo_ans.consumo_historico_plano` | produto_plano | disponivel | 163567 |
| `consumo_ans.consumo_regulatorio_operadora_trimestre` | regulatorio | disponivel | 161173 |
| `consumo_ans.consumo_igr` | regulatorio | disponivel | 136908 |
| `consumo_ans.consumo_nip` | regulatorio | disponivel | 53637 |
| `consumo_ans.consumo_idss` | regulatorio | disponivel | 13072 |
| `consumo_ans.consumo_taxa_resolutividade_operadora_trimestral` | regulatorio | disponivel | 26062 |
| `consumo_ans.consumo_prudencial_operadora_trimestral` | prudencial | disponivel | 11216 |
| `consumo_ans.consumo_financeiro_operadora_trimestre` | financeiro | disponivel | 10978 |
| `consumo_ans.consumo_glosa_operadora_mensal` | glosa | disponivel | 844 |
| `consumo_ans.consumo_tuss_procedimento_vigente` | tuss | disponivel | 64654 |
| `consumo_ans.consumo_regime_especial_operadora_trimestral` | regime_especial | disponivel | 117 |
| `consumo_ans.consumo_rede_assistencial_municipio` | cnes_rede_assistencial | vazia_bloqueada | 0 |
| `consumo_ans.consumo_sip_assistencial_operadora` | sip | vazia_bloqueada | 0 |
| `consumo_ans.consumo_precificacao_plano` | ntrp | vazia_bloqueada | 0 |
| `consumo_ans.consumo_ressarcimento_sus_operadora` | ressarcimento | vazia_bloqueada | 0 |
| `consumo_ans.consumo_beneficiarios_operadora_mes` | sib | parcial | 757 |
| `consumo_ans.consumo_beneficiarios_municipio_mes` | sib | parcial | 646 |
| `consumo_ans.consumo_oportunidade_municipio` | sib | parcial | 646 |
| `consumo_ans.consumo_operadora_360` | sib | parcial | 757 |
| `consumo_ans.consumo_score_operadora_mes` | sib | parcial | 757 |
| `consumo_ans.consumo_beneficiarios_cobertura_municipio` | sib | vazia_bloqueada | 0 |
| `consumo_ans.consumo_tiss_utilizacao_operadora_mes` | tiss | fora_do_escopo | 0 |
| `consumo_ans.consumo_plano_servico_opcional` | produto_plano | vazia_bloqueada | 0 |
| `consumo_ans.consumo_rede_acreditacao` | cnes_rede_assistencial | vazia_bloqueada | 0 |
| `consumo_ans.consumo_regulatorio_complementar_operadora` | regulatorio | vazia_bloqueada | 0 |

## Conclusao comercial

Catalogo comercial apto para entrega honesta a clientes de BI/analytics.
