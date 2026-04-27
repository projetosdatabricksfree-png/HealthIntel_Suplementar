# API Governance

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir as regras de arquitetura, exposição e contrato da API HealthIntel Suplementar. A API é o ponto de consumo primário dos data products.

---

## Arquitetura

### Camada de Leitura

```
FastAPI (Python 3.12+, FastAPI + asyncpg + SQLAlchemy async)
    │
    ├── /v1/operadora/360 ────────► api_ans.api_operadora_360
    ├── /v1/prata/* ──────────────► api_ans.api_cadop, etc.
    ├── /v1/premium/operadoras ───► api_ans.api_premium_operadora_360_validado
    ├── /v1/premium/cnes/* ──────► api_ans.api_premium_cnes_estabelecimento_validado
    ├── /v1/premium/tiss/* ──────► api_ans.api_premium_tiss_procedimento_tuss_validado
    ├── /v1/premium/tuss/* ──────► api_ans.api_premium_tuss_procedimento
    ├── /v1/premium/mdm/* ───────► api_ans.api_premium_mdm_*
    ├── /v1/premium/contratos ───► api_ans.api_premium_contrato_validado
    ├── /v1/premium/subfaturas ──► api_ans.api_premium_subfatura_validada
    ├── /v1/premium/quality/* ───► api_ans.api_premium_quality_dataset
    └── /v1/saude ─────────────────► (health check)
```

### Regra Fundamental

**FastAPI lê apenas schemas `api_ans`.** Nenhum endpoint lê diretamente:

- `consumo_premium_ans`
- `mdm_ans`
- `mdm_privado`
- `quality_ans`
- `bruto_cliente`
- `stg_cliente`
- `nucleo_ans`
- `int_ans`
- `stg_ans`
- `bruto_ans`
- `enrichment`
- `plataforma` (exceto middlewares de autenticação/log)

### API Premium

**API premium (`/v1/premium/*`) lê apenas `api_ans.api_premium_*`.**

---

## Contrato de Endpoint

Todo endpoint deve ter documentado:

| Campo | Descrição |
|-------|-----------|
| **Método** | GET, POST etc. |
| **Rota** | Path completo |
| **Plano** | `ouro`, `prata`, `premium` |
| **Autenticação** | `X-API-Key` header |
| **Parâmetros** | Query params com tipo, obrigatoriedade e validação |
| **Response** | Schema Pydantic v2 com envelope padronizado |
| **Paginação** | `pagina`, `limite` (máx 100) |
| **Rate Limit** | RPM por chave/plano |
| **Cache** | Redis TTL por dataset |

---

## Envelope Padronizado

Toda resposta de lista segue:

```json
{
  "dados": [...],
  "meta": {
    "fonte": "api_premium_operadora_360_validado",
    "competencia": "202501",
    "versao_dataset": "operadora_360_validado_v1",
    "total": 150,
    "pagina": 1,
    "por_pagina": 50,
    "cache": "miss"
  }
}
```

---

## Autenticação e Autorização

1. Header `X-API-Key` obrigatório em todas as rotas.
2. Middleware `validar_api_key` — valida chave, plano, cotas.
3. Middleware `verificar_camada` — bloqueia acesso a camadas não permitidas.
4. Middleware `aplicar_rate_limit` — RPM por chave.
5. Rotas privadas (`/v1/premium/contratos`, `/v1/premium/subfaturas`) exigem `tenant_id` no request state.
6. Sem tenant → HTTP 403 (`TENANT_OBRIGATORIO`).

---

## Planos Comerciais

| Plano | Camadas | Premium |
|-------|---------|---------|
| **Free** | `ouro` | ❌ |
| **Piloto** | `ouro` | ❌ |
| **Prata** | `ouro`, `prata` | ❌ |
| **Ouro** | `ouro`, `prata`, `bronze` | ❌ |
| **Premium** | `ouro`, `prata`, `bronze`, `premium` | ✅ |

---

## Paginação

1. Parâmetros: `pagina` (>=1), `limite` (1–100).
2. Default: `pagina=1&limite=50`.
3. Meta inclui `total`, `pagina`, `por_pagina`.
4. Ordenação documentada por dataset no service.

---

## Cache

1. Redis com TTL por dataset.
2. Cache key: `premium:{dataset}:{pagina}:{limite}:{hash_filtros}`.
3. Meta inclui `cache: "hit"` ou `cache: "miss"`.
4. Cache invalidado por competência/nova carga.

---

## Segurança

1. Nenhum endpoint expõe `_hash_arquivo`, `_lote_ingestao`, `_carregado_em` ou outros campos técnicos.
2. Nenhum endpoint expõe payload bruto.
3. Nenhum endpoint expõe stack trace ou SQL interno em produção.
4. Erros retornam envelope `{"codigo": "...", "mensagem": "..."}` sem dados sensíveis.
5. Rate limiting por chave de API.
6. Log de uso (`plataforma.log_uso`) com hash de IP, sem dados de payload.

---

## Proibições

1. ❌ Nenhum endpoint permite dump completo por padrão.
2. ❌ Nenhum endpoint lê schema que não seja `api_ans`.
3. ❌ Nenhum endpoint monta SQL com input de usuário sem parametrização.
4. ❌ Nenhum endpoint premium retorna dados de outro tenant.
5. ❌ Nenhum endpoint expõe campo `tenant_id` sem coerência com autorização.
6. ❌ Nenhum endpoint depende de API externa (Serpro, Receita, BrasilAPI).

---

## Versionamento

1. Rotas prefixadas: `/v1/`, `/v2/` etc.
2. Mudança quebrando contrato → nova versão de rota.
3. Deprecation de versão anterior com aviso e período de transição.
4. Versão atual documentada no CHANGELOG.