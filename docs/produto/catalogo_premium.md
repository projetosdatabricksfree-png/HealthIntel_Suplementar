# Catálogo de Produtos Premium — HealthIntel Suplementar

**Versão:** 1.0.0 — Sprint 31  
**Data:** 2026-04-27  
**Status:** Entrega técnica/arquitetural — sem cliente ativo em produção  

---

## Visão Geral

A Sprint 31 entrega a primeira geração de **produtos de dados premium** da plataforma HealthIntel Suplementar. Estes produtos são superfícies SQL validadas, enriquecidas com qualidade documental offline (Sprint 28), identidade master via MDM público (Sprint 29) e MDM privado por tenant (Sprint 30).

Os produtos premium **não substituem** os produtos legados em `consumo_ans`. Ambos coexistem, atendendo perfis distintos de consumo:

| Perfil | Schema | Acesso | Propósito |
|--------|--------|--------|-----------|
| **Cliente legado** | `consumo_ans` | `healthintel_cliente_reader` | Consumo operacional padrão |
| **Cliente premium** | `consumo_premium_ans` | `healthintel_premium_reader` | Consumo analítico validado com MDM e scores |

A camada de API (`api_ans.api_premium_*`) isola a FastAPI do schema `consumo_premium_ans`, seguindo o padrão de superfície de serviço estabelecido desde a Fase 4.

---

## Produtos Premium Disponíveis

### 1. Operadora 360 Validada

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_operadora_360_validado` |
| **Modelo API** | `api_ans.api_premium_operadora_360_validado` |
| **Granularidade** | competência × registro_ans |
| **Fontes** | `mart_operadora_360`, `dq_operadora_documento`, `mdm_operadora_master` |
| **Filtro de qualidade** | `documento_quality_status = 'VALIDO'`, registro_ans e CNPJ válidos |
| **Scores** | `quality_score_documental` (100), `quality_score_mdm` (confidence) |
| **Campos-chave** | `operadora_master_id`, `registro_ans`, `cnpj_normalizado`, `score_total` |

### 2. CNES Estabelecimento Validado

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_cnes_estabelecimento_validado` |
| **Modelo API** | `api_ans.api_premium_cnes_estabelecimento_validado` |
| **Granularidade** | competência × cnes_normalizado |
| **Fontes** | `dq_cnes_documento`, `mdm_estabelecimento_master`, `mdm_prestador_master` |
| **Filtro de qualidade** | CNES 7 dígitos válido, CNPJ com dígito válido |
| **Scores** | `quality_score_cnes` (100), `quality_score_mdm` (confidence) |
| **Campos-chave** | `estabelecimento_master_id`, `prestador_master_id`, `cnes_normalizado` |

### 3. TISS/TUSS Procedimento Validado

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_tiss_procedimento_tuss_validado` |
| **Modelo API** | `api_ans.api_premium_tiss_procedimento_tuss_validado` |
| **Granularidade** | trimestre × registro_ans × cd_procedimento_tuss |
| **Fontes** | `mart_tiss_procedimento`, `mdm_operadora_master`, `ref_tuss` (sintético) |
| **Status** | **NÃO COMERCIAL** — base TUSS sintética |
| **Scores** | `quality_score_procedimento` |
| **Campos-chave** | `cd_procedimento_tuss`, `operadora_master_id`, `trimestre` |

> ⚠️ **Aviso:** Os dados TUSS utilizados são sintéticos e não representam a terminologia oficial da ANS. Consulte `docs/produto/tiss_tuss_premium.md`.

### 4. TUSS Procedimento (Catálogo)

| Atributo | Valor |
|----------|-------|
| **Modelo API** | `api_ans.api_premium_tuss_procedimento` |
| **Granularidade** | código_tuss × versão |
| **Fonte** | `dim_tuss_procedimento` |
| **Status** | **NÃO COMERCIAL** — base TUSS sintética |

### 5. MDM Operadora (Superfície Premium)

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_mdm_operadora` |
| **Modelo API** | `api_ans.api_premium_mdm_operadora` |
| **Granularidade** | operadora_master_id |
| **Fonte** | `mdm_operadora_master` (filtrado: status_mdm = 'ATIVO') |
| **Campos-chave** | `operadora_master_id`, `registro_ans_canonico`, `cnpj_canonico` |

### 6. MDM Prestador (Superfície Premium)

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_mdm_prestador` |
| **Modelo API** | `api_ans.api_premium_mdm_prestador` |
| **Granularidade** | prestador_master_id |
| **Fonte** | `mdm_prestador_master` (filtrado: status_mdm = 'ATIVO') |
| **Campos-chave** | `prestador_master_id`, `estabelecimento_master_id`, `cnes_canonico` |

### 7. Contrato Validado (Privado por Tenant)

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_contrato_validado` |
| **Modelo API** | `api_ans.api_premium_contrato_validado` |
| **Granularidade** | tenant_id × contrato_master_id |
| **Fonte** | `mdm_contrato_master` (filtrado: GOLDEN/CANDIDATE, sem exceção bloqueante) |
| **Acesso** | `healthintel_premium_reader` + filtro tenant obrigatório na API |
| **Campos-chave** | `tenant_id`, `contrato_master_id`, `operadora_master_id` |

