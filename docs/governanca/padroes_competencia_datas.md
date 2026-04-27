# Padrões de Competência e Datas

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir o padrão obrigatório para representação de competências, trimestres e datas na plataforma HealthIntel Suplementar.

---

## Competência

### Regra Fundamental

**Toda competência mensal ANS é representada como `int` no formato YYYYMM.**

| Propriedade | Valor |
|-------------|-------|
| **Nome preferencial** | `competencia` |
| **Tipo** | `int` |
| **Formato** | YYYYMM |
| **Faixa mínima** | `200001` (janeiro/2000) |
| **Faixa máxima** | `(ano_atual * 100 + mes_atual) + 1` — competência atual + 1 mês |
| **Validação de mês** | `01` a `12` |
| **Exemplos válidos** | `202501`, `202412`, `202310` |
| **Exemplos inválidos** | `202513` (mês 13), `2501` (formato errado) |

### Aliases de Origem

Aliases encontrados em arquivos ANS devem ser normalizados na staging:

| Origem | Normalização |
|--------|-------------|
| `competencia` (já YYYYMM) | Manter |
| `ano` + `mes` separados | `ano * 100 + mes` |
| `data_competencia` no formato `YYYY-MM-DD` | Extrair `ano * 100 + mes` |
| `CD_COMPETENCIA` | `int` YYYYMM |

### Regras

1. Competência **não é** data de carga (`_carregado_em`).
2. Competência **não é** data de processamento.
3. Competência **não é** data de atualização.
4. Competência é o mês de referência dos dados ANS.
5. Competência nunca usa tipo `date`, `timestamp` ou `varchar`.
6. Nome da coluna é sempre `competencia`, nunca `cd_competencia`, `mes_referencia` ou `ano_mes` em tabelas publicadas. Aliases são aceitos apenas na staging.

---

## Trimestre

### Representação

Trimestres (ex: TISS) usam coluna própria, não misturada com competência mensal.

| Propriedade | Valor |
|-------------|-------|
| **Nome preferencial** | `trimestre` |
| **Tipo** | `varchar(6)` |
| **Formato** | `YYYYTN` onde N = 1, 2, 3, 4 |
| **Exemplos válidos** | `2025T1`, `2024T4` |

### Regras

1. Trimestre tem coluna própria, não se mistura com `competencia`.
2. Não usar `competencia` para trimestre TISS sem documentação explícita.
3. Converter trimestre para competências mensais quando necessário (ex: `2025T1` → `202501, 202502, 202503`).

---

## Datas Puras

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `date` |
| **Nomenclatura** | `dt_<descricao>` |
| **Exemplos** | `dt_referencia`, `dt_nascimento`, `dt_vigencia_inicio` |

### Regras

1. Data pura sem componente de hora usa `date`.
2. Não usar `timestamp` para data pura.

---

## Timestamps Técnicos

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `timestamp(3)` |
| **Precisão** | Milissegundos |
| **Nomenclatura** | `_carregado_em`, `dt_processamento` |
| **Exemplo** | `_carregado_em timestamp(3) not null default now()` |

### Regras

1. Timestamp técnico usa `timestamp(3)`.
2. Timestamps técnicos **não são expostos em API pública**.
3. `_carregado_em` é obrigatório em toda tabela materializada.
4. Evitar `timestamp without time zone` sem documentação explícita da timezone.

---

## Data de Processamento vs Competência

| Campo | Significado | Exemplo |
|-------|-------------|---------|
| `competencia` | Mês de referência dos dados | `202501` (janeiro/2025) |
| `_carregado_em` | Momento da ingestão no banco | `2025-03-15 14:30:00.000` |
| `dt_processamento` | Quando a transformação ocorreu | `2025-03-16 08:00:00.000` |
| `dt_atualizacao` | Última modificação do registro | `2025-04-01 10:00:00.000` |

---

## Regras de Validação de Competência

### Em dbt tests
```yaml
# Exemplo — generic test em schema.yml
- name: competencia
  tests:
    - not_null
    - accepted_range:
        min_value: 200001
        max_value: "{{ modules.datetime.datetime.now().strftime('%Y%m') | int + 1 }}"
    - custom:
        name: competencia_mes_valido
        description: "competencia deve ter mês entre 01 e 12"
        sql: |
          select * from {{ ref('minha_tabela') }}
          where mod(competencia, 100) not between 1 and 12
```

### Em check constraint
```sql
alter table nucleo_ans.mart_operadora_360
  add constraint ck_mart_operadora_360_competencia
  check (competencia between 200001 and 209912);
```

---

## Exceções

1. Tabelas de referência (ex: TUSS, ROL) podem não ter `competencia` — documentar explicitamente.
2. Tabelas de MDM podem usar `competencia` opcional — documentar quando `null` significa "registro mais recente".
3. Tabelas de tenant podem usar `competencia` com granularidade diferente — documentar no catálogo de tabelas.