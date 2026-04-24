# Fase 4 — ELT Completo: Gold Curado para Clientes

Fase de finalização do pipeline ELT. Fecha as lacunas da Prata, implementa ingestão real de SIB e CADOP, cria marts Gold para consumo analítico, introduz o schema `consumo_ans` como camada de entrega para clientes e consolida qualidade + catálogo com baseline `v3.0.0`.

## Sprints

| Sprint | Título | Status |
|--------|--------|--------|
| [Sprint 21](sprint_21_prata_completa.md) | Prata Completa | Pendente |
| [Sprint 22](sprint_22_ingestao_real_sib_cadop.md) | Ingestão Real: SIB e CADOP | Pendente |
| [Sprint 23](sprint_23_gold_marts_bi.md) | Gold Curado: Data Products ANS | Pendente |
| [Sprint 24](sprint_24_consumo_ans_serving.md) | consumo_ans: Camada de Entrega para Clientes | Pendente |
| [Sprint 25](sprint_25_qualidade_catalogo_v3.md) | Qualidade, Catálogo e v3.0.0 | Pendente |

---

## Arquitetura Alvo (Fase 4)

```
ANS / DATASUS
    ↓
Landing Zone (volume docker)
    ↓
Bronze / bruto_ans        ← idempotente, hash, lote
    ↓
Silver / stg_ans          ← tipagem, domínio, quarentena
    ↓
Intermediate / int_ans    ← joins, enriquecimento
    ↓
Gold Analítico / nucleo_ans ← dim_* + fat_* + mart_*
    ↙                        ↘
api_ans (FastAPI REST)    consumo_ans (tabelas curadas para clientes)
                              ↓
                  Power BI / Metabase / Python / SQL / qualquer ferramenta do cliente
```

### Novos schemas introduzidos na Fase 4

| Schema | Propósito | Consumidor |
|--------|-----------|------------|
| `consumo_ans` | Tabelas Gold desnormalizadas prontas para consumo externo | Clientes com acesso PostgreSQL direto |

### Novos modelos dbt introduzidos na Fase 4

| Tipo | Modelos | Sprint |
|------|---------|--------|
| Prata API (CNES/TISS) | `api_prata_cnes_municipio`, `api_prata_cnes_rede_gap`, `api_prata_tiss_procedimento` | 21 |
| Gold Mart | `mart_operadora_360`, `mart_mercado_municipio`, `mart_regulatorio_operadora`, `mart_rede_assistencial`, `mart_score_operadora`, `mart_tiss_procedimento` | 23 |
| Consumo Clientes | `consumo_operadora_360`, `consumo_beneficiarios_operadora_mes`, `consumo_beneficiarios_municipio_mes`, `consumo_financeiro_operadora_trimestre`, `consumo_regulatorio_operadora_trimestre`, `consumo_rede_assistencial_municipio`, `consumo_oportunidade_municipio`, `consumo_score_operadora_mes` | 24 |

### Novos DAGs introduzidos na Fase 4

| DAG | Dataset | Sprint |
|-----|---------|--------|
| `dag_ingest_sib.py` | SIB — beneficiários mensal | 22 |
| `dag_ingest_cadop.py` | CADOP — operadoras ativas | 22 |
| `dag_dbt_consumo_refresh.py` | Refresh automatizado consumo_ans | 24 |

---

## Critério de Saída da Fase 4

- [x] `pytest api/tests/integration/test_prata.py -v` — todos os endpoints Prata registrados em `PRATA_DATASETS` cobertos
- [x] `make smoke-prata` — zero falhas
- [x] `make smoke-sib` — zero falhas
- [x] `make smoke-cadop` — zero falhas
- [x] `make smoke-consumo` — zero falhas
- [x] `dbt build --select tag:prata tag:mart tag:consumo` — sem falhas
- [x] `dbt test` — todos os testes passando
- [x] `dbt docs generate` — documentação gerada sem erro
- [x] `plataforma.lote_ingestao` registrando lotes SIB e CADOP com hash
- [x] `consumo_ans` acessível via conexão PostgreSQL direta com role `healthintel_cliente_reader`
- [x] `healthintel_cliente_reader` recebe `PERMISSION DENIED` em `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans` e `plataforma`
- [x] `pytest testes/regressao/test_endpoints_fase4.py -v` — zero falhas
- [ ] Tag git `v3.0.0` criada após aprovação
