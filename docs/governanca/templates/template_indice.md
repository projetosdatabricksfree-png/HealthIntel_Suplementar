# Template de Documentação de Índice

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template oficial para documentar índices da plataforma.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome do índice (`ix_`, `ux_`, `pk_`) | `ix_api_operadora_360_competencia` |
| `tabela` | Tabela associada | `api_ans.api_premium_operadora_360_validado` |
| `colunas` | Colunas indexadas | `competencia` |
| `tipo` | `btree`, `hash`, `gin`, `gist` | `btree` |
| `unico` | `sim` ou `nao` | `nao` |
| `justificativa` | Motivo do índice | "Filtro por competência nas queries da API" |
| `data_criacao` | Data | `2026-04-27` |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `removido` | `ativo` |

## Exemplo
| Campo | Valor |
|-------|-------|
| nome | `ix_api_premium_operadora_360_competencia` |
| tabela | `api_ans.api_premium_operadora_360_validado` |
| colunas | `competencia` |
| tipo | `btree` |
| unico | `nao` |
| justificativa | Filtro principal da API premium |
| data_criacao | 2026-04-15 |
| owner | Engenharia de Dados |
| status | ativo |

## Checklist
- [ ] Nome segue padrão `ix_`/`ux_`
- [ ] Justificativa documentada
- [ ] Não indexa staging sem justificativa explícita