# Quality Scores — HealthIntel Suplementar

**Versão:** 1.0.0 — Sprint 32
**Data:** 2026-04-27
**Status:** Entrega técnica — scores originados nas Sprints 27-28 (qualidade documental) e 29 (MDM)

---

## Visão Geral

Os scores de qualidade são métricas determinísticas calculadas offline (sem dependência externa) que qualificam registros públicos e privados na plataforma HealthIntel. São expostos nos produtos premium via `api_ans.api_premium_*` e nas rotas `/v1/premium/*`.

Nenhum score utiliza Serpro, Receita online, BrasilAPI ou qualquer provedor externo. Toda validação é offline.

---

## Scores por Domínio

### 1. `quality_score_documental`

- **Definição:** Percentual de registros válidos (formato e dígito verificador) em uma fonte documental.
- **Cálculo:** `(total_valido / total_fonte) * 100`
- **Exposição:** `api_ans.api_premium_quality_dataset.taxa_valido` (já normalizado 0–1) e `quality_score_documental` (0–100).
- **Domínios avaliados:** operadora (CADOP), CNES, prestador.
- **Origem:** Sprint 28 — Validação Determinística de CNPJ Offline.

### 2. `quality_score_mdm`

- **Definição:** Confiança do MDM na resolução de identidade master para uma entidade.
- **Cálculo:** Derivado do `mdm_confidence_score` (0–1), normalizado 0–100.
- **Exposição:** `api_premium_mdm_operadora.mdm_confidence_score`, `api_premium_mdm_prestador.mdm_confidence_score`.
- **Origem:** Sprint 29 — MDM Público.

### 3. `quality_score_publicacao`

- **Definição:** Placeholder para métricas futuras de freshness e completude de publicação.
- **Valor atual:** Constante `100` (nenhuma métrica real implementada).
- **Exposição:** Reservado em schemas de catálogo.
- **Origem:** Sprint 31 (planejado para métricas futuras).

### 4. `quality_score_cnes`

- **Definição:** Score de qualidade documental específico para registros CNES.
- **Cálculo:** 100 se `cnes_formato_valido=true` e `cnpj_digito_valido=true`; =0 caso contrário.
- **Exposição:** `api_premium_cnes_estabelecimento_validado.quality_score_cnes`.
- **Origem:** Sprint 28 — validação CNES + CNPJ offline.

### 5. `quality_score_tuss`

- **Definição:** Score de qualidade para registros do catálogo TUSS.
- **Cálculo:** 100 para registros com `is_tuss_vigente=true` e referência cruzada ROL resolvida.
- **Exposição:** `api_premium_tuss_procedimento.quality_score_tuss`.
- **Observação:** Dados TUSS são sintéticos (não comerciais).

### 6. `quality_score_contrato`

- **Definição:** Score de qualidade para contratos privados validados.
- **Cálculo:** Derivado do status de resolução MDM e ausência de exceções bloqueantes.
- **Exposição:** `api_premium_contrato_validado.mdm_confidence_score` e `mdm_status`.
- **Regra:** Apenas contratos com `mdm_status IN ('ATIVO', 'GOLDEN', 'CANDIDATE')` e `has_excecao_bloqueante=false` são publicados.

### 7. `quality_score_subfatura`

- **Definição:** Score de qualidade para subfaturas privadas validadas.
- **Cálculo:** Derivado do status de resolução de contrato e ausência de exceções bloqueantes.
- **Exposição:** `api_premium_subfatura_validada.mdm_confidence_score` e `mdm_status`.
- **Regra:** Apenas subfaturas com contrato resolvido e sem exceção bloqueante são publicadas.

---

## Fórmulas de Validação Offline

| Validação | Método | Origem |
|-----------|--------|--------|
| CNPJ DV | Algoritmo de dígito verificador (módulo 11) | Sprint 28 |
| CNES formato | 7 dígitos numéricos | Sprint 28 |
| Registro ANS formato | 6 dígitos numéricos | Sprint 28 |
| CPF DV (não implementado) | — | Backlog |
| MDM hash | `md5(normalizar_cnpj(...) \|\| '::' \|\| upper(trim(razao_social)))` | Sprint 29 |

---

## Status da Entrega

- **Sprint:** 32 — Endpoints Premium, Smoke Tests e Hard Gates
- **Natureza:** Técnica/arquitetural — sem cliente ativo em produção
- **Dependências externas:** Nenhuma (validação 100% offline)