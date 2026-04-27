# Template de Documentação de Endpoint de API

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar endpoints da API.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `metodo` | HTTP method | `GET` |
| `rota` | Path completo | `/v1/premium/operadoras` |
| `versao` | Versão da rota | `v1` |
| `plano` | Plano comercial | `premium` |
| `autenticacao` | Header / método | `X-API-Key` |
| `dataset` | Tabela fonte (api_ans) | `api_ans.api_premium_operadora_360_validado` |
| `parametros` | Query params | `pagina`, `limite`, `competencia`, `uf` |
| `formato_resposta` | Schema Pydantic | `PremiumOperadoraResponse` |
| `envelope` | Estrutura do envelope | `{dados, meta, paginacao, qualidade}` |
| `paginacao` | Obrigatória? | `sim` |
| `limite_max_linhas` | Máximo por request | `100` |
| `rate_limit_rpm` | Requests por minuto | `60` |
| `cache_ttl` | Redis TTL (segundos) | `300` |
| `tenant_obrigatorio` | Exige tenant? | `nao` |
| `owner` | Responsável | `Engenharia de API` |
| `status` | `ativo`, `deprecated` | `ativo` |

## Exemplo

| Campo | Valor |
|-------|-------|
| metodo | `GET` |
| rota | `/v1/premium/operadoras` |
| plano | `premium` |
| dataset | `api_ans.api_premium_operadora_360_validado` |
| parametros | `pagina`, `limite`, `competencia`, `uf` |
| paginacao | `sim` |
| limite_max_linhas | `100` |
| tenant_obrigatorio | `nao` |
| status | ativo |

## Exemplo de Request/Response

**Request:**
```
GET /v1/premium/operadoras?competencia=202501&uf=SP&pagina=1&limite=50
X-API-Key: hp_sk_premium_...
```

**Response:**
```json
{
  "dados": [
    {
      "operadora_master_id": "abc123...",
      "registro_ans": "001234",
      "razao_social": "Operadora Exemplo",
      "competencia": 202501,
      "quality_score_publicacao": 95.0
    }
  ],
  "meta": {
    "fonte": "api_premium_operadora_360_validado",
    "competencia": 202501,
    "versao_dataset": "operadora_360_validado_v1",
    "total": 150,
    "pagina": 1,
    "por_pagina": 50,
    "cache": "miss"
  }
}
```

## Checklist
- [ ] Contrato request/response documentado
- [ ] Dataset fonte é `api_ans` apenas
- [ ] Paginação obrigatória
- [ ] Limite máximo de linhas definido
- [ ] Tenant obrigatório quando dados privados
- [ ] Campos técnicos não expostos