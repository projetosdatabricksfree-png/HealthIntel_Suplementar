# Evidência — TUSS Oficial vs Crosswalk Sintético

Data: 2026-05-11

## Objetivo

Verificar que `api_ans` e `consumo_ans` não usam crosswalk TUSS sintético como fonte comercial.

---

## api_ans.api_tuss_procedimento_vigente

Arquivo: `healthintel_dbt/models/api/api_tuss_procedimento_vigente.sql`

```sql
{{
    config(
        materialized='table',
        tags=['delta_ans_100', 'tuss_oficial'],
        post_hook=[
            "{{ criar_indice_api(this, 'codigo_tuss') }}",
            "{{ criar_indice_api(this, 'grupo') }}"
        ]
    )
}}

select
    codigo_tuss,
    descricao,
    versao_tuss,
    vigencia_inicio,
    vigencia_fim,
    is_tuss_vigente,
    grupo,
    subgrupo,
    _carregado_em
from {{ ref('stg_tuss_terminologia_oficial') }}
where is_tuss_vigente = true
```

**Fonte: `stg_tuss_terminologia_oficial`** — carregado a partir do `TUSS.zip` oficial da ANS via parser `ingestao_tuss_oficial`. Sem crosswalk sintético.

---

## xref_tiss_tuss_procedimento — localização e natureza

Arquivo: `healthintel_dbt/models/consumo_premium/xref_tiss_tuss_procedimento.sql`

```sql
{{
    config(
        materialized='table',
        schema='consumo_premium_ans',
        tags=['consumo_premium', 'tiss', 'tuss']
    )
}}

-- Crosswalk sintético TISS/TUSS — Sprint 31.
-- Modo CI não comercial: correspondência baseada em prefixo do código TUSS.
-- Substituir por tabela oficial de mapeamento TISS↔TUSS quando disponível.
```

**Schema**: `consumo_premium_ans` — isolado da camada pública `api_ans` e `consumo_ans`.

**Natureza**: explicitamente marcado como "CI não comercial". Não é exposto a clientes padrão.

---

## YAML de documentação

Arquivo: `healthintel_dbt/models/consumo_premium/_consumo_premium.yml`

```yaml
- name: xref_tiss_tuss_procedimento
  description: >
    Crosswalk TISS/TUSS de procedimentos. Modo CI sintético — não comercial.
    Mapeia códigos TISS para terminologia TUSS sintética. tiss_tuss_match_status
    indica correspondência (MATCHED/UNMATCHED/AMBIGUOUS/DEPRECATED).
```

---

## Conclusão

| Camada | Fonte TUSS | Crosswalk Sintético? |
|--------|-----------|----------------------|
| `api_ans.api_tuss_procedimento_vigente` | `stg_tuss_terminologia_oficial` (TUSS.zip ANS) | **NÃO** |
| `consumo_ans.consumo_tuss_procedimento_vigente` | `api_tuss_procedimento_vigente` | **NÃO** |
| `consumo_premium_ans.xref_tiss_tuss_procedimento` | `dim_tuss_procedimento` (sintético) | SIM — artefato CI, não exposto comercialmente |

**TUSS sintética/crosswalk não está em `api_ans` nem em `consumo_ans`.**
O artefato sintético está isolado em `consumo_premium_ans` e explicitamente documentado como não comercial.

Critério do sprint doc §8: `[x] TUSS sintética/crosswalk sintético não é usado em produção` — **confirmado**.
