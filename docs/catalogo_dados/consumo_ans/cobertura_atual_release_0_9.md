# Cobertura atual — Release 0.9 Core ANS

**Tag**: `v0.9.0-core-ans`
**Schema cliente**: `consumo_ans`
**Catálogo versionado**: `catalogo_consumo_ans.yml`
**Hard gate**: `scripts/auditoria/validar_consumo_ans_comercial.py`

A HealthIntel entrega um **Core ANS curado** para BI/SQL/API com tabelas
comerciais governadas, acesso controlado, documentação, testes e bloqueio
automático contra exposição de dados vazios ou incompletos.

---

## 1. Domínios disponíveis (12 tabelas — `status: disponivel`)

Todas com dados reais, populadas a partir de PDA ANS, fonte rastreada, granularidade
documentada e teste dbt mínimo.

| Domínio | Tabela `consumo_ans.*` | Fonte ANS | Periodicidade | Granularidade |
|---|---|---|---|---|
| **Produtos e planos** | `consumo_produto_plano` | PDA — características de produtos | mensal | registro_ans + codigo_produto + competencia |
| **Histórico de planos** | `consumo_historico_plano` | PDA — histórico de planos | mensal | registro_ans + codigo_plano + competencia |
| **Regulatório agregado** | `consumo_regulatorio_operadora_trimestre` | PDA — NIP + IGR + taxa resolutividade | trimestral | registro_ans + trimestre |
| **IGR** | `consumo_igr` | PDA — IGR | trimestral | registro_ans + trimestre |
| **NIP** | `consumo_nip` | PDA — NIP | trimestral | registro_ans + trimestre |
| **IDSS** | `consumo_idss` | PDA — IDSS anual | anual | registro_ans + ano_base |
| **Taxa de resolutividade** | `consumo_taxa_resolutividade_operadora_trimestral` | PDA — taxa de resolutividade | trimestral | registro_ans + trimestre |
| **Indicadores prudenciais** | `consumo_prudencial_operadora_trimestral` | PDA — indicadores prudenciais | trimestral | registro_ans + trimestre |
| **Financeiro** | `consumo_financeiro_operadora_trimestre` | PDA — DIOPS/FIP | trimestral | registro_ans + trimestre |
| **Glosa** | `consumo_glosa_operadora_mensal` | PDA — glosa | mensal | registro_ans + competencia + tipo_glosa |
| **TUSS oficial vigente** | `consumo_tuss_procedimento_vigente` | PDA — TUSS oficial | versão vigente | codigo_tuss |
| **Regime especial** | `consumo_regime_especial_operadora_trimestral` | PDA — regime especial | trimestral | registro_ans + trimestre + tipo_regime |

**Acesso**: role `healthintel_cliente_reader`, schema `consumo_ans` (SQL direto + DaaS).

---

## 2. Domínios parciais (5 tabelas — `status: parcial`)

Dependências de SIB. **Não publicáveis** como produto completo, mas existem em
preview interno. Não aparecem para cliente externo.

| Tabela | Limitação |
|---|---|
| `consumo_beneficiarios_operadora_mes` | depende de SIB; fora do escopo desta release |
| `consumo_beneficiarios_municipio_mes` | depende de SIB; fora do escopo desta release |
| `consumo_oportunidade_municipio` | métricas de beneficiários dependem de SIB |
| `consumo_operadora_360` | colunas de beneficiários e scores derivados dependem de SIB |
| `consumo_score_operadora_mes` | componente core e métricas de beneficiários dependem de SIB |

---

## 3. Domínios bloqueados (8 tabelas — `status: vazia_bloqueada`)

Estrutura criada mas **sem dados reais** ainda. **Não aparecem no catálogo
comercial**. Roadmap para sprints futuras.

| Tabela | Motivo |
|---|---|
| `consumo_rede_assistencial_municipio` | CNES bloqueado por fonte DataSUS retornando 404 |
| `consumo_sip_assistencial_operadora` | tabela zerada na validação real (parser SIP) |
| `consumo_precificacao_plano` | carga NTRP não produz linhas ainda |
| `consumo_ressarcimento_sus_operadora` | carga ressarcimento bloqueada |
| `consumo_beneficiarios_cobertura_municipio` | cobertura depende de SIB |
| `consumo_plano_servico_opcional` | aguarda carga real não vazia |
| `consumo_rede_acreditacao` | aguarda carga real não vazia |
| `consumo_regulatorio_complementar_operadora` | IAP/PFA aguardam carga real |

---

## 4. Fora do escopo (1 tabela — `status: fora_do_escopo`)

| Tabela | Motivo |
|---|---|
| `consumo_tiss_utilizacao_operadora_mes` | **TISS explicitamente fora do escopo desta release.** Não prometido a clientes. |

---

## 5. O que NÃO está incluso

- ❌ **TISS** (todas as subfamílias) — fora do escopo da Release 0.9.
- ❌ **SIB histórico completo** — apenas tabelas SIB parciais, sem promessa de cobertura completa.
- ❌ **CNES rede assistencial detalhada** — fonte DataSUS bloqueada.
- ❌ **NTRP / precificação detalhada** — carga ainda não produz dados.
- ❌ **Ressarcimento SUS detalhado** — em roadmap.
- ❌ **Glosa detalhada por procedimento** — apenas mensal agregada.

---

## 6. SLA e atualização

| Domínio | Frequência de atualização | Janela de carga |
|---|---|---|
| Produtos/planos | mensal | até D+5 do mês |
| Regulatório (NIP/IGR/IDSS/Resolutividade) | trimestral | até D+15 do trimestre |
| Financeiro | trimestral | após publicação DIOPS/FIP pela ANS |
| Glosa | mensal | conforme disponibilidade ANS |
| TUSS | versão vigente | mediante publicação ANS |
| Regime especial | trimestral | conforme publicação ANS |

---

## 7. Roadmap (não-comercial — para alinhamento interno)

| Domínio | Sprint alvo |
|---|---|
| Popular CNES (rede assistencial municipio) | Sprint 45 |
| Popular SIP delta (parser + carga) | Sprint 45 |
| Popular NTRP (precificação) | Sprint 46 |
| Popular ressarcimento SUS | Sprint 46 |
| Popular regulatório complementar (IAP, PFA) | Sprint 47 |
| Avaliar SIB cobertura (parcial → disponível) | Sprint 48 |
| TISS (fora do escopo) | Não roteirizado |