### 8. Subfatura Validada (Privada por Tenant)

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_subfatura_validada` |
| **Modelo API** | `api_ans.api_premium_subfatura_validada` |
| **Granularidade** | tenant_id × subfatura_master_id × competencia |
| **Fonte** | `mdm_subfatura_master` (filtrado: GOLDEN/CANDIDATE, contrato resolvido, sem exceção bloqueante) |
| **Acesso** | `healthintel_premium_reader` + filtro tenant obrigatório na API |
| **Campos-chave** | `tenant_id`, `subfatura_master_id`, `contrato_master_id` |

### 9. Quality Dataset (Agregado de Qualidade)

| Atributo | Valor |
|----------|-------|
| **Modelo consumo** | `consumo_premium_ans.consumo_premium_quality_dataset` |
| **Modelo API** | `api_ans.api_premium_quality_dataset` |
| **Granularidade** | fonte_documento × documento_quality_status |
| **Fontes** | `dq_cadop_documento`, `dq_operadora_documento`, `dq_cnes_documento`, `dq_prestador_documento` |
| **Scores** | `quality_score_documental` (percentual de registros válidos por fonte) |

---

## Modelos de Inconsistência (Privados)

### Contrato/Subfatura × Operadora

| Atributo | Valor |
|----------|-------|
| **Modelo** | `consumo_premium_ans.consumo_premium_contrato_subfatura_operadora` |
| **Granularidade** | tenant_id × contrato_master_id × subfatura_master_id |
| **Fontes** | `consumo_premium_contrato_validado`, `consumo_premium_subfatura_validada`, `mdm_operadora_master` |
| **Propósito** | Visão integrada contrato-subfatura-operadora para consumo premium |

### Inconsistência de Contrato

| Atributo | Valor |
|----------|-------|
| **Modelo** | `consumo_premium_ans.consumo_premium_contrato_inconsistencia` |
| **Granularidade** | contrato_master_id × exception_type |
| **Fonte** | `mdm_contrato_exception` (filtrado: is_blocking = true) |
| **Propósito** | Exposição controlada de exceções bloqueantes, separada dos produtos principais |

---

## Consumo Futuro

### Consumo SQL Direto (Clientes Premium)

```sql
-- Exemplo: operadoras 360 validadas com score máximo
SELECT operadora_master_id, razao_social, uf, score_total, quality_score_documental
FROM consumo_premium_ans.consumo_premium_operadora_360_validado
WHERE competencia = '202401'
ORDER BY score_total DESC;
```

### Consumo via API (FastAPI — Sprint 32)

A FastAPI premium (a ser implementada na Sprint 32) consumirá exclusivamente os modelos `api_ans.api_premium_*`. O padrão de autenticação e autorização aplicará filtro obrigatório de `tenant_id` para modelos privados.

---

## Controle de Acesso

| Role | consumo_ans | consumo_premium_ans | mdm_privado | bruto_cliente | stg_cliente |
|------|-------------|---------------------|-------------|---------------|-------------|
| `healthintel_cliente_reader` | SELECT | **REVOKED** | REVOKED | REVOKED | REVOKED |
| `healthintel_premium_reader` | — | SELECT | REVOKED | REVOKED | REVOKED |

---

## Status da Entrega

- **Sprint:** 31 — Produtos Premium Validados para Consumo
- **Fase:** 5 — Qualidade, Governança, MDM e Produtos Premium
- **Status atual:** Em execução — hard gates pendentes
- **Cliente ativo em produção:** Nenhum
- **Natureza da entrega:** Técnica/arquitetural — preparação de superfícies para futura comercialização
- **Próxima sprint:** Sprint 32 — Endpoints FastAPI Premium + Smoke Tests

---

## Limitações Conhecidas

1. **TUSS/ROL:** Base sintética, não comercial (ver `docs/produto/tiss_tuss_premium.md`)
2. **Dados privados:** Modelos de contrato/subfatura compilam mas podem materializar zero linhas se não houver tenant/cliente ativo
3. **Prestador × Operadora:** `mdm_prestador_master.operadora_master_id` é `null` por design — link será feito via rede credenciada futuramente
4. **API endpoints:** Não criados nesta sprint (escopo da Sprint 32)
5. **Scores de publicação:** `quality_score_publicacao` implementado como `100` (placeholders para métricas futuras de freshness e completude)