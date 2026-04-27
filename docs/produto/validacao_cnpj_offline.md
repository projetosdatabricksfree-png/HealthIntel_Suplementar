# Validação Determinística de CNPJ Offline — HealthIntel Suplementar

**Versão:** 1.0.0 — Sprint 32
**Data:** 2026-04-27
**Status:** Sprint 28 concluída — validação 100% offline, sem dependência externa

---

## Visão Geral

A Sprint 28 implementou validação determinística offline de CNPJ (e outros documentos regulatórios) na camada `quality_ans`. Esta validação é executada inteiramente dentro do PostgreSQL, sem chamadas externas a Serpro, Receita Federal, BrasilAPI ou qualquer outro provedor.

**Regra arquitetural:** A FastAPI premium (Sprint 32) não consulta `quality_ans` diretamente — consome apenas `api_ans.api_premium_*`, que herdam os indicadores de qualidade calculados offline.

---

## Validações Implementadas

### 1. CNPJ — Dígito Verificador (DV)

- **Algoritmo:** Módulo 11 com pesos [6,5,4,3,2,9,8,7,6,5,4,3,2] para o primeiro DV e [5,4,3,2,9,8,7,6,5,4,3,2] para o segundo.
- **Macro dbt:** `validar_cnpj_completo` em `healthintel_dbt/macros/validar_cnpj_completo.sql`.
- **Exposição:** `cnpj_digito_valido` (boolean) nos schemas premium.

### 2. Registro ANS — Formato

- **Validação:** 6 dígitos numéricos.
- **Macro dbt:** `normalizar_registro_ans` em `healthintel_dbt/macros/normalizar_registro_ans.sql`.
- **Exposição:** `registro_ans_formato_valido` (boolean).

### 3. CNES — Formato

- **Validação:** 7 dígitos numéricos.
- **Macro dbt:** `validar_cnes_formato` em `healthintel_dbt/macros/validar_cnes_formato.sql`.
- **Exposição:** `cnes_formato_valido` (boolean).

### 4. CNPJ — Normalização

- **Formato:** 14 dígitos numéricos (sem pontuação), com zero-fill à esquerda.
- **Macro dbt:** `normalizar_cnpj` em `healthintel_dbt/macros/normalizar_cnpj.sql`.
- **Nota:** A normalização não valida o DV; apenas padroniza o formato.

---

## Status de Qualidade Documental

Cada registro nos produtos premium carrega `documento_quality_status`:

| Status | Significado |
|--------|-------------|
| `VALIDO` | CNPJ com formato e DV válidos |
| `INVALIDO_FORMATO` | CNPJ não possui 14 dígitos numéricos |
| `INVALIDO_DIGITO` | CNPJ com formato válido mas DV incorreto |
| `SEQUENCIA_INVALIDA` | CNPJ com todos dígitos iguais (ex: 00000000000000) |
| `NULO` | CNPJ ausente ou nulo |

Apenas registros com `documento_quality_status = 'VALIDO'` são publicados nas superfícies premium (`api_premium_*`).

---

## O Que NÃO É Implementado

| Funcionalidade | Status | Motivo |
|----------------|--------|--------|
| Consulta à Receita Federal | **Não implementado** | Decisão arquitetural Sprint 28 |
| Consulta ao Serpro | **Não implementado** | Decisão arquitetural Sprint 28 |
| Consulta à BrasilAPI | **Não implementado** | Decisão arquitetural Sprint 28 |
| Validação de situação cadastral | **Não implementado** | Fora do escopo offline |
| Enriquecimento (enrich-cnpj) | **Não implementado** | Proibido pela Sprint 28 |
| Validação de CPF | **Não implementado** | Backlog |

---

## Campo `motivo_invalidade_documento`

Quando `documento_quality_status != 'VALIDO'`, o campo `motivo_invalidade_documento` descreve a razão:

- `CNPJ_FORMATO_INVALIDO` — não possui 14 dígitos
- `CNPJ_DIGITO_INVALIDO` — DV não confere
- `CNPJ_SEQUENCIA_INVALIDA` — todos dígitos iguais
- `CNPJ_NULO` — valor ausente
- `REGISTRO_ANS_FORMATO_INVALIDO` — não possui 6 dígitos

---

## Status da Entrega

- **Sprint de origem:** 28 — Validação Determinística de CNPJ Offline
- **Sprint atual:** 32 — Endpoints Premium
- **Natureza:** Técnica — validação offline, sem cliente ativo em produção
- **Dependências externas:** Nenhuma