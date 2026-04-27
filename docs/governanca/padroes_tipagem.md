# Padrões de Tipagem

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir os tipos PostgreSQL obrigatórios por domínio de dado na plataforma HealthIntel Suplementar. Desvios deste padrão são blocking para merge em main.

---

## Tipos Obrigatórios por Domínio

| Domínio | Tipo PostgreSQL | Observação |
|---------|----------------|------------|
| **CPF** | `varchar(11)` | Nunca `int`, `integer`, `bigint`, `numeric`, `decimal` |
| **CNPJ** | `varchar(14)` | Nunca `int`, `integer`, `bigint`, `numeric`, `decimal` |
| **CNES** | `varchar(7)` | Preservar zeros à esquerda |
| **Registro ANS** | `varchar(6)` | Preservar zeros à esquerda |
| **UF** | `char(2)` | Sempre maiúscula |
| **Código IBGE Município** | `varchar(7)` | Preservar zeros |
| **Competência** | `int` | Formato YYYYMM |
| **Valores monetários** | `numeric(18,2)` | Nunca `float`, `real`, `double precision` |
| **Quantidades** | `bigint` | |
| **Taxas / Percentuais técnicos** | `double precision` | |
| **Flags booleanas** | `boolean` | |
| **Data pura** | `date` | Sem componente de hora |
| **Timestamp técnico** | `timestamp(3)` | Com milissegundos |
| **JSON bruto** | `jsonb` | |
| **Hash / identificador interno** | `varchar(64)` ou `varchar(36)` | |
| **Descrições / textos** | `varchar(N)` ou `text` | `text` apenas quando tamanho imprevisível |

---

## Regras Obrigatórias

### Documentos de Identificação

1. **CNPJ nunca é tipo numérico.** `int`, `integer`, `bigint`, `numeric`, e `decimal` são terminantemente proibidos para CNPJ.
2. **CPF nunca é tipo numérico.** Mesma proibição.
3. **CNES sempre `varchar(7)`**, com zeros à esquerda preservados.
4. **Registro ANS sempre `varchar(6)`**, com zeros à esquerda preservados.
5. Código com zero à esquerda sempre é texto (`varchar`).

### Valores Monetários

6. **Dinheiro nunca é `float`, `real` ou `double precision`.**
7. Usar `numeric(18,2)` como padrão para valores monetários.
8. Em cenários com necessidade de maior precisão, usar `numeric(24,6)` com justificativa documentada.

### Taxas e Percentuais Técnicos

9. Taxas técnicas (ex: `taxa_aprovacao`, `sinistralidade_pct`) podem usar `double precision`.
10. Scores (0-100) podem usar `double precision`.

### Flags

11. Flags devem usar `boolean`. Evitar `int` 0/1 ou `varchar` S/N para flags.

### Datas e Timestamps

12. Data pura sem hora usa `date`.
13. Timestamp com hora e precisão de milissegundos usa `timestamp(3)`.
14. Evitar `timestamp without time zone` sem documentação explícita da zona.

### Colunas Publicadas

15. Coluna publicada **não muda tipo silenciosamente**.
16. Alteração de tipo em coluna publicada exige:
    - Deprecation da coluna antiga;
    - Nova coluna com nome distinto;
    - Período de coexistência;
    - Atualização de todos os downstreams antes da remoção da coluna antiga.

---

## Precisão, Escala e Tipos Numéricos

| Tipo | Uso |
|------|-----|
| `numeric(18,2)` | Valores monetários |
| `numeric(24,6)` | Valores monetários de alta precisão (justificativa obrigatória) |
| `bigint` | Quantidades, contagens |
| `integer` | Flags de categoria, anos, meses (não competência) |
| `double precision` | Scores, taxas, índices, percentuais técnicos |
| `smallint` | Códigos de categoria limitados |

---

## Arredondamento

1. Valores monetários: arredondamento bancário (half-even) na carga.
2. Scores: arredondamento para 2 casas decimais.
3. Percentuais: documentar se normalizados 0-1 ou 0-100.

---

## Justificativa para Exceções

Qualquer exceção a este padrão exige:

1. Documento de decisão (ADR) em `docs/arquitetura/`.
2. Aprovação do owner técnico.
3. Atualização deste documento com a exceção registrada.
4. Hard gate específico para a exceção.

---

## Exemplos de Tipagem Correta

```sql
-- ✅ Correto
cnpj                    varchar(14) not null,
cpf                     varchar(11),
cnes                    varchar(7) not null,
registro_ans            varchar(6) not null,
competencia             int not null,
uf                      char(2),
cd_municipio            varchar(7),
vl_total                numeric(18,2),
qt_beneficiarios        bigint,
score_total             double precision,
is_ativo                boolean,
dt_referencia           date,
_carregado_em           timestamp(3) not null,
_hash_arquivo           varchar(64) not null,
```

```sql
-- ❌ ERRADO — NUNCA FAZER
cnpj                    bigint,         -- ❌ perde zeros à esquerda
cpf                     integer,        -- ❌ idem
cnes                    integer,        -- ❌ idem
vl_total                float,          -- ❌ imprecisão monetária
score_total             real,           -- ❌ usar double precision
is_ativo                int,            -- ❌ usar boolean