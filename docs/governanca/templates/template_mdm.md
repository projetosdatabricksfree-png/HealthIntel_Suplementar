# Template de Documentação de MDM

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar entidades MDM (Master Data Management).

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `entidade` | Nome da entidade | `Operadora` |
| `master_table` | Tabela master | `mdm_ans.mdm_operadora_master` |
| `surrogate_key` | Surrogate key | `operadora_master_id` |
| `chave_natural` | Chave natural do negócio | `registro_ans` |
| `fonte_primaria` | Fonte principal | `CADOP` |
| `fontes_complementares` | Fontes adicionais | `DIOPS, SIB, TISS` |
| `survivorship_rule` | Regra de sobrevivência | "CADOP vence em atributos cadastrais" |
| `confidence_score` | Coluna de score | `mdm_confidence_score` |
| `schema` | `mdm_ans` ou `mdm_privado` | `mdm_ans` |
| `rls` | RLS ativo? | `nao` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo` | `ativo` |

## Exemplo

| Campo | Valor |
|-------|-------|
| entidade | Operadora |
| master_table | `mdm_ans.mdm_operadora_master` |
| surrogate_key | `operadora_master_id` |
| chave_natural | `registro_ans` |
| fonte_primaria | CADOP |
| fontes_complementares | DIOPS, SIB, TISS |
| survivorship_rule | CADOP vence atributos cadastrais; DIOPS vence financeiros |
| confidence_score | `mdm_confidence_score` |
| schema | `mdm_ans` |
| rls | `nao` |
| owner | Engenharia de Dados |
| status | ativo |

## Checklist
- [ ] Survivorship rule documentada
- [ ] Surrogate key definida
- [ ] Confidence score presente
- [ ] Schema público vs privado coerente com RLS