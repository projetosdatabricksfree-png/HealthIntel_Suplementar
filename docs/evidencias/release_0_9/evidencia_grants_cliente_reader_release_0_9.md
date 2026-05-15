# Evidencia — Auditoria empirica de grants healthintel_cliente_reader

- Gerado em: 2026-05-15T22:28:26.839542+00:00
- Resultado: SUCESSO
- Tabelas acessiveis (SELECT): 12
- Schemas internos testados: 11
- Tabelas disponivel testadas: 12

## 1. Tabelas acessiveis (information_schema.role_table_grants)

| schema | tabela |
|---|---|
| `consumo_ans` | `consumo_financeiro_operadora_trimestre` |
| `consumo_ans` | `consumo_glosa_operadora_mensal` |
| `consumo_ans` | `consumo_historico_plano` |
| `consumo_ans` | `consumo_idss` |
| `consumo_ans` | `consumo_igr` |
| `consumo_ans` | `consumo_nip` |
| `consumo_ans` | `consumo_produto_plano` |
| `consumo_ans` | `consumo_prudencial_operadora_trimestral` |
| `consumo_ans` | `consumo_regime_especial_operadora_trimestral` |
| `consumo_ans` | `consumo_regulatorio_operadora_trimestre` |
| `consumo_ans` | `consumo_taxa_resolutividade_operadora_trimestral` |
| `consumo_ans` | `consumo_tuss_procedimento_vigente` |

## 2. Schemas internos — testes de bloqueio (espera 42501)

| schema | tabela testada | resultado |
|---|---|---|
| `bruto_ans` | `rn623_lista_operadora_trimestral` | ✅ OK bloqueado (42501) |
| `stg_ans` | `stg_operadora_cancelada` | ✅ OK bloqueado (42501) |
| `nucleo_ans` | `fat_sinistralidade_procedimento` | ✅ OK bloqueado (42501) |
| `api_ans` | `api_bronze_vda` | ✅ OK bloqueado (42501) |
| `plataforma` | `execucao_layout` | ✅ OK bloqueado (42501) |
| `mdm_ans` | `mdm_operadora_master` | ✅ OK bloqueado (42501) |
| `mdm_privado` | `xref_contrato_origem` | ✅ OK bloqueado (42501) |
| `quality_ans` | `dq_prestador_documento` | ✅ OK bloqueado (42501) |
| `bruto_cliente` | `contrato` | ✅ OK bloqueado (42501) |
| `stg_cliente` | `stg_cliente_subfatura` | ✅ OK bloqueado (42501) |
| `consumo_premium_ans` | `consumo_premium_contrato_subfatura_operadora` | ✅ OK bloqueado (42501) |

## 3. Tabelas disponivel — testes de permissao (espera SELECT ok)

| tabela | resultado |
|---|---|
| `consumo_ans.consumo_produto_plano` | ✅ OK 163661 linhas |
| `consumo_ans.consumo_historico_plano` | ✅ OK 163567 linhas |
| `consumo_ans.consumo_regulatorio_operadora_trimestre` | ✅ OK 161173 linhas |
| `consumo_ans.consumo_igr` | ✅ OK 136908 linhas |
| `consumo_ans.consumo_nip` | ✅ OK 53637 linhas |
| `consumo_ans.consumo_idss` | ✅ OK 13072 linhas |
| `consumo_ans.consumo_taxa_resolutividade_operadora_trimestral` | ✅ OK 26062 linhas |
| `consumo_ans.consumo_prudencial_operadora_trimestral` | ✅ OK 11216 linhas |
| `consumo_ans.consumo_financeiro_operadora_trimestre` | ✅ OK 10978 linhas |
| `consumo_ans.consumo_glosa_operadora_mensal` | ✅ OK 844 linhas |
| `consumo_ans.consumo_tuss_procedimento_vigente` | ✅ OK 64654 linhas |
| `consumo_ans.consumo_regime_especial_operadora_trimestral` | ✅ OK 117 linhas |

## 4. Conclusao

Cliente reader bloqueia 100% dos schemas internos e libera 100% das tabelas disponivel do catalogo. Release 0.9 apta para piloto comercial.

