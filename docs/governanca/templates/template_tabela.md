# Template de Documentação de Tabela

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Template oficial para documentar toda tabela da plataforma HealthIntel Suplementar.

---

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome_fisico` | Nome físico no PostgreSQL | `api_premium_operadora_360_validado` |
| `schema` | Schema PostgreSQL | `api_ans` |
| `camada` | Camada oficial | `api_ans` |
| `tipo_artefato` | Tabela, view, materialized view, seed, snapshot | `table` |
| `descricao` | Descrição funcional em português | "Operadoras com score 360 validado" |
| `origem` | Fonte primária dos dados | `ANS — CADOP, DIOPS, SIB, TISS` |
| `finalidade` | Propósito de negócio | "Visão 360 para consumo premium" |
| `granularidade` | Grão da tabela | `Uma linha por operadora por competência` |
| `chave_natural` | Coluna(s) do negócio | `registro_ans, competencia` |
| `chave_surrogate` | Surrogate key | `operadora_master_id` |
| `upstream` | Tabelas fonte | `mdm_ans.mdm_operadora_master` |
| `downstream` | Consumidores | `api/app/routers/premium.py` |
| `status_publicacao` | `interno`, `publico`, `premium`, `restrito` | `premium` |
| `sensibilidade_lgpd` | `publico`, `interno`, `restrito`, `pessoal`, `sensivel` | `publico` |
| `owner_tecnico` | Time responsável | `Engenharia de Dados` |
| `owner_negocio` | Área de negócio | `Produto HealthIntel` |
| `sla_atualizacao` | Frequência | `Mensal (D+5)` |
| `regra_atualizacao` | `full_refresh`, `incremental`, `snapshot` | `incremental` |
| `regra_retencao` | Política de retenção | `60 competências` |
| `data_criacao` | Data de criação | `2026-04-27` |
| `data_alteracao` | Última alteração | `2026-04-27` |
| `status` | `ativo`, `deprecated`, `removido` | `ativo` |

---

## Exemplo Preenchido

### `api_ans.api_premium_operadora_360_validado`

| Campo | Valor |
|-------|-------|
| nome_fisico | `api_premium_operadora_360_validado` |
| schema | `api_ans` |
| camada | `api_ans` |
| tipo_artefato | `table` |
| descricao | Operadoras com score 360 validado |
| origem | CADOP, DIOPS, SIB, TISS; quality_ans; mdm_ans |
| finalidade | Visão 360 premium |
| granularidade | Uma linha por operadora por competência |
| chave_natural | `registro_ans, competencia` |
| chave_surrogate | `operadora_master_id` |
| upstream | `mdm_ans.mdm_operadora_master`, `quality_ans.quality_operadora_360` |
| downstream | `/v1/premium/operadoras` |
| status_publicacao | `premium` |
| sensibilidade_lgpd | `publico` |
| owner_tecnico | Engenharia de Dados |
| owner_negocio | Produto HealthIntel |
| sla_atualizacao | Mensal (D+5) |
| regra_atualizacao | `incremental` |
| regra_retencao | 60 competências |
| data_criacao | 2026-04-15 |
| data_alteracao | 2026-04-15 |
| status | ativo |

---

## Checklist de Validação

- [ ] Todos os campos obrigatórios preenchidos
- [ ] Nome físico corresponde ao artefato no banco
- [ ] Schema corresponde ao schema físico
- [ ] Camada está na lista de camadas oficiais
- [ ] Status de publicação coerente com a camada
- [ ] Sensibilidade LGPD classificada
- [ ] Owner técnico e de negócio definidos
- [ ] Data de criação preenchida