# Data Products — Governança

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir o que constitui um data product na plataforma HealthIntel Suplementar, seus contratos de consumo, responsabilidades e regras de exposição.

---

## Definição de Data Product

Um data product é um conjunto de dados curado, documentado e versionado, exposto para consumo externo (cliente) via API ou SQL direto, com contrato de consumo explícito.

---

## Tipos de Data Product

### Legado (Ouro/Prata)

| Data Product | Schema | Acesso | Plano |
|-------------|--------|--------|-------|
| `api_operadora_360` | `api_ans` | API `/v1/operadora/360` | Ouro |
| `api_cadop` | `api_ans` | API `/v1/prata/cadop` | Prata |
| `consumo_beneficiarios_operadora_mes` | `consumo_ans` | SQL direto | Ouro+ |
| `consumo_financeiro_operadora_trimestre` | `consumo_ans` | SQL direto | Ouro+ |

### Premium

| Data Product | Schema | Acesso | Plano |
|-------------|--------|--------|-------|
| `api_premium_operadora_360_validado` | `api_ans` | API `/v1/premium/operadoras` | Premium |
| `api_premium_cnes_estabelecimento_validado` | `api_ans` | API `/v1/premium/cnes/estabelecimentos` | Premium |
| `api_premium_tiss_procedimento_tuss_validado` | `api_ans` | API `/v1/premium/tiss/procedimentos` | Premium |
| `api_premium_tuss_procedimento` | `api_ans` | API `/v1/premium/tuss/procedimentos` | Premium |
| `api_premium_mdm_operadora` | `api_ans` | API `/v1/premium/mdm/operadoras` | Premium |
| `api_premium_mdm_prestador` | `api_ans` | API `/v1/premium/mdm/prestadores` | Premium |
| `api_premium_contrato_validado` | `api_ans` | API `/v1/premium/contratos` | Premium |
| `api_premium_subfatura_validada` | `api_ans` | API `/v1/premium/subfaturas` | Premium |
| `api_premium_quality_dataset` | `api_ans` | API `/v1/premium/quality/datasets` | Premium |
| `consumo_premium_*` | `consumo_premium_ans` | SQL direto autorizado | Premium |

---

## Contrato de Data Product

Cada data product deve ter:

| Campo | Descrição |
|-------|-----------|
| **Owner** | Responsável técnico pelo data product |
| **SLA** | Frequência de atualização e prazo máximo |
| **Granularidade** | Grão dos dados |
| **Fonte** | Linhagem upstream |
| **Score de qualidade** | Qualidade mínima exigida |
| **Master IDs** | Surrogate keys disponíveis |
| **Linhagem** | Documentada em `docs/arquitetura/lineage_fase4.md` |
| **Contrato de consumo** | Formato, paginação, limites, autenticação |

---

## Regras de Consumo

### API (`api_ans`)

1. FastAPI lê **apenas** `api_ans`.
2. API premium lê **apenas** `api_ans.api_premium_*`.
3. Toda rota tem paginação.
4. Limite máximo de linhas por request: 100.
5. Nenhuma rota permite dump completo sem contrato específico.

### SQL Direto (`consumo_ans` / `consumo_premium_ans`)

1. Acesso via credencial de banco com grants restritos.
2. `consumo_ans` acessível para plano Ouro+.
3. `consumo_premium_ans` acessível apenas para plano Premium.
4. SQL direto não tem limite de linhas (contrato Enterprise).
5. RLS aplicado em schemas com `tenant_id`.

---

## Anti-Exfiltração

1. Nenhum endpoint permite dump completo por padrão.
2. Limite máximo de 100 linhas por request em API pública/premium.
3. Rate limiting por chave de API.
4. Log de uso (`plataforma.log_uso`) registra toda requisição.
5. Dados privados nunca em schema público.
6. RLS obrigatório em `mdm_privado` e `consumo_premium_ans`.

---

## Score de Qualidade por Data Product

Data products premium devem publicar score de qualidade no envelope de resposta:

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

Os scores estão disponíveis em `/v1/premium/quality/datasets`.

---

## Linhagem

A linhagem completa de cada data product está documentada em:
- `docs/arquitetura/lineage_fase4.md`
- Campo `upstream` no catálogo de tabelas (`docs/governanca/catalogo_tabelas.md`)
- `healthintel_dbt/docs/` (dbt docs gerados)

---

## Versionamento

1. Data products são versionados (ex: `operadora_360_validado_v1`).
2. Mudança de schema quebrando contrato exige nova versão.
3. Versão anterior mantida por período de transição (mínimo 2 competências).
4. Deprecation comunicado com antecedência mínima de 1 competência.