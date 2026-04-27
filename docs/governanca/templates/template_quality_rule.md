# Template de Regra de Qualidade

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar regras de qualidade (validações, testes dbt, constraints).

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome da regra | `validar_cnpj_completo` |
| `tipo` | `macro`, `dbt_test`, `constraint` | `macro` |
| `tabela_alvo` | Tabela(s) onde se aplica | `stg_ans.stg_cadop` |
| `coluna_alvo` | Coluna(s) | `cnpj_normalizado` |
| `descricao` | O que valida | "CNPJ com 14 dígitos e dígito verificador válido" |
| `severidade` | `error` ou `warn` | `error` |
| `bloqueia_publicacao` | Impede produto principal? | `sim` |
| `deterministica` | `sim` ou `nao` | `sim` |
| `dependencia_externa` | Usa API externa? | `nao` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `deprecated` | `ativo` |

## Exemplo

| Campo | Valor |
|-------|-------|
| nome | `validar_cnpj_completo` |
| tipo | `macro` |
| tabela_alvo | `stg_cadop`, `stg_diops`, `stg_sib` |
| coluna_alvo | `cnpj_normalizado` |
| descricao | Valida dígito verificador do CNPJ deterministicamente |
| severidade | `error` |
| bloqueia_publicacao | `sim` |
| deterministica | `sim` |
| dependencia_externa | `nao` |
| owner | Engenharia de Dados |
| status | ativo |

## Checklist
- [ ] Severidade definida (error/warn)
- [ ] Sem dependência externa em runtime
- [ ] Determinística
- [ ] Owner definido