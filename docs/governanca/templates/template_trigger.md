# Template de Documentação de Trigger

**Versão:** v3.8.0-gov | **Data:** 2026-04-27

## Objetivo
Template para documentar triggers PostgreSQL.

## Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome` | Nome do trigger | `trg_set_carregado_em` |
| `tabela` | Tabela associada | `bruto_ans.cadop_202501` |
| `evento` | `before insert`, `after update` etc. | `before insert` |
| `funcao` | Função executada | `fn_set_timestamp()` |
| `justificativa` | Por que existe | "Auditoria de timestamp de carga" |
| `owner` | Responsável | `Engenharia de Dados` |
| `status` | `ativo`, `removido` | `ativo` |

## Regras
- Apenas para auditoria ou regra operacional inevitável.
- Não usar para agregação ou transformação pesada.
- Não substitui dbt tests nem MDM.