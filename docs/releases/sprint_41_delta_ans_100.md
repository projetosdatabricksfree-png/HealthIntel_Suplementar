# Release Notes — Sprint 41: Delta ANS 100%

Data: 2026-05-11  
Commit: `bb5e8fe`  
Branch: `main`

---

## Objetivo

Implementar os datasets ANS que ainda não existiam no projeto, atingindo cobertura 100% do repositório público ANS, sem mexer em modelos, routers, schemas ou tabelas existentes.

---

## Datasets adicionados

### 1. Produtos e planos
- `produto_caracteristica` — características de produtos de saúde suplementar
- `produto_tabela_auxiliar` — tabelas auxiliares associadas
- `historico_plano` — histórico de planos de saúde
- `plano_servico_opcional` — serviços opcionais dos planos
- `quadro_auxiliar_corresponsabilidade` — quadros auxiliares de corresponsabilidade

### 2. TUSS oficial
- `tuss_terminologia_oficial` — TUSS carregado a partir de `TUSS.zip` oficial ANS
- API: `api_tuss_procedimento_vigente` (filtrado por `is_tuss_vigente = true`)

### 3. TISS por subfamília
- `tiss_ambulatorial` — dados TISS/AMBULATORIAL
- `tiss_hospitalar` — dados TISS/HOSPITALAR
- `tiss_dados_plano` — dados TISS/DADOS_DE_PLANOS
- Janela de retenção: 24 meses nas tabelas API/consumo

### 4. SIP
- `sip_mapa_assistencial` — Mapa Assistencial

### 5. Ressarcimento ao SUS
- `ressarcimento_beneficiario_abi` — beneficiários identificados SUS/ABI
- `ressarcimento_sus_operadora_plano` — dados por operadora/plano
- `ressarcimento_hc` — HC Ressarcimento SUS
- `ressarcimento_cobranca_arrecadacao` — cobrança e arrecadação
- `ressarcimento_indice_pagamento` — índice de efetivo pagamento

### 6. Precificação, NTRP e reajustes
- `ntrp_area_comercializacao` — área de comercialização NTRP
- `painel_precificacao` — painel de precificação
- `percentual_reajuste_agrupamento` — percentuais de reajuste
- `ntrp_vcm_faixa_etaria` — nota técnica NTRP/VCM/faixa etária
- `valor_comercial_medio_municipio` — valor comercial médio por município
- `faixa_preco` — faixa de preço

### 7. Operadoras, rede e prestadores complementares
- `operadora_cancelada` — operadoras canceladas
- `operadora_acreditada` — operadoras acreditadas
- `prestador_acreditado` — prestadores acreditados
- `produto_prestador_hospitalar` — produtos e prestadores hospitalares
- `operadora_prestador_nao_hospitalar` — operadoras e prestadores não hospitalares
- `solicitacao_alteracao_rede_hospitalar` — solicitações de alteração de rede hospitalar

### 8. Regulatórios complementares
- `penalidade_operadora` — penalidades aplicadas
- `monitoramento_garantia_atendimento` — monitoramento de garantia de atendimento
- `peona_sus` — PEONA SUS
- `promoprev` — PROMOPREV
- `rpc` — RPC (24 meses)
- `iap` — IAP
- `pfa` — PFA
- `programa_qualificacao_institucional` — programa de qualificação institucional

### 9. Beneficiários e cobertura complementares
- `beneficiario_regiao_geografica` — beneficiários por região geográfica
- `beneficiario_informacao_consolidada` — informações consolidadas de beneficiários
- `taxa_cobertura_plano` — taxa de cobertura de planos

---

## Artefatos criados

