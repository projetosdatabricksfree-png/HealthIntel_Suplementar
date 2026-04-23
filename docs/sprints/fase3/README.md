# Fase 3 — Arquitetura Medallion Completa e Comercialização

Fase de formalização arquitetural e expansão comercial. Estabelece contratos por camada, multi-tier API (Bronze/Prata/Ouro) e rollout enterprise final com baseline `v2.0.0`.

## Sprints

| Sprint | Título | Status |
|--------|--------|--------|
| [Sprint 15](sprint_15_governanca_camadas.md) | Governança de Camadas | Não iniciada |
| [Sprint 16](sprint_16_bronze_api_tecnica.md) | Bronze API Técnica | Não iniciada |
| [Sprint 17](sprint_17_prata_api_analitica.md) | Prata API Analítica | Não iniciada |
| [Sprint 18](sprint_18_datasets_complementares.md) | Datasets Complementares | Não iniciada |
| [Sprint 19](sprint_19_score_v3_indice_composto.md) | Score v3 e Índice Composto | Não iniciada |
| [Sprint 20](sprint_20_comercializacao_enterprise.md) | Comercialização e Enterprise Final | Não iniciada |

---

## Arquitetura de Referência

```
Raw/Landing  →  Bronze        →  Prata entrada  →  Prata saída  →  Ouro analítico  →  Ouro serviço
(storage)       bruto_ans        stg_ans            int_ans         nucleo_ans          api_ans
                (técnica)        (tipagem)           (enriquecida)   (negócio)           (produto)
```

### Matriz de Camadas

| Camada | Schema | Garantia | API exposta | Plano mínimo |
|--------|--------|----------|-------------|--------------|
| Bronze | `bruto_ans` | Estrutural: hash, lote, encoding, idempotência | Bronze API | `enterprise_tecnico` |
| Prata entrada | `stg_ans` | Tipagem + domínio + normalização | Prata API | `analitico` |
| Prata saída | `int_ans` | Semântica básica + joins + dedup | Prata API enriquecida | `analitico` |
| Ouro analítico | `nucleo_ans` | Regras de negócio, SCD2, scores | — (interno) | — |
| Ouro serviço | `api_ans` | SLA forte, contrato estável, indexado | Ouro API (produto principal) | `piloto` |

---

## Tiers Comerciais

| Plano | Camadas | Rate limit | SLA latência p95 | Disponibilidade |
|-------|---------|------------|------------------|-----------------|
| `piloto` | Ouro | 100 req/h | < 500ms | melhor esforço |
| `essencial` | Ouro | 1.000 req/h | < 200ms | 99,0%/mês |
| `plus` | Ouro + Prata | 5.000 req/h | < 200ms | 99,5%/mês |
| `enterprise` | Ouro + Prata + Bronze | 20.000 req/h | < 150ms | 99,9%/mês |
| `enterprise_tecnico` | Todos + raw | ilimitado | < 150ms | 99,9%/mês + SLA de carga |

---

## Contratos por Camada

### Bronze — Confiança Técnica
- Dado as-is, zero transformação semântica
- Metadados obrigatórios: `_lote_id`, `_arquivo_origem`, `_carregado_em`, `_hash_arquivo`, `versao_dataset`
- Sem SLA semântico; aviso de qualidade explícito no envelope
- Validações: estruturais (encoding, cabeçalho, contagem de linhas, hash, partição)

### Prata — Confiança Estrutural
- Dado padronizado: cast, normalização, chaves substitutas
- Quarentena real: registros inválidos em `*_quarentena` com motivo e regra preservados
- Metadados de qualidade: `taxa_aprovacao`, `registros_quarentena`, `competencia`
- Validações: tipagem, domínio, regex de chave, data válida, CNPJ 14 dígitos, UF existente

### Ouro — Confiança de Negócio
- Dado analítico: modelagem dimensional, fatos incrementais, snapshots SCD2
- Score entre 0–100, share soma 100% por partição, séries históricas comparáveis
- SLA de contrato estável: campo não muda de tipo entre versões
- Validações: grão correto, unicidade de chave de negócio, integridade referencial

---

## Critério de Saída da Fase 3

- [ ] `pytest testes/regressao/test_endpoints_fase3.py` — zero falhas (hard gate)
- [ ] `dbt compile` sem erros com todos os novos modelos
- [ ] `docs/arquitetura/contratos_por_camada.md` revisado e aprovado
- [ ] `plataforma.plano` contém os 5 tiers com `sla_*` e `camadas_permitidas`
- [ ] Tag git `v2.0.0` criada após aprovação
