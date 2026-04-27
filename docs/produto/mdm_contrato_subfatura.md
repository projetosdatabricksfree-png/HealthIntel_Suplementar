# MDM Contrato e Subfatura — HealthIntel Suplementar

**Versão:** 1.0.0 — Sprint 32
**Data:** 2026-04-27
**Status:** Entrega técnica — sem cliente ativo em produção

---

## Visão Geral

O MDM de contrato e subfatura é a camada de identidade master para dados privados por tenant. Ele opera no schema `mdm_privado`, isolado por `tenant_id` via Row-Level Security (RLS) e exposto na API premium via `api_ans.api_premium_contrato_validado` e `api_ans.api_premium_subfatura_validada`.

---

## Arquitetura

### Fluxo de Dados

```
bruto_cliente (tenant-isolado, schema privado)
  → stg_cliente (staging cliente, normalização)
    → mdm_privado (golden records + exceptions + crosswalks)
      → consumo_premium_ans (superfície SQL direta premium)
        → api_ans.api_premium_* (superfície FastAPI)
```

### Isolamento por Tenant

- **RLS:** `mdm_privado` aplica `app.tenant_id = current_setting('app.tenant_id')` via `028_fase5_mdm_privado_rls.sql`.
- **Hash determinístico:** `md5(text)` para master IDs, sem dependência de sequência.
- **FastAPI:** Rotas `/v1/premium/contratos` e `/v1/premium/subfaturas` exigem tenant autenticado (`request.state.cliente_id`). Sem tenant → HTTP 403.

---

## Entidades

### `mdm_contrato_master`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `contrato_master_id` | text | Hash determinístico MDM |
| `tenant_id` | text | Identificador do tenant |
| `numero_contrato_canonico` | text | Número canônico do contrato |
| `operadora_master_id` | text | FK para `mdm_operadora_master` |
| `status_mdm` | text | `ATIVO`, `QUARENTENA`, `REPROVADO`, `DESATIVADO` |
| `mdm_confidence_score` | float | 0–1 |
| `has_excecao_bloqueante` | bool | Flag de exceção impeditiva |

### `mdm_subfatura_master`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `subfatura_master_id` | text | Hash determinístico MDM |
| `contrato_master_id` | text | FK para `mdm_contrato_master` |
| `tenant_id` | text | Identificador do tenant |
| `competencia` | text | YYYYMM |
| `status_mdm` | text | `ATIVO`, `QUARENTENA`, `REPROVADO`, `DESATIVADO` |
| `has_excecao_bloqueante` | bool | Flag de exceção impeditiva |

---

## Exceções Bloqueantes

Exceções bloqueantes (`is_blocking = true`) impedem a publicação do registro master na superfície premium:

- **CNPJ operadora inválido:** `is_cnpj_operadora_estrutural_valido = false`
- **Operadora não resolvida no MDM:** `is_operadora_mdm_resolvida = false`
- **Contrato não resolvido para subfatura:** `is_contrato_resolvido = false`

Registros com exceções bloqueantes são movidos para `mdm_*_exception` e **não** aparecem em `api_premium_*`.

---

## Publicação Premium

### Contrato Validado

Rota: `GET /v1/premium/contratos`

- Exige `tenant_id` autenticado
- Filtra automaticamente por `tenant_id`
- Publica apenas registros com `status_mdm IN ('ATIVO', 'GOLDEN', 'CANDIDATE')`
- Exclui registros com `has_excecao_bloqueante = true`

### Subfatura Validada

Rota: `GET /v1/premium/subfaturas`

- Exige `tenant_id` autenticado
- Filtra automaticamente por `tenant_id`
- Publica apenas registros com contrato resolvido e sem exceção bloqueante

---

## Segurança

| Controle | Implementação |
|----------|---------------|
| RLS por tenant | PostgreSQL `app.tenant_id` |
| API tenant obrigatório | FastAPI `_obter_tenant_id()` → HTTP 403 |
| Cache por tenant | Redis key inclui `tenant_id` |
| Nenhum cross-tenant leak | Filtro `WHERE tenant_id = :tenant_id` parametrizado |

---

## Status da Entrega

- **Sprint:** 32 — Endpoints Premium
- **Natureza:** Técnica/arquitetural — sem cliente ativo em produção
- **Dados:** Modelos compilam mas podem materializar zero linhas sem tenant/cliente ativo