### DDL (infra/postgres/init/)
- `041_delta_ans_produtos_planos.sql`
- `042_delta_ans_tuss_oficial.sql`
- `043_delta_ans_tiss_subfamilias.sql`
- `044_delta_ans_sip.sql`
- `045_delta_ans_ressarcimento_sus.sql`
- `046_delta_ans_precificacao_ntrp.sql`
- `047_delta_ans_rede_prestadores.sql`
- `048_delta_ans_regulatorios_complementares.sql`
- `049_delta_ans_beneficiarios_cobertura.sql`
- `050_delta_ans_grants.sql`

### Ingestão
- `ingestao/app/ingestao_delta_ans.py` — módulo consolidado com 40+ parsers
- 9 scripts `scripts/bootstrap_layout_registry_*.py`
- 9 DAGs `ingestao/dags/dag_ingest_*.py`
- `ingestao/tests/test_delta_ans_parsers.py` — 14 novos testes Python

### dbt models (tag: delta_ans_100)
- 38 staging views (`stg_*`)
- 34+ API tables (`api_*`) em `api_ans`
- 10+ consumo tables em `consumo_ans` (inclui consumo_historico_plano, consumo_plano_servico_opcional, consumo_tuss_procedimento_vigente, consumo_tiss_utilizacao_operadora_mes, consumo_sip_assistencial_operadora, consumo_ressarcimento_sus_operadora, consumo_precificacao_plano, consumo_produto_plano, consumo_rede_acreditacao, consumo_regulatorio_complementar_operadora, consumo_beneficiarios_cobertura_municipio)

### YAML / Documentação dbt
- `_stg_produtos_planos.yml` (corrigido bug de chave duplicada + expandido)
- `_stg_ressarcimento_sus.yml`
- `_stg_precificacao_ntrp.yml`
- `_stg_rede_prestadores.yml`
- `_stg_regulatorios_complementares.yml`
- `_stg_beneficiarios_cobertura.yml`
- `_consumo.yml` (expandido)

---

## Resultados dos gates

| Gate | Resultado |
|------|-----------|
| `ruff check api ingestao scripts testes` | All checks passed |
| `pytest ingestao/tests/ -v` | 101 passed |
| `pytest api/tests/ -v` | 114 passed |
| `dbt compile --select tag:delta_ans_100` | Sem erros |
| `dbt build --select tag:delta_ans_100` | PASS=162 WARN=0 ERROR=0 |
| Smokes SQL (12 tabelas api_ans) | Estrutura OK; 0 rows local (esperado) |
| `/saude` VPS | HTTP 200 `{"status":"ok"}` |
| Frontend VPS | HTTP 200 |
| Docker compose VPS | Todos os serviços Up/healthy |

---

## Grants aplicados

```
healthintel_cliente_reader  → consumo_ans   (19 tabelas)
healthintel_premium_reader  → consumo_premium_ans (11 tabelas)
healthintel                 → api_ans, consumo_ans, consumo_premium_ans
```

---

## TUSS — crosswalk sintético

`api_ans.api_tuss_procedimento_vigente` lê exclusivamente de `stg_tuss_terminologia_oficial` (TUSS.zip oficial ANS). O artefato sintético `xref_tiss_tuss_procedimento` está isolado em `consumo_premium_ans` e marcado como "CI não comercial" — não afeta a camada pública.

---

## Evidências

Todas em `docs/evidencias/ans_100_delta/`:
- `dbt_build.md` — output completo do `dbt build`
- `smoke_sql.md` — resultado dos smokes SQL
- `grants.md` — verificação de grants
- `smoke_api.md` — validação VPS pós-deploy
- `tuss_oficial.md` — evidência TUSS oficial vs sintético

---

## Decisões formais de não bloqueio

Ver seção §11 em `docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md`.

Resumo:
- `nucleo_ans.*` dimensional/factual → escopo de sprint posterior
- `consumo_premium_ans.*` completo → escopo de sprint posterior
- HTTP endpoints FastAPI para delta api_ans → escopo de sprint posterior
- História 11 Documentais → classificados como `não_comercial`
- Gates dependentes de carga real → validáveis após DAGs rodarem na VPS
